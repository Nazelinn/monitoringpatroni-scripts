import subprocess
import psycopg2
import platform
import sys
from datetime import datetime


def get_leader_connection():
    try:

        result = subprocess.run(['patronictl', '-c', '/etc/patroni.yml', 'list'], 
                                capture_output=True, text=True)
        
        lines = result.stdout.split('\n')
        leader_host = None

        for line in lines:
            if "Leader" in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]

                if len(parts) >= 2:
                    leader_host = parts[1] # IP adresini al
                break

        if not leader_host:
            print("--- Lists Çıktısı ---")
            print(result.stdout)
            raise Exception("Not found in table 'Leader'")

        print(f"Leader IP: {leader_host}")
        
        conn = psycopg2.connect(
            dbname="postgres", 
            user="postgres", 
            host=leader_host,
            password="ccnPdhs3WDopnN3oYf",
            port=5432,
            connect_timeout=5
        )
        return conn

    except Exception as e:
        print(f"Hata: {e}")
        return None

def run_automation():
    conn = get_leader_connection()
    if not conn:
        return

    conn.autocommit = True
    cur = conn.cursor()
    
    machine_name = platform.node().replace("-", "_").replace(".", "_")
    table_name = datetime.now().strftime("data_%Y_%m_%d")

    try:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{machine_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {machine_name}")
            print(f"Database '{machine_name}' created.")
        else:
            print(f"Database '{machine_name}' already exists.")

        conn_new = psycopg2.connect(dbname=machine_name, user="postgres",password="ccnPdhs3WDopnN3oYf", host=conn.info.host)
        cur_new = conn_new.cursor()
        cur_new.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, info TEXT, created_at TIMESTAMP DEFAULT NOW())")
        conn_new.commit()
        print(f"Table '{table_name}' successfully created.")
        
        cur_new.close()
        conn_new.close()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_automation()

