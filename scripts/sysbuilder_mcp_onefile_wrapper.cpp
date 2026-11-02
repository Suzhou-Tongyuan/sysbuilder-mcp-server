#include <windows.h>

#include <cstdio>
#include <string>
#include <vector>

namespace {

constexpr int kPayloadResourceId = 101;

// 统一管理 Win32 句柄生命周期，适用于进程、管道和临时文件。
class UniqueHandle {
public:
    UniqueHandle() noexcept = default;
    explicit UniqueHandle(HANDLE handle) noexcept : handle_(handle) {}
    ~UniqueHandle() { Reset(); }

    UniqueHandle(const UniqueHandle&) = delete;
    UniqueHandle& operator=(const UniqueHandle&) = delete;

    UniqueHandle(UniqueHandle&& other) noexcept : handle_(other.Release()) {}
    UniqueHandle& operator=(UniqueHandle&& other) noexcept {
        if (this != &other) {
            Reset(other.Release());
        }
        return *this;
    }

    HANDLE Get() const noexcept { return handle_; }
    bool IsValid() const noexcept { return handle_ != nullptr && handle_ != INVALID_HANDLE_VALUE; }

    HANDLE Release() noexcept {
        const HANDLE value = handle_;
        handle_ = nullptr;
        return value;
    }

    void Reset(HANDLE handle = nullptr) noexcept {
        if (IsValid()) {
            CloseHandle(handle_);
        }
        handle_ = handle;
    }

private:
    HANDLE handle_ = nullptr;
};

// 返回当前最终发行 EXE 的目录，用于发现标准 Tools 部署位置。
std::wstring GetExecutableDirectory() {
    std::vector<wchar_t> buffer(MAX_PATH);
    while (true) {
        const DWORD length = GetModuleFileNameW(nullptr, buffer.data(), static_cast<DWORD>(buffer.size()));
        if (length == 0) {
            return {};
        }
        if (length < buffer.size() - 1) {
            std::wstring path(buffer.data(), length);
            const size_t separator = path.find_last_of(L"\\/");
            return separator == std::wstring::npos ? std::wstring{} : path.substr(0, separator);
        }
        buffer.resize(buffer.size() * 2);
    }
}

// 返回路径父目录，不访问文件系统，适用于组装标准安装布局。
std::wstring ParentPath(const std::wstring& path) {
    const size_t separator = path.find_last_of(L"\\/");
    if (separator == std::wstring::npos) {
        return {};
    }
    return path.substr(0, separator);
}

// 检查普通文件是否存在，避免把目录误当作 Sysbuilder 主程序。
bool IsRegularFile(const std::wstring& path) {
    const DWORD attributes = GetFileAttributesW(path.c_str());
    return attributes != INVALID_FILE_ATTRIBUTES && (attributes & FILE_ATTRIBUTE_DIRECTORY) == 0;
}

// 按 Windows CreateProcess 命令行规则引用参数，兼容空格、引号和尾部反斜杠。
std::wstring QuoteArgument(const std::wstring& argument) {
    if (argument.empty()) {
        return L"\"\"";
    }
    if (argument.find_first_of(L" \t\n\v\"") == std::wstring::npos) {
        return argument;
    }

    std::wstring quoted = L"\"";
    size_t backslashes = 0;
    for (const wchar_t character : argument) {
        if (character == L'\\') {
            ++backslashes;
            continue;
        }
        if (character == L'\"') {
            quoted.append(backslashes * 2 + 1, L'\\');
            quoted.push_back(L'\"');
            backslashes = 0;
            continue;
        }
        quoted.append(backslashes, L'\\');
        backslashes = 0;
        quoted.push_back(character);
    }
    quoted.append(backslashes * 2, L'\\');
    quoted.push_back(L'\"');
    return quoted;
}

// 把启动错误写入 stderr，确保 stdout 始终只承载 MCP JSON-RPC。
void PrintLaunchError(const wchar_t* message, const std::wstring& detail = {}) {
    if (detail.empty()) {
        std::fwprintf(stderr, L"sysbuilder-mcp-server: %ls\n", message);
    } else {
        std::fwprintf(stderr, L"sysbuilder-mcp-server: %ls: %ls\n", message, detail.c_str());
    }
}

// 完整写入字节缓冲区，处理管道或文件的短写场景。
bool WriteAll(HANDLE handle, const void* data, DWORD size) {
    const auto* bytes = static_cast<const unsigned char*>(data);
    DWORD offset = 0;
    while (offset < size) {
        DWORD written = 0;
        if (!WriteFile(handle, bytes + offset, size - offset, &written, nullptr) || written == 0) {
            return false;
        }
        offset += written;
    }
    return true;
}

// 创建本次运行专用临时目录，避免多个 MCP 实例相互覆盖内层 EXE。
std::wstring CreateTemporaryDirectory() {
    std::vector<wchar_t> tempPath(MAX_PATH);
    const DWORD length = GetTempPathW(static_cast<DWORD>(tempPath.size()), tempPath.data());
    if (length == 0 || length >= tempPath.size()) {
        return {};
    }

    wchar_t uniquePath[MAX_PATH] = {};
    if (GetTempFileNameW(tempPath.data(), L"SBM", 0, uniquePath) == 0) {
        return {};
    }
    DeleteFileW(uniquePath);
    if (!CreateDirectoryW(uniquePath, nullptr)) {
        return {};
    }
    return uniquePath;
}

// 将资源中的完整 PyInstaller 单文件写入临时目录，供子进程启动。
bool ExtractEmbeddedPayload(const std::wstring& payloadPath) {
    const HMODULE module = GetModuleHandleW(nullptr);
    const HRSRC resource = FindResourceW(module, MAKEINTRESOURCEW(kPayloadResourceId), RT_RCDATA);
    if (resource == nullptr) {
        return false;
    }
    const HGLOBAL loaded = LoadResource(module, resource);
    const DWORD size = SizeofResource(module, resource);
    const void* data = loaded == nullptr ? nullptr : LockResource(loaded);
    if (data == nullptr || size == 0) {
        return false;
    }

    UniqueHandle file(CreateFileW(
        payloadPath.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS,
        FILE_ATTRIBUTE_TEMPORARY, nullptr));
    return file.IsValid() && WriteAll(file.Get(), data, size);
}

// 设置标准 Tools 部署所需路径；显式命令行参数仍由内层 MCP 服务覆盖。
void ConfigureRuntimeEnvironment(const std::wstring& executableDirectory) {
    SetEnvironmentVariableW(L"PYTHONUTF8", L"1");
    SetEnvironmentVariableW(L"PYTHONUNBUFFERED", L"1");

    const std::wstring toolsDirectory = ParentPath(executableDirectory);
    const std::wstring runtimeRoot = ParentPath(toolsDirectory);
    if (runtimeRoot.empty()) {
        return;
    }

    const std::vector<std::wstring> processCandidates = {
        runtimeRoot + L"\\Release\\Sysbuilder.exe",
        runtimeRoot + L"\\Bin\\Sysbuilder.exe",
        runtimeRoot + L"\\Sysbuilder.exe",
    };
    for (const auto& candidate : processCandidates) {
        if (!IsRegularFile(candidate)) {
            continue;
        }
        if (GetEnvironmentVariableW(L"SYSBUILDER_INSTALL_DIR", nullptr, 0) == 0) {
            SetEnvironmentVariableW(L"SYSBUILDER_INSTALL_DIR", runtimeRoot.c_str());
        }
        if (GetEnvironmentVariableW(L"SYSBUILDER_PROCESS_PATH", nullptr, 0) == 0) {
            SetEnvironmentVariableW(L"SYSBUILDER_PROCESS_PATH", candidate.c_str());
        }
        break;
    }
}

// 只识别安全软件注入的已知 REX 诊断行，不吞掉其他原生输出。
bool IsRexAnomaly(const std::string& line) {
    return line.rfind("[0x", 0) == 0 &&
           line.find("] ANOMALY:") != std::string::npos &&
           line.find("REX") != std::string::npos;
}

// 按换行边界代理子进程 stdout，过滤噪声后原样转发 MCP JSON-RPC。
bool PumpFilteredStdout(HANDLE childStdout, HANDLE parentStdout) {
    std::string pending;
    std::vector<char> chunk(8192);
    while (true) {
        DWORD bytesRead = 0;
        if (!ReadFile(childStdout, chunk.data(), static_cast<DWORD>(chunk.size()), &bytesRead, nullptr)) {
            if (GetLastError() == ERROR_BROKEN_PIPE) {
                break;
            }
            return false;
        }
        if (bytesRead == 0) {
            break;
        }
        pending.append(chunk.data(), bytesRead);

        size_t newline = std::string::npos;
        while ((newline = pending.find('\n')) != std::string::npos) {
            std::string line = pending.substr(0, newline + 1);
            pending.erase(0, newline + 1);
            std::string comparable = line;
            while (!comparable.empty() && (comparable.back() == '\r' || comparable.back() == '\n')) {
                comparable.pop_back();
            }
            if (!IsRexAnomaly(comparable) &&
                !WriteAll(parentStdout, line.data(), static_cast<DWORD>(line.size()))) {
                return false;
            }
        }
    }

    if (!pending.empty() && !IsRexAnomaly(pending)) {
        return WriteAll(parentStdout, pending.data(), static_cast<DWORD>(pending.size()));
    }
    return true;
}

}  // namespace

// 最终单文件入口：解出内层服务、代理 stdio、等待退出并清理临时文件。
int wmain(int argc, wchar_t* argv[]) {
    const std::wstring executableDirectory = GetExecutableDirectory();
    if (executableDirectory.empty()) {
        PrintLaunchError(L"无法确定启动器目录");
        return 2;
    }
    ConfigureRuntimeEnvironment(executableDirectory);

    const std::wstring temporaryDirectory = CreateTemporaryDirectory();
    if (temporaryDirectory.empty()) {
        PrintLaunchError(L"无法创建临时目录");
        return 2;
    }
    const std::wstring payloadPath = temporaryDirectory + L"\\sysbuilder-mcp-server-inner.exe";
    if (!ExtractEmbeddedPayload(payloadPath)) {
        PrintLaunchError(L"无法释放内置 MCP 服务", payloadPath);
        RemoveDirectoryW(temporaryDirectory.c_str());
        return 2;
    }

    SECURITY_ATTRIBUTES security = {};
    security.nLength = sizeof(security);
    security.bInheritHandle = TRUE;
    UniqueHandle childStdoutRead;
    UniqueHandle childStdoutWrite;
    HANDLE readHandle = nullptr;
    HANDLE writeHandle = nullptr;
    if (!CreatePipe(&readHandle, &writeHandle, &security, 0)) {
        PrintLaunchError(L"无法创建 stdout 代理管道");
        DeleteFileW(payloadPath.c_str());
        RemoveDirectoryW(temporaryDirectory.c_str());
        return 2;
    }
    childStdoutRead.Reset(readHandle);
    childStdoutWrite.Reset(writeHandle);
    SetHandleInformation(childStdoutRead.Get(), HANDLE_FLAG_INHERIT, 0);

    std::wstring commandLine = QuoteArgument(payloadPath);
    for (int index = 1; index < argc; ++index) {
        commandLine.push_back(L' ');
        commandLine += QuoteArgument(argv[index]);
    }
    std::vector<wchar_t> mutableCommand(commandLine.begin(), commandLine.end());
    mutableCommand.push_back(L'\0');

    STARTUPINFOW startupInfo = {};
    startupInfo.cb = sizeof(startupInfo);
    startupInfo.dwFlags = STARTF_USESTDHANDLES;
    startupInfo.hStdInput = GetStdHandle(STD_INPUT_HANDLE);
    startupInfo.hStdOutput = childStdoutWrite.Get();
    startupInfo.hStdError = GetStdHandle(STD_ERROR_HANDLE);

    PROCESS_INFORMATION processInfo = {};
    const BOOL created = CreateProcessW(
        payloadPath.c_str(), mutableCommand.data(), nullptr, nullptr, TRUE,
        CREATE_NO_WINDOW, nullptr, temporaryDirectory.c_str(), &startupInfo, &processInfo);
    if (!created) {
        PrintLaunchError(L"无法启动内置 MCP 服务", payloadPath);
        DeleteFileW(payloadPath.c_str());
        RemoveDirectoryW(temporaryDirectory.c_str());
        return 2;
    }

    UniqueHandle process(processInfo.hProcess);
    UniqueHandle thread(processInfo.hThread);
    childStdoutWrite.Reset();
    const bool pumpSucceeded = PumpFilteredStdout(
        childStdoutRead.Get(), GetStdHandle(STD_OUTPUT_HANDLE));
    childStdoutRead.Reset();

    WaitForSingleObject(process.Get(), INFINITE);
    DWORD exitCode = 1;
    GetExitCodeProcess(process.Get(), &exitCode);
    process.Reset();

    if (!DeleteFileW(payloadPath.c_str())) {
        MoveFileExW(payloadPath.c_str(), nullptr, MOVEFILE_DELAY_UNTIL_REBOOT);
    }
    RemoveDirectoryW(temporaryDirectory.c_str());

    if (!pumpSucceeded) {
        PrintLaunchError(L"转发 MCP stdout 失败");
        return 3;
    }
    return static_cast<int>(exitCode);
}
