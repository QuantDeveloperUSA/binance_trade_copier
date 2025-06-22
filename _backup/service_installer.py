import os
import subprocess
import ctypes

def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_service():
    """Install the Binance Copy Trader as a Windows service"""
    if not is_admin():
        print("ERROR: This script requires administrator privileges!")
        print("Please run as administrator.")
        return False
    
    exe_path = os.path.join(os.getcwd(), "dist", "BinanceCopyTrader.exe")
    
    if not os.path.exists(exe_path):
        print(f"ERROR: Executable not found at {exe_path}")
        print("Please run build_exe.bat first.")
        return False
    
    try:
        # Install the service
        print("Installing service...")
        subprocess.run([exe_path, "install"], check=True)
        
        # Configure service to start automatically
        print("Configuring automatic startup...")
        subprocess.run([
            "sc", "config", "BinanceCopyTrader", 
            "start=", "auto",
            "obj=", "LocalSystem"
        ], check=True)
        
        # Set recovery options
        print("Setting recovery options...")
        subprocess.run([
            "sc", "failure", "BinanceCopyTrader",
            "reset=", "86400",
            "actions=", "restart/60000/restart/60000/restart/60000"
        ], check=True)
        
        # Start the service
        print("Starting service...")
        subprocess.run(["net", "start", "BinanceCopyTrader"], check=True)
        
        print("\nService installed successfully!")
        print("The Binance Copy Trader will now start automatically on system boot.")
        print("\nService commands:")
        print("  Stop service:    net stop BinanceCopyTrader")
        print("  Start service:   net start BinanceCopyTrader")
        print("  Remove service:  BinanceCopyTrader.exe remove")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install service: {e}")
        return False

if __name__ == "__main__":
    install_service()
