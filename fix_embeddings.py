# fix_embeddings.py
import psycopg2
import json
from embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_embeddings():
    """Embedding sorunlarını düzelt"""
    
    connection_params = {
        "host": "localhost",
        "port": 5434,
        "database": "urun_risk_analiz",
        "user": "postgres", 
        "password": "furkan"
    }
    
    embedding_service = EmbeddingService()
    
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        
        print("🔧 EMBEDDİNG SORUNLARI DÜZELTİLİYOR...")
        print("=" * 50)
        
        # 1. Sorunlu telephone_embeddings tablosunu temizle
        print("🗑️ Sorunlu telephone_embeddings temizleniyor...")
        try:
            cur.execute("DROP TABLE IF EXISTS telephone_embeddings CASCADE")
            conn.commit()
            print("✅ telephone_embeddings silindi")
        except Exception as e:
            print(f"⚠️ telephone_embeddings silme hatası: {e}")
            conn.rollback()
        
        # 2. Eksik embedding'leri tamamla
        tables_to_fix = [
            ('kulaklik', 'kulaklik_embeddings'),
            ('computer', 'computer_embeddings')
        ]
        
        for source_table, embedding_table in tables_to_fix:
            print(f"\n🔨 {source_table} tablosu düzeltiliyor...")
            
            # Mevcut embedding sayısını kontrol et
            cur.execute(f"SELECT COUNT(*) FROM {embedding_table}")
            current_embeddings = cur.fetchone()[0]
            
            # Toplam ürün sayısını kontrol et
            cur.execute(f"SELECT COUNT(*) FROM {source_table}")
            total_products = cur.fetchone()[0]
            
            print(f"📊 Mevcut: {current_embeddings}, Toplam: {total_products}")
            
            if current_embeddings < total_products:
                # Eksik embedding'leri bul
                cur.execute(f"""
                    SELECT s.id, s.name, s.brand, s.model, s.description
                    FROM {source_table} s
                    LEFT JOIN {embedding_table} e ON s.id::text = e.product_id
                    WHERE e.product_id IS NULL
                    LIMIT {total_products - current_embeddings}
                """)
                
                missing_products = cur.fetchall()
                print(f"🔍 {len(missing_products)} eksik embedding bulundu")
                
                # Eksik embedding'leri oluştur
                for i, (pid, name, brand, model, description) in enumerate(missing_products):
                    try:
                        # Combined text oluştur
                        text_parts = []
                        if name: text_parts.append(str(name))
                        if brand: text_parts.append(str(brand))
                        if model: text_parts.append(str(model))
                        if description: text_parts.append(str(description))
                        
                        combined_text = ' '.join(text_parts) or f"Ürün {pid}"
                        
                        # Embedding oluştur
                        embedding = embedding_service.create_embedding(combined_text)
                        
                        if embedding:
                            # Embedding tablosuna ekle
                            cur.execute(f"""
                                INSERT INTO {embedding_table} 
                                (product_id, product_name, combined_text, embedding)
                                VALUES (%s, %s, %s, %s)
                            """, (str(pid), name or f"Ürün {pid}", combined_text, json.dumps(embedding)))
                            
                            if (i + 1) % 10 == 0:
                                print(f"📝 {i+1}/{len(missing_products)} embedding oluşturuldu")
                                conn.commit()
                    
                    except Exception as e:
                        print(f"⚠️ Embedding {i} hatası: {e}")
                        continue
                
                conn.commit()
                print(f"✅ {source_table} tablosu tamamlandı")
            else:
                print(f"✅ {source_table} zaten tamamlanmış")
        
        # 3. Telefon tablolarını birleştir
        print(f"\n📱 Telefon tablolarını kontrol et...")
        
        # telefon_urunleri tablosunu kontrol et
        cur.execute("SELECT COUNT(*) FROM telefon_urunleri")
        telefon_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM telefon_urunleri_embeddings")
        telefon_embedding_count = cur.fetchone()[0]
        
        print(f"📊 telefon_urunleri: {telefon_count} ürün, {telefon_embedding_count} embedding")
        
        # telephone tablosu var mı kontrol et
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'telephone'
        """)
        
        telephone_exists = cur.fetchone()[0] > 0
        
        if telephone_exists:
            cur.execute("SELECT COUNT(*) FROM telephone")
            telephone_count = cur.fetchone()[0]
            print(f"📊 telephone: {telephone_count} ürün")
            
            # telephone için embedding oluştur
            if telephone_count > 0:
                print("🔨 telephone tablosu için embedding oluşturuluyor...")
                
                # telephone_embeddings tablosunu oluştur
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS telephone_embeddings (
                        id SERIAL PRIMARY KEY,
                        product_id VARCHAR(255),
                        product_name TEXT,
                        combined_text TEXT,
                        embedding JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # telephone verilerini al
                cur.execute("""
                    SELECT id, name, brand, model, description
                    FROM telephone
                    LIMIT 200
                """)
                
                telephone_products = cur.fetchall()
                
                for i, (pid, name, brand, model, description) in enumerate(telephone_products):
                    try:
                        # Combined text oluştur
                        text_parts = []
                        if name: text_parts.append(str(name))
                        if brand: text_parts.append(str(brand))
                        if model: text_parts.append(str(model))
                        if description: text_parts.append(str(description))
                        
                        combined_text = ' '.join(text_parts) or f"Telefon {pid}"
                        
                        # Embedding oluştur
                        embedding = embedding_service.create_embedding(combined_text)
                        
                        if embedding:
                            # Embedding tablosuna ekle
                            cur.execute(f"""
                                INSERT INTO telephone_embeddings 
                                (product_id, product_name, combined_text, embedding)
                                VALUES (%s, %s, %s, %s)
                            """, (str(pid), name or f"Telefon {pid}", combined_text, json.dumps(embedding)))
                            
                            if (i + 1) % 10 == 0:
                                print(f"📝 {i+1}/{len(telephone_products)} telefon embedding oluşturuldu")
                                conn.commit()
                    
                    except Exception as e:
                        print(f"⚠️ Telefon embedding {i} hatası: {e}")
                        continue
                
                conn.commit()
                print("✅ telephone_embeddings tablosu oluşturuldu")
        
        cur.close()
        conn.close()
        
        print("\n🎉 EMBEDDİNG DÜZELTMELERİ TAMAMLANDI!")
        
    except Exception as e:
        logger.error(f"❌ Düzeltme hatası: {e}")

if __name__ == "__main__":
    fix_embeddings()