import psycopg2
import subprocess
import time

LOG_FILE = "service.log"
DB_PARAMS = "dbname=postgres user=postgres password=ccnPdhs3WDopnN3oYf host=localhost port=5432"
SERVICE_NAME = "patroni"

def log_write(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}")

def check_and_start_service():
    check = subprocess.run(["systemctl", "is-active", SERVICE_NAME], capture_output=True, text=True)
    
    if check.stdout.strip() != "active":
        log_write(f"ALARM: {SERVICE_NAME} is down! Attempting to restart...")
        subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME])
        return False 
    
    log_write(f"Service Status: OK ({SERVICE_NAME} is running)")
    return True 


if __name__ == "__main__":
    was_already_running = check_and_start_service()
    
    if not was_already_running:
        log_write("System initiated. Waiting for DB connection to stabilize...")
        time.sleep(50)
