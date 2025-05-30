import subprocess
import sys
import time
import os
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_fastapi():
    """Run the FastAPI server"""
    try:
        # Ensure we're in the correct directory
        os.chdir(Path(__file__).parent)
        
        # Run FastAPI with uvicorn
        process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "api_server:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(2)
        
        if process.poll() is not None:
            # Process has terminated
            out, err = process.communicate()
            logger.error(f"FastAPI failed to start: {err}")
            return None
            
        logger.info("FastAPI server started successfully")
        return process
        
    except Exception as e:
        logger.error(f"Failed to start FastAPI: {str(e)}")
        return None

def run_streamlit():
    """Run the Streamlit app"""
    try:
        # Ensure we're in the correct directory
        os.chdir(Path(__file__).parent)
        
        # Run Streamlit
        process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit",
                "run", "main.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(2)
        
        if process.poll() is not None:
            # Process has terminated
            out, err = process.communicate()
            logger.error(f"Streamlit failed to start: {err}")
            return None
            
        logger.info("Streamlit server started successfully")
        return process
        
    except Exception as e:
        logger.error(f"Failed to start Streamlit: {str(e)}")
        return None

def cleanup(processes):
    """Cleanup function to terminate all processes"""
    for process in processes:
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main function to run both servers"""
    processes = []
    
    try:
        # Start FastAPI
        fastapi_process = run_fastapi()
        if fastapi_process:
            processes.append(fastapi_process)
        else:
            logger.error("Failed to start FastAPI server")
            return
            
        # Start Streamlit
        streamlit_process = run_streamlit()
        if streamlit_process:
            processes.append(streamlit_process)
        else:
            logger.error("Failed to start Streamlit server")
            return
            
        # Keep the script running
        while all(p.poll() is None for p in processes):
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        cleanup(processes)

if __name__ == "__main__":
    main() 