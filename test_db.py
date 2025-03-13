import psycopg2

DATABASE_URL = "your_supabasedb"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
finally:
    if 'conn' in locals():
        cur.close()
        conn.close()
