import psycopg2

def check_product_ids():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            port=5434, 
            database='urun_risk_analiz', 
            user='postgres', 
            password='furkan'
        )
        cur = conn.cursor()
        
        # telefon_urunleri tablosundaki sütunları kontrol et
        print("=== TELEFON_URUNLERI TABLO YAPISI ===")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'telefon_urunleri'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f'Sütun: {col[0]}, Tip: {col[1]}')
            
        print("\n=== TELEFON_URUNLERI VERİLERİ ===")
        # İlk sütunu kullanarak veri çek
        first_column = columns[0][0] if columns else 'name'
        cur.execute(f'SELECT {first_column} FROM telefon_urunleri LIMIT 5')
        results = cur.fetchall()
        for i, row in enumerate(results):
            print(f'{i+1}. {first_column}: {row[0]}')
        
        # Embedding tablosundaki product_id'leri kontrol et
        print("\n=== TELEFON_URUNLERI_EMBEDDINGS TABLO YAPISI ===")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'telefon_urunleri_embeddings'
            ORDER BY ordinal_position
        """)
        emb_columns = cur.fetchall()
        for col in emb_columns:
            print(f'Sütun: {col[0]}, Tip: {col[1]}')
            
        print("\n=== TELEFON_URUNLERI_EMBEDDINGS VERİLERİ ===")
        cur.execute('SELECT product_id, product_name FROM telefon_urunleri_embeddings LIMIT 5')
        results = cur.fetchall()
        for row in results:
            print(f'Product ID: {row[0]}, Name: {row[1]}')
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    check_product_ids()