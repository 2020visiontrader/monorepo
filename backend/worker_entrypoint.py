#!/usr/bin/env python
"""
Worker entrypoint that runs both health check server and Celery worker.
Required for Render web services that need HTTP health checks.
"""
import os
import subprocess
import sys
import time
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': time.time()}

def run_health_server():
    """Run Flask health check server in background thread."""
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def main():
    """Main entrypoint - start health server and Celery worker."""
    # Start health check server in background
    import threading
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Give server time to start
    time.sleep(2)
    print("Health check server started on port 8000")

    # Start Celery worker
    queue = os.environ.get('CELERY_QUEUE', 'celery')
    cmd = f'celery -A config.celery worker -Q {queue} --loglevel=info --concurrency=1 --hostname={queue}-worker@%h'
    print(f'Starting Celery worker: {cmd}')

    # Run Celery worker (this will block)
    sys.exit(subprocess.call(cmd, shell=True))

if __name__ == '__main__':
    main()
