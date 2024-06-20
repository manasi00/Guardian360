#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess
import signal

model_run = None

def handle_signal(signum, frame):
    global model_run
    if model_run:
        model_run.kill()
        print("Model process terminated.")
    sys.exit(0)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ahss0001.settings')
    try:
        from django.core.management import execute_from_command_line
        try:
            global model_run
            model_run = subprocess.Popen(['python', 'inference/run_detect.py'])
            print("Models Running...")
        except Exception as e:
            print(e)
            print('Failed to run detect.py')
        
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Register signal handler
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Execute Django command
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
