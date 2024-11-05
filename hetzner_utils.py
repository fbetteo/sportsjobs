import psycopg2
import os
from psycopg2 import sql


def start_postgres_connection():
    try:
        conn = psycopg2.connect(
            # host=os.getenv("HETZNER_POSTGRES_HOST"),
            host="localhost",
            port=os.getenv("HETZNER_POSTGRES_PORT"),
            dbname=os.getenv("HETZNER_POSTGRES_DB"),
            user=os.getenv("HETZNER_POSTGRES_USER"),
            password=os.getenv("HETZNER_POSTGRES_PASSWORD"),
        )

        print("Connected to PostgreSQL database!")
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        exit(1)

    return conn


def get_recent_urls(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT url FROM jobs where CURRENT_DATE - start_date < 30")
        records = cursor.fetchall()
        url_list = [url[0] for url in records]
    return url_list


def get_skills(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT UNNEST(skills) AS value FROM jobs;")
        records = cursor.fetchall()
        skills_list = [skill[0] for skill in records]
    return skills_list


def insert_records(conn, table, data):
    try:
        # Use context manager to open connection
        # Use another context manager to open cursor
        with conn.cursor() as cursor:
            # Build the SQL query dynamically and safely using psycopg2.sql
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                sql.SQL(", ").join(sql.Placeholder() * len(data)),
            )
            print(query.as_string(conn))
            # Execute the query with values as parameters
            cursor.execute(query, tuple(data.values()))

    except Exception as e:
        print(f"Error occurred: {e}")
        # Optional: Handle rollback explicitly if an error occurs
        if conn:
            conn.rollback()
    else:
        print("Data inserted successfully.")


# def insert_record(conn, table, data):
#     try:
#         insert_query = """
#         INSERT INTO users (name, email)
#         VALUES (%s, %s);
#         """
#         cursor.execute(insert_query, (data["name"], data["email"]))
#         conn.commit()
#     except Exception as e:
#         print(f"Error inserting record: {e}")
#         conn.rollback()
