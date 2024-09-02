
#!/usr/bin/python3

import subprocess
import time
from datetime import datetime

SERVICES = ['stunnel4', 'dropbear', 'squid', 'openvpn', 'ssh']
LOG_FILE = '/var/log/multimonitor.log'

def log(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def check_and_restart_services():
    for service in SERVICES:
        try:
            # Check if the service is active
            result = subprocess.run(['systemctl', 'is-active', '--quiet', service],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                # Service is not active
                log(f"{service} is not running, restarting...")
                subprocess.run(['systemctl', 'restart', service], check=True)
                log(f"Restarted {service}")
        except subprocess.CalledProcessError as e:
            log(f"Failed to restart {service}: {e}")

def main():
    while True:
        check_and_restart_services()
        time.sleep(10)

if __name__ == "__main__":
    main()