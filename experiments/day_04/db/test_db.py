import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="aegisflow",
    user="jyotish",
    password="1234",
    port="5432"
)

print("Connected successfully")

conn.close()