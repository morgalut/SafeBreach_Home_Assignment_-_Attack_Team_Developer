#!/usr/bin/env python3
"""
Complete Port Monitor Persistence Cleanup
SafeBreach Home Assignment - T1547.010
"""

import os
import sys
import ctypes
import logging
import subprocess
import winreg
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\Windows\\Temp\\port_monitor_cleanup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompleteCleanup:
    def __init__(self):
        self.monitor_name = "UltimateMonitor"
        self.dll_name = "monitor_dll.dll"
        self.system32_path = os.path.join(os.environ['WINDIR'], 'System32')
        self.dll_path = os.path.join(self.system32_path, self.dll_name)
        
        # All task names to remove
        self.task_names = [
            "UltimateMonitorUI",
            "SafeBreachNotepad",
            "SafeBreachBootMessage", 
            "SafeBreachSystemBoot",
            "SafeBreachUserLogon",
            "SafeBreachSystemStartup",
            "SafeBreachStartup",
            "SafeBreachVerify"
        ]
    
    def check_admin_privileges(self):
        """Check administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def remove_scheduled_tasks(self):
        """Remove all scheduled tasks"""
        logger.info("Removing scheduled tasks...")
        
        removed_count = 0
        for task_name in self.task_names:
            try:
                result = subprocess.run(
                    ['schtasks', '/delete', '/tn', task_name, '/f'],
                    capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    logger.info(f"Removed task: {task_name}")
                    removed_count += 1
                else:
                    logger.info(f"Task not found: {task_name}")
            except Exception as e:
                logger.warning(f"Error removing task {task_name}: {e}")
        
        logger.info(f"Removed {removed_count} scheduled tasks")
        return removed_count > 0
    
    def remove_registry_entries(self):
        """Remove registry entries"""
        logger.info("Removing registry entries...")
        
        removed_count = 0
        
        # Remove port monitor registry entry
        try:
            registry_path = r"SYSTEM\CurrentControlSet\Control\Print\Monitors"
            full_path = f"{registry_path}\\{self.monitor_name}"
            
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, full_path)
            logger.info("Port monitor registry entry removed")
            removed_count += 1
        except FileNotFoundError:
            logger.info("Port monitor registry entry not found (already removed)")
            removed_count += 1
        except Exception as e:
            logger.error(f"Error removing port monitor registry: {e}")
        
        # Remove Run registry entry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"Software\Microsoft\Windows\CurrentVersion\Run", 
                              0, winreg.KEY_WRITE) as key:
                try:
                    winreg.DeleteValue(key, "UltimateMonitorUI")
                    logger.info("Run registry entry removed")
                    removed_count += 1
                except FileNotFoundError:
                    logger.info("Run registry entry not found (already removed)")
                    removed_count += 1
        except Exception as e:
            logger.error(f"Error removing Run registry: {e}")
        
        return removed_count >= 2
    
    def remove_monitor_dll(self):
        """Remove DLL from System32"""
        logger.info("Removing DLL from System32...")
        
        try:
            if os.path.exists(self.dll_path):
                os.remove(self.dll_path)
                if not os.path.exists(self.dll_path):
                    logger.info("DLL removed from System32")
                    return True
                else:
                    logger.error("Failed to remove DLL")
                    return False
            else:
                logger.info("DLL not found (already removed)")
                return True
                
        except Exception as e:
            logger.error(f"Error removing DLL: {e}")
            return False
    
    def restart_print_spooler(self):
        """Restart print spooler service"""
        logger.info("Restarting Print Spooler service...")
        
        try:
            # Stop spooler
            subprocess.run(['net', 'stop', 'spooler', '/y'], 
                         capture_output=True, text=True, check=False)
            logger.info("Print Spooler service stopped")
            
            # Wait a moment
            import time
            time.sleep(2)
            
            # Start spooler
            subprocess.run(['net', 'start', 'spooler'], 
                         capture_output=True, text=True, check=False)
            logger.info("Print Spooler service started")
            
            return True
            
        except Exception as e:
            logger.error(f"Error restarting spooler: {e}")
            return False
    
    def cleanup_files(self):
        """Remove all created files"""
        logger.info("Cleaning up files...")
        
        files_to_remove = [
            "C:\\Windows\\Temp\\persistence_success.txt",
            "C:\\Windows\\Temp\\ultimate_working.log",
            "C:\\Windows\\Temp\\port_monitor_cleanup.log",
            "C:\\Windows\\Temp\\ultimate_ui.bat",
            "C:\\Windows\\Temp\\boot_success.txt",
            "C:\\Windows\\Temp\\notepad_success.txt",
            "C:\\Windows\\Temp\\zombie_boot.log",
            "C:\\Windows\\Temp\\task_creation.log",
            "C:\\Windows\\Temp\\ui_trigger.log",
            "C:\\Windows\\Temp\\zombie_complete.log",
            "C:\\Windows\\Temp\\port_monitor.log",
            "C:\\Windows\\Temp\\registry_set.log"
        ]
        
        removed_count = 0
        
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed: {file_path}")
                    removed_count += 1
            except Exception as e:
                logger.warning(f"Could not remove {file_path}: {e}")
        
        logger.info(f"Removed {removed_count} files")
        return removed_count > 0
    
    def show_cleanup_message(self):
        """Show cleanup completion message"""
        try:
            ctypes.windll.user32.MessageBoxW(0,
                "Port Monitor Persistence has been completely removed.\n\n"
                "All registry entries deleted\n"
                "Monitor DLL removed from System32\n"
                "All scheduled tasks removed\n"
                "Print Spooler service restarted\n"
                "All log and success files cleaned up\n\n"
                "System has been restored to its original state.",
                "Cleanup Complete - SafeBreach",
                0x40 | 0x0)
        except Exception as e:
            logger.error(f"Failed to show cleanup message: {e}")
    
    def cleanup(self):
        """Main cleanup function"""
        logger.info("Starting complete cleanup...")
        
        if not self.check_admin_privileges():
            logger.error("Administrator privileges required for cleanup")
            return False
        
        steps = [
            ("Remove scheduled tasks", self.remove_scheduled_tasks),
            ("Remove registry entries", self.remove_registry_entries),
            ("Remove DLL", self.remove_monitor_dll),
            ("Restart Print Spooler", self.restart_print_spooler),
            ("Cleanup files", self.cleanup_files)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            logger.info(f"--- {step_name} ---")
            try:
                if step_func():
                    logger.info(f"SUCCESS: {step_name}")
                    success_count += 1
                else:
                    logger.warning(f"WARNING: {step_name}")
            except Exception as e:
                logger.error(f"ERROR: {step_name} - {e}")
        
        # Show completion message
        if success_count >= 3:
            self.show_cleanup_message()
        
        logger.info(f"Cleanup completed: {success_count}/{len(steps)} steps successful")
        return success_count >= 3

def main():
    """Main execution function"""
    print("Port Monitor Persistence - Complete Cleanup")
    print("SafeBreach Research")
    print("=" * 50)
    
    if os.name != 'nt':
        print("Error: Windows required")
        sys.exit(1)
    
    try:
        cleaner = CompleteCleanup()
        success = cleaner.cleanup()
        
        if success:
            print("\nCleanup completed successfully!")
            print("System restored to original state")
            print("Check C:\\Windows\\Temp\\port_monitor_cleanup.log for details")
        else:
            print("\nCleanup completed with warnings")
            print("Some manual cleanup may be needed")
            
    except Exception as e:
        print(f"Critical cleanup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()