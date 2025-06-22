import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess
import time

class BinanceCopyTraderService(win32serviceutil.ServiceFramework):
    _svc_name_ = "BinanceCopyTrader"
    _svc_display_name_ = "Binance Copy Trader Service"
    _svc_description_ = "Automated Binance trading copy service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.process = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.process:
            self.process.terminate()
            
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        # Get the directory where the service executable is located
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            app_path = sys.executable
        else:
            # Running as script
            app_path = os.path.abspath(__file__)
            
        app_dir = os.path.dirname(app_path)
        
        # Start the FastAPI application
        while True:
            if win32event.WaitForSingleObject(self.hWaitStop, 0) == win32event.WAIT_OBJECT_0:
                break
                
            try:
                # Run the main application
                self.process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                    cwd=app_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Wait for process to complete or service stop
                while self.process.poll() is None:
                    if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                        self.process.terminate()
                        break
                        
            except Exception as e:
                servicemanager.LogErrorMsg(f"Error starting service: {str(e)}")
                time.sleep(10)  # Wait before retry

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BinanceCopyTraderService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BinanceCopyTraderService)
