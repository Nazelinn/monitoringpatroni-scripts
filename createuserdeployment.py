import psycopg2
import random
import string



PGUSER = "ozalpn"
PGPASSWORDD = "3nBr44!XqKdzPP"   
PGHOST = "pg-payment-loan-db.hepsi.io"
PGPORT = "6532"
DEPLOYMENTUSER = "pg-payment-loan-deployment-user"

def generate_password(length=12):
    if length < 12:
        raise ValueError("Şifre uzunluğu en az 12 olmalı")

    letters = string.ascii_letters  # a-z A-Z
    digits = string.digits          # 0-9
    specials = "!*"

    # En az 2 özel karakter garanti et
    password = [
        random.choice(specials),
        random.choice(specials),
        random.choice(letters),
        random.choice(digits),
    ]

    # Kalan karakterleri rastgele doldur
    all_chars = letters + digits + specials
    password += random.choices(all_chars, k=length - len(password))

    # Karıştır
    random.shuffle(password)

    return "".join(password)
PGPASSWORD = generate_password()
print(f'password: {PGPASSWORD}')
def run_query(dbname, query):
    conn = psycopg2.connect(
        dbname=dbname,
        user=PGUSER,
        password=PGPASSWORDD,
        host=PGHOST,
        port=PGPORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(query)
    cur.close()
    conn.close()

# 1. Deployment user sadece bir kez oluştur
create_user_sql = f"""
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{DEPLOYMENTUSER}') THEN
      CREATE USER "{DEPLOYMENTUSER}" WITH SUPERUSER PASSWORD '{PGPASSWORD}';
   END IF;
END
$$;
"""
print(create_user_sql)
run_query("postgres", create_user_sql)

# 2. Tüm veritabanlarını listele
conn = psycopg2.connect(
    dbname="postgres",
    user=PGUSER,
    password=PGPASSWORDD,
    host=PGHOST,
    port=PGPORT
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
dblist = [row[0] for row in cur.fetchall()]
cur.close()
conn.close()

# 3. Her veritabanında şemaları bul ve alter yap
for db in dblist:
    print(f"Processing database: {db}")
    conn = psycopg2.connect(
        dbname=db,
        user=PGUSER,
        password=PGPASSWORDD,
        host=PGHOST,
        port=PGPORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    # o DB'deki %appuser% userlarını al
    cur.execute("SELECT rolname FROM pg_roles WHERE rolname LIKE '%appuser%';")
    appusers = [f'"{row[0]}"' for row in cur.fetchall()]
    print(appusers)

    # TO kısmına ekle
    to_users = appusers
    to_users_str = ",".join(to_users)

    roles_str = ",".join(["gkiran","ozalpn","usarikaya","oaltuntas","nturkoglu", f'"{DEPLOYMENTUSER}"'])

    cur.execute("""
        SELECT nspname FROM pg_namespace 
        WHERE nspname NOT IN ('pg_catalog','information_schema');
    """)
    schemas = [row[0] for row in cur.fetchall()]

    for schema in schemas:
        print(f"   🔹 Processing schema: {schema}")
        alter_sql = f"""
        ALTER DEFAULT PRIVILEGES FOR ROLE {roles_str}
        IN SCHEMA "{schema}" GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {to_users_str};

        ALTER DEFAULT PRIVILEGES FOR ROLE {roles_str}
        IN SCHEMA "{schema}" GRANT ALL ON SEQUENCES TO {to_users_str};
        """
        print(alter_sql)
        cur.execute(alter_sql)

    cur.close()
    conn.close()

print("✅ Script completed.")
print(f'password: {PGPASSWORD}')
print(f'user: {DEPLOYMENTUSER}')
