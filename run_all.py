import subprocess
import time
import os
import signal
import sys
import atexit

def cleanup_processes(processes):
    for p in processes:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except:
            pass

def main():
    # Store processes for cleanup
    processes = []
    atexit.register(cleanup_processes, processes)
    
    # Start FastAPI server
    print("Starting FastAPI server...")
    fastapi_process = subprocess.Popen(
        ["uvicorn", "utils.api_routes:app", "--host", "0.0.0.0", "--port", "8000"],
        preexec_fn=os.setsid
    )
    processes.append(fastapi_process)
    
    # Wait for FastAPI to start
    time.sleep(2)
    
    # Start Streamlit
    print("Starting Streamlit...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "main.py"],
        preexec_fn=os.setsid
    )
    processes.append(streamlit_process)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        cleanup_processes(processes)
        sys.exit(0)

if __name__ == "__main__":
    main() 