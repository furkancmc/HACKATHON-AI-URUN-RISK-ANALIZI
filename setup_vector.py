import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="urun_risk_analiz",
        user="postgres",
        password="furkan"
    )
    cur = conn.cursor()

    # Vector extension ekle
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("✅ Vector extension eklendi")

    # Embedding sütunu ekle
    cur.execute("ALTER TABLE vector_products ADD COLUMN IF NOT EXISTS embedding vector(384);")
    print("✅ Embedding sütunu eklendi")

    # Index oluştur
    cur.execute("""
                CREATE INDEX IF NOT EXISTS vector_products_embedding_idx
                    ON vector_products USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """)
    print("✅ Index oluşturuldu")

    conn.commit()
    cur.close()
    conn.close()

    print("🎉 PostgreSQL setup tamamlandı!")

except Exception as e:
    print(f"❌ Hata: {e}")