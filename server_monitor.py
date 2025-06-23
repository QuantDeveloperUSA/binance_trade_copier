import asyncio
import logging
import sys
import uvicorn
from datetime import datetime

# Import your main app
from main import app

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ServerMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.restart_count = 0
    
    async def run_server(self):
        """Run server with monitoring"""
        while True:
            try:
                self.restart_count += 1
                logger.info(f"=== SERVER START ATTEMPT #{self.restart_count} ===")
                logger.info(f"Start time: {datetime.now()}")
                logger.info(f"Initial start: {self.start_time}")
                
                # Configure uvicorn with more explicit settings
                config = uvicorn.Config(
                    app=app,
                    host="0.0.0.0",
                    port=8000,
                    log_level="info",
                    access_log=True,
                    reload=False,
                    workers=1
                )
                
                server = uvicorn.Server(config)
                logger.info("Starting uvicorn server...")
                await server.serve()
                
                # If we get here, server stopped normally
                logger.warning("Server stopped normally - this is unexpected for a production server")
                break
                
            except KeyboardInterrupt:
                logger.info("Server stopped by user (Ctrl+C)")
                break
            except Exception as e:
                logger.error(f"Server crashed with error: {e}")
                logger.exception("Full error details:")
                logger.info("Waiting 10 seconds before restart...")
                await asyncio.sleep(10)
            
        logger.info("Server monitor shutdown complete")

if __name__ == "__main__":
    monitor = ServerMonitor()
    try:
        asyncio.run(monitor.run_server())
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Monitor failed: {e}")
        logger.exception("Monitor error details:")
