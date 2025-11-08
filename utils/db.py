import psycopg2

def get_db():
    return psycopg2.connect(
        dbname="sapience",
        user="postgres",
        password="your_password",
        host="localhost",
        port="5432"
    )