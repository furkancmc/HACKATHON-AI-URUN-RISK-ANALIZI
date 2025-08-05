# check_embeddings.py
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_embeddings():
    """Embedding durumunu kontrol et"""
    
    connection_params = {
        "host": "localhost",
        "port": 5434,
        "database": "urun_risk_analiz",
        "user": "postgres", 
        "password": "furkan"
    }
    
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        
        print("🔍 VERİTABANI DURUM KONTROLÜ")
        print("=" * 50)
        
        # Tüm tabloları listele
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        all_tables = [row[0] for row in cur.fetchall()]
        print(f"📋 Toplam tablo sayısı: {len(all_tables)}")
        
        # Kaynak tabloları
        source_tables = [t for t in all_tables if not t.endswith('_embeddings')]
        print(f"📦 Kaynak tablo sayısı: {len(source_tables)}")
        
        # Embedding tabloları
        embedding_tables = [t for t in all_tables if t.endswith('_embeddings')]
        print(f"🔨 Embedding tablo sayısı: {len(embedding_tables)}")
        
        print("\n📊 TABLO DETAYLARI:")
        print("-" * 50)
        
        for table in source_tables:
            # Kaynak tablo kayıt sayısı
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            source_count = cur.fetchone()[0]
            
            # Embedding tablosu var mı?
            embedding_table = f"{table}_embeddings"
            embedding_count = 0
            
            if embedding_table in embedding_tables:
                cur.execute(f"SELECT COUNT(*) FROM {embedding_table}")
                embedding_count = cur.fetchone()[0]
                
                # Embedding kapsama oranı
                coverage = (embedding_count / source_count * 100) if source_count > 0 else 0
                
                print(f"📦 {table.upper()}")
                print(f"   - Kaynak kayıt: {source_count:,}")
                print(f"   - Embedding: {embedding_count:,}")
                print(f"   - Kapsama: %{coverage:.1f}")
                
                # Telefon tablosu için detaylı kontrol
                if table == 'telephone':
                    print(f"   🔍 TELEFON TABLOSU DETAYLI KONTROL:")
                    
                    # İlk 5 embedding'i kontrol et
                    cur.execute(f"SELECT product_id, product_name, embedding FROM {embedding_table} LIMIT 5")
                    sample_embeddings = cur.fetchall()
                    
                    for i, (pid, pname, emb) in enumerate(sample_embeddings, 1):
                        emb_type = type(emb).__name__
                        emb_len = len(str(emb)) if emb else 0
                        print(f"     {i}. {pname[:30]}... - Tip: {emb_type}, Uzunluk: {emb_len}")
                
            else:
                print(f"❌ {table.upper()}")
                print(f"   - Kaynak kayıt: {source_count:,}")
                print(f"   - Embedding: YOK")
                print(f"   - Kapsama: %0")
        
        print("\n🎯 ÖZET:")
        print("-" * 30)
        total_source = sum(len([t for t in source_tables]))
        total_embedding = len(embedding_tables)
        print(f"Kaynak tablolar: {total_source}")
        print(f"Embedding tablolar: {total_embedding}")
        print(f"Eksik embedding'ler: {total_source - total_embedding}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Kontrol hatası: {e}")

if __name__ == "__main__":
    check_embeddings()