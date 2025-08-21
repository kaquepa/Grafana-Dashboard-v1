import os
import psycopg2

def main():
    #db_url = os.environ.get("DATABASE_URL")
    #conn = psycopg2.connect(db_url)
    #cur = conn.cursor()
    #cur.execute("SELECT version();")
    #version = cur.fetchone()
    #print(f"Connected to Postgres! Version: {version[0]}")
    #cur.close()
    #conn.close()
    pass
    print("Finished execution")

if __name__ == "__main__":
    main()
