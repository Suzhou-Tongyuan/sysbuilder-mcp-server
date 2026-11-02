[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PythonPath,
    [string]$OutputPath,
    [string]$BuildRoot,
    [switch]$KeepBuildArtifacts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$buildSourceRoot = $PSScriptRoot
$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $buildSourceRoot ".."))
$projectRoot = $repositoryRoot
if (-not $OutputPath) {
    $OutputPath = Join-Path $projectRoot "sysbuilder-mcp-server-win64.exe"
}
if (-not $BuildRoot) {
    $BuildRoot = Join-Path ([IO.Path]::GetTempPath()) ("sysbuilder-mcp-onefile-" + [Guid]::NewGuid().ToString("N"))
}

$PythonPath = [IO.Path]::GetFullPath($PythonPath)
$OutputPath = [IO.Path]::GetFullPath($OutputPath)
$BuildRoot = [IO.Path]::GetFullPath($BuildRoot)
$temporaryRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())

if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "未找到用于构建的 Python: $PythonPath"
}

# 默认构建目录必须位于系统临时目录内，确保后续递归清理不会越过预期范围。
if (-not $KeepBuildArtifacts -and -not $BuildRoot.StartsWith($temporaryRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "自动清理仅允许用于系统临时目录：$BuildRoot"
}

$venvRoot = Join-Path $BuildRoot "venv"
$workRoot = Join-Path $BuildRoot "work"
$distRoot = Join-Path $BuildRoot "dist"
$specPath = Join-Path $buildSourceRoot "sysbuilder-mcp-server-onefile.spec"
$innerExe = Join-Path $distRoot "sysbuilder-mcp-server-win64.exe"
$wrapperSource = Join-Path $buildSourceRoot "sysbuilder_mcp_onefile_wrapper.cpp"
$resourceScript = Join-Path $BuildRoot "onefile_payload.rc"
$resourceFile = Join-Path $BuildRoot "onefile_payload.res"
$wrapperExe = Join-Path $BuildRoot "sysbuilder-mcp-server-win64.exe"
$wrapperObject = Join-Path $BuildRoot "sysbuilder_mcp_onefile_wrapper.obj"

try {
    New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null
    & $PythonPath -m venv --system-site-packages $venvRoot
    if ($LASTEXITCODE -ne 0) {
        throw "创建单文件构建环境失败。"
    }

    $venvPython = Join-Path $venvRoot "Scripts\python.exe"
    & $venvPython -m pip install --disable-pip-version-check "pyinstaller==6.21.0" "pypdf==6.10.0"
    if ($LASTEXITCODE -ne 0) {
        throw "安装 PyInstaller 6.21.0 或 pypdf 6.10.0 失败。"
    }

    $manualIndex = Join-Path $projectRoot "resources\manuals\Sysbuilder_User_Manual.pages.json"
    if (-not (Test-Path -LiteralPath $manualIndex -PathType Leaf)) {
        throw "缺少已同步的 Sysbuilder 用户手册索引：$manualIndex"
    }

    & $venvPython -m PyInstaller `
        --noconfirm `
        --clean `
        --workpath $workRoot `
        --distpath $distRoot `
        $specPath
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $innerExe -PathType Leaf)) {
        throw "PyInstaller 未生成预期的内层单文件 EXE。"
    }

    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
        throw "未找到 Visual Studio Installer 的 vswhere.exe。"
    }
    $visualStudioRoot = (& $vswhere -latest -products * `
        -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
        -property installationPath | Select-Object -First 1)
    if (-not $visualStudioRoot) {
        throw "未找到可用的 Visual C++ x64 构建工具。"
    }
    $vcvars64 = Join-Path $visualStudioRoot "VC\Auxiliary\Build\vcvars64.bat"
    if (-not (Test-Path -LiteralPath $vcvars64 -PathType Leaf)) {
        throw "未找到 vcvars64.bat: $vcvars64"
    }

    # RC 文件仅在临时目录生成，将已验证的内层 EXE 作为 RCDATA 嵌入最终原生外壳。
    $resourcePath = $innerExe.Replace("\", "/")
    [IO.File]::WriteAllText(
        $resourceScript,
        "101 RCDATA `"$resourcePath`"`r`n",
        [Text.Encoding]::ASCII)

    $compileCommand = 'call "{0}" >nul && rc.exe /nologo /fo "{1}" "{2}" && cl.exe /nologo /utf-8 /std:c++17 /EHsc /O2 /MT /DUNICODE /D_UNICODE /Fo:"{5}" "{3}" "{1}" /Fe:"{4}" /link /SUBSYSTEM:CONSOLE' -f `
        $vcvars64, $resourceFile, $resourceScript, $wrapperSource, $wrapperExe, $wrapperObject
    & $env:COMSPEC /d /s /c $compileCommand
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $wrapperExe -PathType Leaf)) {
        throw "原生单文件外壳构建失败。"
    }

    $outputDirectory = Split-Path -Parent $OutputPath
    New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
    Copy-Item -LiteralPath $wrapperExe -Destination $OutputPath -Force
    $outputItem = Get-Item -LiteralPath $OutputPath
    $outputHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $OutputPath).Hash.ToLowerInvariant()
    Write-Host "单文件 MCP 已生成：$($outputItem.FullName)"
    Write-Host "大小：$($outputItem.Length) 字节"
    Write-Host "SHA-256：$outputHash"
}
finally {
    if (-not $KeepBuildArtifacts -and (Test-Path -LiteralPath $BuildRoot)) {
        $resolvedBuildRoot = [IO.Path]::GetFullPath($BuildRoot)
        if (-not $resolvedBuildRoot.StartsWith($temporaryRoot, [StringComparison]::OrdinalIgnoreCase)) {
            throw "拒绝清理临时目录之外的路径：$resolvedBuildRoot"
        }
        Remove-Item -LiteralPath $resolvedBuildRoot -Recurse -Force
    }
}
