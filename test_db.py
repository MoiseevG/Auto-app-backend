import psycopg2

try:
    conn = psycopg2.connect(
        dbname="autoservice_db",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    print("Connection to PostgreSQL successful!")
    conn.close()
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")