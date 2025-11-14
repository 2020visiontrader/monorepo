#!/usr/bin/env python
"""
Worker entrypoint that runs both health check server and Celery worker.
Required for Render web services that need HTTP health checks.
Uses only standard library for minimal dependencies.
"""
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import time

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'timestamp': time.time()}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_health_server():
    """Run simple HTTP health check server in background thread."""
    try:
        with socketserver.TCPServer(("", 8000), HealthCheckHandler) as httpd:
            print("Health check server started on port 8000")
            httpd.serve_forever()
    except Exception as e:
        print(f"Health server error: {e}")

def main():
    """Main entrypoint - start health server and Celery worker."""
    # Start health check server in background
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Give server time to start
    time.sleep(2)

    # Start Celery worker
    queue = os.environ.get('CELERY_QUEUE', 'celery')
    cmd = f'celery -A config.celery worker -Q {queue} --loglevel=info --concurrency=1 --hostname={queue}-worker@%h'
    print(f'Starting Celery worker: {cmd}')

    # Run Celery worker (this will block)
    sys.exit(subprocess.call(cmd, shell=True))

if __name__ == '__main__':
    main()
