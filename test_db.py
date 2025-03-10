import psycopg2

DATABASE_URL = "postgresql://postgres.kzcawnxbcoxwbeulbgpp:Idaen147&@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

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
