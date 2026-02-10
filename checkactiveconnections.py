import psycopg2
import subprocess
import time

LOG_FILE = "monitor.log"
DB_PARAMS = "dbname=postgres user=postgres password=ccnPdhs3WDopnN3oYf host=localhost port=5432"
SERVICE_NAME = "patroni"

def log_write(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}")

def check_metrics():
    try:
        conn = psycopg2.connect(DB_PARAMS)
        cur = conn.cursor()

        cur.execute("SELECT count(*) FROM pg_stat_activity")
        count = cur.fetchone()[0]
        
        if count > 10:
            log_write(f"WARNING: High connection count detected: {count} (Threshold: 10)")
        else:
            log_write(f"Connection Count: {count}")

        cur.close()
        conn.close()
    except Exception as e:
        log_write(f"ERROR: Could not retrieve metrics. Database might not be ready yet. ({e})")

if __name__ == "__main__":
    check_metrics()
