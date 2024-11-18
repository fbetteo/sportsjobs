import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path("sportsjobs") / ".env"
load_dotenv(dotenv_path=env_path)
# Airtable configuration

# PostgreSQL configuration
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
record = cursor.fetchone()
print(f"You are connected to - {record}\n")

cursor.close()
conn.close()

# funciona si estoy ssheado en hetzner o dsede mi pc si corro el comando de abajo, que va a forwardear el puerto. En ese caso podria correrlo desde local tambien
# ssh -L 5432:localhost:5432 root@188.245.110.228
