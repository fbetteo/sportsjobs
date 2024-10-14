import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="sportsjobs",
    user="admin",
    password="carotex1",
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
record = cursor.fetchone()
print(f"You are connected to - {record}\n")

cursor.close()
conn.close()

# funciona si estoy ssheado en hetzner o dsede mi pc si corro el comando de abajo, que va a forwardear el puerto. En ese caso podria correrlo desde local tambien
# ssh -L 5432:localhost:5432 root@188.245.110.228
