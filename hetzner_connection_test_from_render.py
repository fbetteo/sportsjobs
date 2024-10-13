import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.getenv("HETZNER_POSTGRES_HOST"),
        port=os.getenv("HETZNER_POSTGRES_PORT"),
        dbname=os.getenv("HETZNER_POSTGRES_DB"),
        user=os.getenv("HETZNER_POSTGRES_USER"),
        password=os.getenv("HETZNER_POSTGRES_PASSWORD"),
    )

    cursor = conn.cursor()
    print("Connected to PostgreSQL database!")
except Exception as e:
    print(f"Error connecting to PostgreSQL database: {e}")
    exit(1)


# Function to insert data into the database
def insert_record(data):
    try:
        insert_query = """
        INSERT INTO users (name, email)
        VALUES (%s, %s, ...);
        """
        cursor.execute(insert_query, (data["name"], data["email"], ...))
        conn.commit()
    except Exception as e:
        print(f"Error inserting record: {e}")
        conn.rollback()


if __name__ == "__main__":
    data_list = [{"name": "render", "email": "render@gmail.com"}]

    for data in data_list:
        insert_record(data)

    # Close the connection
    cursor.close()
    conn.close()
