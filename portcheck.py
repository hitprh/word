
#!/usr/bin/python3

import subprocess
import time
from datetime import datetime

SERVICES = ['stunnel4', 'dropbear', 'squid', 'openvpn', 'ssh']
LOG_FILE = '/var/log/multimonitor.log'

def log(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def get_service_status(service):
    result = subprocess.Popen(['systemctl', 'status', service],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = result.communicate()
    return output.decode('utf-8')  # Decode bytes to string

def check_and_restart_services():
    restarted_services = []
    for service in SERVICES:
        try:
            # Get service status
            status_output = get_service_status(service)
            if 'active (running)' not in status_output and 'active (exited)' not in status_output:
                # Log the current status if it's not acceptable
                log(f"{service} is not in an acceptable state. Current status: {status_output.splitlines()[2].strip()}")
                
                # Restart the service
                log(f"{service} is not running, restarting...")
                subprocess.run(['systemctl', 'restart', service], check=True)
                log(f"Restarted {service}")
                restarted_services.append(service)
        except subprocess.CalledProcessError as e:
            log(f"Failed to restart {service}: {e}")
    
    return restarted_services

def main():
    while True:
        restarted_services = check_and_restart_services()
        if restarted_services:
            print(f"Restarted services: {', '.join(restarted_services)}")
        else:
            print("All services are running fine.")
        time.sleep(30)

if __name__ == "__main__":
    main()
