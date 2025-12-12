import subprocess
import time
import sys
import os
import signal

# Define processes globally so we can kill them on exit
procs = []

def cleanup(signum, frame):
    """Kills all subprocesses when you press Ctrl+C"""
    print("\n\n🛑 Shutting down CV Extractor...")
    for p in procs:
        p.terminate()
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, cleanup)

def run_command(cmd, name):
    """Helper to start a process"""
    print(f"🚀 Starting {name}...")
    # shell=False is safer, but we use shell=True for simple environment inheritance on Linux
    p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
    procs.append(p)
    return p

if __name__ == "__main__":
    print("=======================================")
    print("   🤖 AIO CV EXTRACTOR - LAUNCHER    ")
    print("=======================================")

    # 1. Start Redis (Just in case it's not running as a service)
    # We don't track this process strictly because it might be a system service
    try:
        subprocess.Popen(["redis-server", "--daemonize", "yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Redis check initiated")
    except Exception:
        print("⚠️  Could not start Redis automatically. Assuming it's running as a service.")

    time.sleep(1)

    # 2. Start Celery Worker
    # Note: We activate the venv python explicitly if needed, but assuming you run this FROM venv
    run_command("celery -A tasks.celery_app worker --loglevel=info -n worker1@%h", "Celery Worker")

    # 3. Start Flask App
    run_command("python3 app.py", "Flask API")

    print("\n✅ System is running!")
    print("🌍 Open your browser: http://127.0.0.1:5000")
    print("⌨️  Press Ctrl+C to stop everything.\n")

    # Keep the script alive to monitor
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup(None, None)