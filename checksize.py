import psycopg2

db_params = {'user': 'postgres','password': 'ccnPdhs3WDopnN3oYf','host': 'localhost','port': '5432'}

def check_all_databases():
    try:
        conn = psycopg2.connect(database='postgres', **db_params)
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';")
        databases = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()

        for db_name in databases:
            try:
                db_conn = psycopg2.connect(database=db_name, **db_params)
                db_cur = db_conn.cursor()

                query = """SELECT relname AS table_name, pg_total_relation_size(C.oid) / (1024 * 1024) AS size_mb FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN ('pg_catalog', 'information_schema')   AND relkind = 'r'  AND pg_total_relation_size(C.oid) / (1024 * 1024) > 50;"""
                
                db_cur.execute(query)
                large_tables = db_cur.fetchall()

                if large_tables:
                    for table_name, size_mb in large_tables:
                        log_write(f"WARNING: Database [{db_name}] table '{table_name}' exceeded size limit: {size_mb} MB")
                else:
                    log_write(f"Check Status: [{db_name}] - No tables found exceeding 50 MB.")

                db_cur.close()
                db_conn.close()

            except Exception as e:
                log_write(f"ERROR: Could not connect to database {db_name}: {e}")

    except Exception as e:
        log_write(f"GLOBAL ERROR: Failed to retrieve database list: {e}")

def log_write(message):
    print(message)

if __name__ == "__main__":
    check_all_databases()
