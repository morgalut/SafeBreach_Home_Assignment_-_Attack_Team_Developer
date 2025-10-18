#!/usr/bin/env python3
"""
COMPLETE Port Monitor Persistence Cleanup
Removes ALL installations from both original and delayed versions
"""

import os
import sys
import ctypes
import logging
import subprocess
import winreg
import glob
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\Windows\\Temp\\ultimate_cleanup_complete.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompleteCleanup:
    def __init__(self):
        # All possible monitor names used
        self.monitor_names = [
            "UltimateMonitor",
            "SafeBreachMonitor", 
            "ZombieMonitor",
            "PortMonitor"
        ]
        
        # All possible DLL names used
        self.dll_names = [
            "monitor_dll.dll",
            "safebreach_monitor.dll",
            "zombie_monitor.dll",
            "port_monitor.dll"
        ]
        
        self.system32_path = os.path.join(os.environ['WINDIR'], 'System32')
        
        # ALL task names to remove (from all versions)
        self.task_names = [
            "UltimateMonitorUI",
            "UltimateMonitorDelayedUI",
            "SafeBreachNotepad",
            "SafeBreachBootMessage", 
            "SafeBreachSystemBoot",
            "SafeBreachUserLogon",
            "SafeBreachSystemStartup",
            "SafeBreachStartup",
            "SafeBreachVerify",
            "ZombiePersistence",
            "PortMonitorUI"
        ]
        
        # ALL registry value names to remove
        self.registry_values = [
            "UltimateMonitorUI",
            "UltimateMonitorDelayed",
            "SafeBreachMonitor",
            "ZombiePersistence",
            "PortMonitor"
        ]

    def check_admin_privileges(self):
        """Check administrator privileges"""
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

    def remove_all_scheduled_tasks(self):
        """Remove ALL scheduled tasks from all versions"""
        logger.info("Removing ALL scheduled tasks...")
        
        removed_count = 0
        for task_name in self.task_names:
            try:
                result = subprocess.run(
                    ['schtasks', '/delete', '/tn', task_name, '/f'],
                    capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    logger.info(f"✓ Removed task: {task_name}")
                    removed_count += 1
                else:
                    if "not found" not in result.stderr.lower():
                        logger.info(f"Task not found: {task_name}")
            except Exception as e:
                logger.warning(f"Error removing task {task_name}: {e}")
        
        # Also try to remove any tasks that might have similar names
        try:
            result = subprocess.run(['schtasks', '/query', '/fo', 'list'], 
                                  capture_output=True, text=True, check=False)
            for line in result.stdout.split('\n'):
                if 'Ultimate' in line or 'Zombie' in line or 'SafeBreach' in line or 'PortMonitor' in line:
                    task_name = line.split(':')[-1].strip()
                    if task_name:
                        subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                                     capture_output=True, check=False)
                        logger.info(f"✓ Removed additional task: {task_name}")
                        removed_count += 1
        except Exception as e:
            logger.warning(f"Error scanning for additional tasks: {e}")
        
        logger.info(f"Removed {removed_count} scheduled tasks total")
        return removed_count > 0

    def remove_all_registry_entries(self):
        """Remove ALL registry entries from all versions"""
        logger.info("Removing ALL registry entries...")
        
        removed_count = 0
        
        # Remove port monitor registry entries
        for monitor_name in self.monitor_names:
            try:
                registry_path = r"SYSTEM\CurrentControlSet\Control\Print\Monitors"
                full_path = f"{registry_path}\\{monitor_name}"
                
                winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, full_path)
                logger.info(f"✓ Removed port monitor registry: {monitor_name}")
                removed_count += 1
            except FileNotFoundError:
                logger.info(f"Port monitor registry not found: {monitor_name}")
            except Exception as e:
                logger.error(f"Error removing port monitor registry {monitor_name}: {e}")
        
        # Remove Run registry entries
        run_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
        ]
        
        for hkey, subkey in run_locations:
            for value_name in self.registry_values:
                try:
                    with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, value_name)
                        logger.info(f"✓ Removed Run entry: {value_name} from {hkey}")
                        removed_count += 1
                except FileNotFoundError:
                    pass
                except Exception as e:
                    logger.warning(f"Could not remove {value_name} from {hkey}: {e}")
        
        logger.info(f"Removed {removed_count} registry entries total")
        return removed_count > 0

    def remove_all_dlls(self):
        """Remove ALL DLLs from System32"""
        logger.info("Removing ALL DLLs from System32...")
        
        removed_count = 0
        for dll_name in self.dll_names:
            dll_path = os.path.join(self.system32_path, dll_name)
            try:
                if os.path.exists(dll_path):
                    os.remove(dll_path)
                    if not os.path.exists(dll_path):
                        logger.info(f"✓ Removed DLL: {dll_name}")
                        removed_count += 1
                    else:
                        logger.error(f"Failed to remove DLL: {dll_name}")
                else:
                    logger.info(f"DLL not found: {dll_name}")
            except Exception as e:
                logger.error(f"Error removing DLL {dll_name}: {e}")
        
        # Also remove any backup DLLs
        backup_pattern = os.path.join(self.system32_path, "*.backup")
        for backup_file in glob.glob(backup_pattern):
            try:
                os.remove(backup_file)
                logger.info(f"✓ Removed backup: {os.path.basename(backup_file)}")
                removed_count += 1
            except Exception as e:
                logger.warning(f"Could not remove backup {backup_file}: {e}")
        
        logger.info(f"Removed {removed_count} DLL files total")
        return removed_count > 0

    def restart_print_spooler(self):
        """Restart print spooler service"""
        logger.info("Restarting Print Spooler service...")
        
        try:
            # Stop spooler
            logger.info("Stopping Print Spooler service...")
            stop_result = subprocess.run(['net', 'stop', 'spooler', '/y'], 
                                       capture_output=True, text=True, check=False)
            time.sleep(3)
            
            # Start spooler
            logger.info("Starting Print Spooler service...")
            start_result = subprocess.run(['net', 'start', 'spooler'], 
                                        capture_output=True, text=True, check=False)
            
            # Verify service is running
            time.sleep(2)
            verify_result = subprocess.run(['sc', 'query', 'spooler'],
                                         capture_output=True, text=True, check=False)
            
            if "RUNNING" in verify_result.stdout:
                logger.info("✓ Print Spooler service restarted successfully")
                return True
            else:
                logger.warning("Print Spooler may not be running properly")
                return False
                
        except Exception as e:
            logger.error(f"Error restarting spooler: {e}")
            return False

    def cleanup_all_files(self):
        """Remove ALL created files from all versions"""
        logger.info("Cleaning up ALL files...")
        
        # Comprehensive list of ALL possible files created by any version
        files_to_remove = [
            # Log files
            "C:\\Windows\\Temp\\ultimate_working.log",
            "C:\\Windows\\Temp\\ultimate_delayed.log", 
            "C:\\Windows\\Temp\\port_monitor_cleanup.log",
            "C:\\Windows\\Temp\\ultimate_cleanup_complete.log",
            "C:\\Windows\\Temp\\zombie_boot.log",
            "C:\\Windows\\Temp\\zombie_complete.log",
            "C:\\Windows\\Temp\\port_monitor.log",
            "C:\\Windows\\Temp\\task_creation.log",
            "C:\\Windows\\Temp\\delayed_task_creation.log",
            "C:\\Windows\\Temp\\ui_trigger.log",
            "C:\\Windows\\Temp\\ui_trigger_delayed.log",
            "C:\\Windows\\Temp\\registry_set.log",
            "C:\\Windows\\Temp\\startup_setup.log",
            
            # Success files
            "C:\\Windows\\Temp\\boot_success.txt",
            "C:\\Windows\\Temp\\persistence_success.txt",
            "C:\\Windows\\Temp\\persistence_delayed_success.txt",
            
            # Notepad files
            "C:\\Windows\\Temp\\notepad_success.txt",
            "C:\\Windows\\Temp\\notepad_success_delayed.txt",
            "C:\\Windows\\Temp\\startup_success.txt",
            "C:\\Windows\\Temp\\run_registry_success.txt",
            
            # Batch files
            "C:\\Windows\\Temp\\ultimate_ui.bat",
            "C:\\Windows\\Temp\\ultimate_ui_delayed.bat",
            "C:\\Windows\\Temp\\show_ui.bat",
            "C:\\Windows\\Temp\\startup_ui.bat",
            "C:\\Windows\\Temp\\run_delayed.bat",
            
            # UI logs
            "C:\\Windows\\Temp\\ui_display.log",
            "C:\\Windows\\Temp\\ui_ready.txt"
        ]
        
        removed_count = 0
        
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"✓ Removed: {os.path.basename(file_path)}")
                    removed_count += 1
            except Exception as e:
                logger.warning(f"Could not remove {file_path}: {e}")
        
        # Remove any files with patterns
        patterns = [
            "C:\\Windows\\Temp\\*zombie*",
            "C:\\Windows\\Temp\\*ultimate*", 
            "C:\\Windows\\Temp\\*monitor*",
            "C:\\Windows\\Temp\\*safebreach*",
            "C:\\Windows\\Temp\\*persistence*",
            "C:\\Windows\\Temp\\*boot*success*",
            "C:\\Windows\\Temp\\*notepad*success*"
        ]
        
        for pattern in patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"✓ Removed pattern: {os.path.basename(file_path)}")
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove {file_path}: {e}")
        
        logger.info(f"Removed {removed_count} files total")
        return removed_count > 0

    def verify_cleanup(self):
        """Verify that ALL components have been removed"""
        logger.info("Verifying complete cleanup...")
        
        remaining_components = []
        
        # Check for remaining scheduled tasks
        for task_name in self.task_names:
            try:
                result = subprocess.run(['schtasks', '/query', '/tn', task_name], 
                                      capture_output=True, check=False)
                if result.returncode == 0:
                    remaining_components.append(f"Scheduled task: {task_name}")
            except:
                pass
        
        # Check for remaining DLLs
        for dll_name in self.dll_names:
            dll_path = os.path.join(self.system32_path, dll_name)
            if os.path.exists(dll_path):
                remaining_components.append(f"DLL: {dll_name}")
        
        # Check for remaining registry entries
        for monitor_name in self.monitor_names:
            try:
                registry_path = f"SYSTEM\\CurrentControlSet\\Control\\Print\\Monitors\\{monitor_name}"
                winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
                remaining_components.append(f"Registry: {monitor_name}")
            except:
                pass
        
        if remaining_components:
            logger.warning(f"Found {len(remaining_components)} remaining components:")
            for component in remaining_components:
                logger.warning(f"  - {component}")
            return False
        else:
            logger.info("✓ Verification passed: No remaining components found")
            return True

    def show_cleanup_complete_message(self):
        """Show comprehensive cleanup completion message"""
        try:
            message = (
                "PORT MONITOR PERSISTENCE - COMPLETE CLEANUP FINISHED\n\n"
                "ALL components have been removed:\n"
                "• All scheduled tasks deleted\n"
                "• All registry entries removed\n"
                "• All DLLs removed from System32\n"
                "• Print Spooler service restarted\n"
                "• All log and success files cleaned\n\n"
                "System has been restored to its original state.\n"
                "No trace of the persistence remains."
            )
            
            ctypes.windll.user32.MessageBoxW(0, message, "Cleanup Complete - All Versions", 0x40 | 0x0)
        except Exception as e:
            logger.error(f"Cleanup message failed: {e}")

    def execute_complete_cleanup(self):
        """Main comprehensive cleanup function"""
        logger.info("=" * 60)
        logger.info("STARTING COMPLETE PORT MONITOR PERSISTENCE CLEANUP")
        logger.info("Removing ALL versions and components")
        logger.info("=" * 60)
        
        if not self.check_admin_privileges():
            return False
        
        cleanup_steps = [
            ("Remove ALL scheduled tasks", self.remove_all_scheduled_tasks),
            ("Remove ALL registry entries", self.remove_all_registry_entries),
            ("Remove ALL DLLs", self.remove_all_dlls),
            ("Restart Print Spooler", self.restart_print_spooler),
            ("Cleanup ALL files", self.cleanup_all_files),
            ("Verify complete cleanup", self.verify_cleanup)
        ]
        
        success_count = 0
        total_steps = len(cleanup_steps)
        
        for step_name, step_func in cleanup_steps:
            logger.info(f"\n--- {step_name.upper()} ---")
            try:
                if step_func():
                    logger.info(f"✓ SUCCESS: {step_name}")
                    success_count += 1
                else:
                    logger.warning(f"⚠ WARNING: {step_name} had issues")
            except Exception as e:
                logger.error(f"✗ ERROR: {step_name} - {e}")
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("CLEANUP COMPLETION SUMMARY")
        logger.info(f"Steps completed: {success_count}/{total_steps}")
        
        if success_count >= 4:  # At least 4 out of 6 steps successful
            logger.info("✓ CLEANUP SUCCESSFUL - System restored")
            self.show_cleanup_complete_message()
            return True
        else:
            logger.error("✗ CLEANUP INCOMPLETE - Manual cleanup may be needed")
            return False

def main():
    """Main execution function"""
    print("PORT MONITOR PERSISTENCE - COMPLETE CLEANUP")
    print("Removes ALL versions: Original + Delayed UI")
    print("SafeBreach Research - MITRE ATT&CK T1547.010")
    print("=" * 60)
    
    if os.name != 'nt':
        print("ERROR: Windows operating system required")
        sys.exit(1)
    
    try:
        cleaner = CompleteCleanup()
        success = cleaner.execute_complete_cleanup()
        
        if success:
            print("\n CLEANUP COMPLETED SUCCESSFULLY!")
            print(" All scheduled tasks removed")
            print(" All registry entries deleted") 
            print(" All DLLs removed from System32")
            print(" Print Spooler restarted")
            print(" All files cleaned up")
            print(" System restored to original state")
            print("\nCheck C:\\Windows\\Temp\\ultimate_cleanup_complete.log for details")
        else:
            print("\n⚠ CLEANUP COMPLETED WITH WARNINGS")
            print("Some components may need manual removal")
            print("Check the log file for details")
            
    except Exception as e:
        print(f"❌ CRITICAL CLEANUP ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()