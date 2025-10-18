# Port Monitor Persistence Emulator
## MITRE ATT&CK T1547.010 - Boot or Logon Autostart Execution: Port Monitors

### Overview
This project demonstrates the Port Monitors persistence technique where a malicious DLL is loaded by the print spooler service during system boot, achieving persistence with SYSTEM privileges.

### Features
- Implements both registry-based and API-based persistence methods
- Comprehensive logging and error handling
- Complete cleanup functionality
- Verification of persistence establishment
- Production-grade code with security considerations

### Usage

#### 1. Build the Monitor DLL
```bash
cd monitor_dll
make
```

#### 2. Run Emulation (Administrator required)
```bash
python emulator.py
```

#### 3. Run Cleanup (Administrator required)
```bash
python cleanup.py
```

### Verification
After successful emulation:
1. Reboot the system
2. Check `C:\Windows\Temp\persistence_success.txt`
3. Check `C:\Windows\Temp\monitor_dll_log.txt`

### Technical Details
- **Persistence Mechanism**: DLL loaded by spoolsv.exe (Print Spooler)
- **Privilege Level**: SYSTEM
- **Activation**: System boot
- **Detection Difficulty**: Medium

### Security Considerations
This is a legitimate security research tool. Use only in controlled environments with proper authorization.

## 5. Compilation and Execution Instructions

### Building the DLL:
1. Install MinGW-w64 for Windows
2. Navigate to the `monitor_dll` directory
3. Run: `make`

### Running the Emulation:
```cmd
# Run as Administrator
python emulator.py
```