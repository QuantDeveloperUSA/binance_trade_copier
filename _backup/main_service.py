import sys
import os

# Check if running as Windows service
if len(sys.argv) > 1 and sys.argv[1] in ['install', 'update', 'remove', 'start', 'stop', 'restart']:
    from service_wrapper import BinanceCopyTraderService
    import win32serviceutil
    win32serviceutil.HandleCommandLine(BinanceCopyTraderService)
else:
    # Run normally
    from main import app
    import uvicorn
    
    if __name__ == "__main__":
        # When running as service, templates path needs to be absolute
        if getattr(sys, 'frozen', False):
            # Running as exe
            template_dir = os.path.join(os.path.dirname(sys.executable), "templates")
            os.environ['TEMPLATE_DIR'] = template_dir
            
        uvicorn.run(app, host="0.0.0.0", port=8000)
