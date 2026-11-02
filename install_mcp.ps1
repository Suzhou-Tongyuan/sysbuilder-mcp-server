param(
    [string]$SysbuilderPath = "",
    [string]$PythonPath = "",
    [string]$ServerName = "sysbuilder_mcp_server"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message)
    Write-Host "[sysbuilder_mcp_server] $Message"
}

function Write-Utf8File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Backup-FileIfExists {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $backupPath = "$Path.bak.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Copy-Item -LiteralPath $Path -Destination $backupPath -Force
    return $backupPath
}

function Normalize-ExistingText {
    param([string]$Content)

    if ([string]::IsNullOrEmpty($Content)) {
        return ""
    }

    return $Content.Replace("`r`n", "`n").Replace("`r", "`n")
}

function Set-ManagedTextBlock {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$StartMarker,
        [Parameter(Mandatory = $true)][string]$EndMarker,
        [Parameter(Mandatory = $true)][string]$Block
    )

    $existing = ""
    if (Test-Path -LiteralPath $Path) {
        $existing = Normalize-ExistingText -Content ([System.IO.File]::ReadAllText($Path))
    }

    $pattern = [regex]::Escape($StartMarker) + ".*?" + [regex]::Escape($EndMarker)
    $replacement = $Block.TrimEnd() + "`n"
    if ([regex]::IsMatch($existing, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)) {
        $updated = [regex]::Replace(
            $existing,
            $pattern,
            [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $replacement },
            [System.Text.RegularExpressions.RegexOptions]::Singleline
        )
    }
    else {
        if ($existing -and -not $existing.EndsWith("`n")) {
            $existing += "`n"
        }
        if ($existing) {
            $existing += "`n"
        }
        $updated = $existing + $replacement
    }

    Write-Utf8File -Path $Path -Content $updated
}

function Escape-TomlSingleQuoted {
    param([string]$Value)

    return ($Value -replace "'", "''")
}

function ConvertTo-TomlSingleQuotedArray {
    param([string[]]$Values)

    $items = foreach ($value in $Values) {
        "'" + (Escape-TomlSingleQuoted -Value $value) + "'"
    }
    return "[" + ($items -join ", ") + "]"
}

function ConvertTo-Hashtable {
    param([AllowNull()]$InputObject)

    if ($null -eq $InputObject) {
        return $null
    }

    if ($InputObject -is [System.Collections.IDictionary]) {
        $table = @{}
        foreach ($key in $InputObject.Keys) {
            $table[$key] = ConvertTo-Hashtable -InputObject $InputObject[$key]
        }
        return $table
    }

    if (($InputObject -is [System.Collections.IEnumerable]) -and -not ($InputObject -is [string])) {
        $list = @()
        foreach ($item in $InputObject) {
            $list += ,(ConvertTo-Hashtable -InputObject $item)
        }
        return $list
    }

    if ($InputObject -is [psobject]) {
        $properties = $InputObject.PSObject.Properties
        if (@($properties).Count -gt 0) {
            $table = @{}
            foreach ($property in $properties) {
                $table[$property.Name] = ConvertTo-Hashtable -InputObject $property.Value
            }
            return $table
        }
    }

    return $InputObject
}

function Remove-JsonTrailingCommas {
    param([Parameter(Mandatory = $true)][string]$Content)

    if ([string]::IsNullOrEmpty($Content)) {
        return $Content
    }

    $builder = New-Object System.Text.StringBuilder
    $inString = $false
    $isEscaped = $false

    for ($i = 0; $i -lt $Content.Length; $i++) {
        $char = $Content[$i]

        if ($inString) {
            [void]$builder.Append($char)

            if ($isEscaped) {
                $isEscaped = $false
            }
            elseif ($char -eq '\') {
                $isEscaped = $true
            }
            elseif ($char -eq '"') {
                $inString = $false
            }

            continue
        }

        if ($char -eq '"') {
            $inString = $true
            [void]$builder.Append($char)
            continue
        }

        if ($char -eq ',') {
            $nextIndex = $i + 1
            while ($nextIndex -lt $Content.Length -and [char]::IsWhiteSpace($Content[$nextIndex])) {
                $nextIndex++
            }

            if ($nextIndex -lt $Content.Length -and ($Content[$nextIndex] -eq '}' -or $Content[$nextIndex] -eq ']')) {
                continue
            }
        }

        [void]$builder.Append($char)
    }

    return $builder.ToString()
}

function Get-JsonObject {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return @{}
    }

    $raw = [System.IO.File]::ReadAllText($Path)
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return @{}
    }

    if ($raw[0] -eq [char]0xFEFF) {
        $raw = $raw.Substring(1)
    }

    try {
        $parsed = $raw | ConvertFrom-Json
    }
    catch {
        $sanitized = Remove-JsonTrailingCommas -Content $raw
        try {
            $parsed = $sanitized | ConvertFrom-Json
        }
        catch {
            throw "无法解析 JSON 配置文件: $Path。请检查文件格式是否为合法 JSON（Windows PowerShell 5.1 不接受尾随逗号等扩展语法）。原始错误: $($_.Exception.Message)"
        }
    }

    return ConvertTo-Hashtable -InputObject $parsed
}

function Ensure-HashtableValue {
    param([AllowNull()]$InputObject)

    if ($null -eq $InputObject) {
        return @{}
    }

    if ($InputObject -is [System.Collections.IDictionary]) {
        return $InputObject
    }

    $converted = ConvertTo-Hashtable -InputObject $InputObject
    if ($converted -is [System.Collections.IDictionary]) {
        return $converted
    }

    return @{}
}

function Write-JsonObject {
    param(
        [string]$Path,
        [Parameter(Mandatory = $true)]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 100
    Write-Utf8File -Path $Path -Content ($json + "`n")
}

function Test-UsablePythonPath {
    param([string]$CandidatePath)

    if ([string]::IsNullOrWhiteSpace($CandidatePath)) {
        return $false
    }

    if (-not (Test-Path -LiteralPath $CandidatePath -PathType Leaf)) {
        return $false
    }

    if ($CandidatePath -match '\\WindowsApps\\') {
        return $false
    }

    return $true
}

function Resolve-PythonPath {
    param(
        [string]$PreferredPath,
        [string]$RepoRoot,
        [string]$InstallDir,
        [string]$ProcessPath,
        [bool]$InputIsProcessPath = $false
    )

    $candidateList = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($PreferredPath)) {
        $candidateList.Add([System.IO.Path]::GetFullPath($PreferredPath.Trim()))
    }

    $candidateList.Add((Join-Path $InstallDir "external\Python311\python.exe"))
    if ($InputIsProcessPath) {
        $processDir = Split-Path -Parent $ProcessPath
        $processParentDir = Split-Path -Parent $processDir
        if (-not [string]::IsNullOrWhiteSpace($processParentDir)) {
            $candidateList.Add((Join-Path $processParentDir "external\Python311\python.exe"))
        }
    }
    else {
        $candidateList.Add((Join-Path (Split-Path -Parent $ProcessPath) "external\Python311\python.exe"))
    }
    $candidateList.Add((Join-Path $RepoRoot ".venv\Scripts\python.exe"))

    foreach ($pattern in @(
        "C:\Python*\python.exe",
        "D:\Python*\python.exe",
        "E:\Python*\python.exe",
        "$HOME\AppData\Local\Programs\Python\Python*\python.exe"
    )) {
        $matched = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue |
            Where-Object { $_ -and -not $_.PSIsContainer } |
            Sort-Object FullName -Descending
        foreach ($item in $matched) {
            $candidateList.Add($item.FullName)
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $candidateList.Add($pythonCommand.Source)
    }

    foreach ($candidate in $candidateList) {
        if (Test-UsablePythonPath -CandidatePath $candidate) {
            return [System.IO.Path]::GetFullPath($candidate)
        }
    }

    throw "未找到可用的 Python。请确认 Sysbuilder 安装目录下包含 external\Python311\python.exe，或执行 install_mcp.ps1 时通过 -PythonPath 显式指定 python.exe。"
}

function Resolve-SysbuilderPaths {
    param([string]$RawInput)

    if ([string]::IsNullOrWhiteSpace($RawInput)) {
        throw "未提供 Sysbuilder 安装目录或 Sysbuilder.exe 路径。"
    }

    $candidate = [System.IO.Path]::GetFullPath($RawInput.Trim())
    if (-not (Test-Path -LiteralPath $candidate)) {
        throw "路径不存在: $candidate"
    }

    if ((Test-Path -LiteralPath $candidate -PathType Leaf) -and $candidate.ToLowerInvariant().EndsWith("sysbuilder.exe")) {
        $processPath = $candidate
        $installDir = Split-Path -Parent $candidate
        $inputIsProcessPath = $true
    }
    elseif (Test-Path -LiteralPath $candidate -PathType Container) {
        $binProcess = Join-Path $candidate "Bin\Sysbuilder.exe"
        $directProcess = Join-Path $candidate "Sysbuilder.exe"
        if (Test-Path -LiteralPath $binProcess -PathType Leaf) {
            $processPath = $binProcess
            $installDir = $candidate
            $inputIsProcessPath = $false
        }
        elseif (Test-Path -LiteralPath $directProcess -PathType Leaf) {
            $processPath = $directProcess
            $installDir = $candidate
            $inputIsProcessPath = $false
        }
        else {
            throw "目录中未找到 Sysbuilder.exe: $candidate"
        }
    }
    else {
        throw "无效的 Sysbuilder 路径: $candidate"
    }

    return @{
        InstallDir = [System.IO.Path]::GetFullPath($installDir)
        ProcessPath = [System.IO.Path]::GetFullPath($processPath)
        InputIsProcessPath = $inputIsProcessPath
    }
}

$repoRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$entryScript = Join-Path $repoRoot "main.py"
$resourcesDir = Join-Path $repoRoot "resources"
$workspaceDir = $repoRoot
$outputDir = Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)) "Sysbuilder\SysMLAIOutput"

if (-not (Test-Path -LiteralPath $entryScript -PathType Leaf)) {
    throw "未找到入口脚本: $entryScript"
}

if ([string]::IsNullOrWhiteSpace($SysbuilderPath)) {
    $SysbuilderPath = Read-Host "请输入 Sysbuilder 安装目录或 Sysbuilder.exe 路径"
}

$resolved = Resolve-SysbuilderPaths -RawInput $SysbuilderPath
$resolved["PythonPath"] = Resolve-PythonPath `
    -PreferredPath $PythonPath `
    -RepoRoot $repoRoot `
    -InstallDir $resolved.InstallDir `
    -ProcessPath $resolved.ProcessPath `
    -InputIsProcessPath $resolved.InputIsProcessPath

$command = $resolved.PythonPath
$args = @(
    $entryScript,
    "--sysbuilder-install-dir", $resolved.InstallDir,
    "--sysbuilder-process-path", $resolved.ProcessPath,
    "--resources-dir", $resourcesDir,
    "--workspace-dir", $workspaceDir,
    "--output-dir", $outputDir
)
$cwd = $repoRoot

$managedStart = "# >>> sysbuilder_mcp_server managed block >>>"
$managedEnd = "# <<< sysbuilder_mcp_server managed block <<<"
$tomlBlock = @"
$managedStart
[mcp_servers.$ServerName]
command = '$(Escape-TomlSingleQuoted -Value $command)'
args = $(ConvertTo-TomlSingleQuotedArray -Values $args)
cwd = '$(Escape-TomlSingleQuoted -Value $cwd)'
$managedEnd
"@

$codexConfigPath = Join-Path $HOME ".codex\config.toml"
$claudeConfigPath = Join-Path $HOME ".claude.json"
$openCodeConfigPath = Join-Path $HOME ".config\opencode\opencode.json"
$genericConfigPath = Join-Path $repoRoot "mcp_server_config.json"

$backups = @()
foreach ($path in @($codexConfigPath, $claudeConfigPath, $openCodeConfigPath)) {
    $backup = Backup-FileIfExists -Path $path
    if ($backup) {
        $backups += $backup
    }
}

Set-ManagedTextBlock -Path $codexConfigPath -StartMarker $managedStart -EndMarker $managedEnd -Block $tomlBlock

$claudeConfig = Get-JsonObject -Path $claudeConfigPath
if (-not $claudeConfig.ContainsKey("mcpServers")) {
    $claudeConfig["mcpServers"] = @{}
}
$claudeConfig["mcpServers"] = Ensure-HashtableValue -InputObject $claudeConfig["mcpServers"]
$claudeConfig["mcpServers"][$ServerName] = @{
    command = $command
    args = $args
    cwd = $cwd
}
Write-JsonObject -Path $claudeConfigPath -Data $claudeConfig

$openCodeConfig = Get-JsonObject -Path $openCodeConfigPath
if (-not $openCodeConfig.ContainsKey("mcp")) {
    $openCodeConfig["mcp"] = @{}
}
$openCodeConfig["mcp"] = Ensure-HashtableValue -InputObject $openCodeConfig["mcp"]
$openCodeConfig["mcp"][$ServerName] = @{
    type = "local"
    command = @($command) + $args
}
Write-JsonObject -Path $openCodeConfigPath -Data $openCodeConfig

$genericConfig = @{
    mcpServers = @{
        $ServerName = @{
            command = $command
            args = $args
            cwd = $cwd
        }
    }
}
Write-JsonObject -Path $genericConfigPath -Data $genericConfig

Write-Status "安装完成。"
Write-Status "Sysbuilder 安装目录: $($resolved.InstallDir)"
Write-Status "Sysbuilder 可执行文件: $($resolved.ProcessPath)"
Write-Status "Python: $($resolved.PythonPath)"
Write-Status "中间数据目录: $outputDir"
Write-Status "Codex 配置: $codexConfigPath"
Write-Status "Claude 配置: $claudeConfigPath"
Write-Status "OpenCode 配置: $openCodeConfigPath"
Write-Status "通用配置示例: $genericConfigPath"
if ($backups.Count -gt 0) {
    Write-Status "已创建备份:"
    foreach ($backupPath in $backups) {
        Write-Host "  $backupPath"
    }
}
