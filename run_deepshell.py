import subprocess
import sys
import os
import signal

def start_backend():
    cmd = [sys.executable, os.path.join("deepshell-backend", "wrapper.py")]
    process = subprocess.Popen(cmd)
    print(f"DeepShell backend started with PID {process.pid}")
    return process

def main():
    backend_process = start_backend()
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("Stopping DeepShell backend...")
        backend_process.send_signal(signal.SIGINT)
        backend_process.wait()

if __name__ == "__main__":
    main()
