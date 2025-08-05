# run_embedding_creation.py
import sys
import os
import json
import psycopg2
from embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_json_to_postgres():
    """JSON dosyalarını PostgreSQL'e aktar"""
    
    connection_params = {
        "host": "localhost",
        "port": 5434,
        "database": "urun_risk_analiz",
        "user": "postgres", 
        "password": "furkan"
    }
    
    # JSON dosyaları
    json_files = {
        'telephone': 'telephone_sonnnn.json',
        'kulaklik': 'kulaklık_sonnnn.json',
        'computer': 'computer_sonnnn.json'
    }
    
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        
        for table_name, json_file in json_files.items():
            if not os.path.exists(json_file):
                logger.warning(f"❌ {json_file} dosyası bulunamadı")
                continue
                
            logger.info(f"📥 {json_file} dosyası işleniyor...")
            
            # JSON dosyasını oku
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.error(f"❌ {json_file} geçerli bir liste formatında değil")
                continue
            
            logger.info(f"📊 {len(data)} kayıt bulundu")
            
            # Tablo oluştur
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    price DECIMAL,
                    rating DECIMAL,
                    brand TEXT,
                    model TEXT,
                    description TEXT,
                    seller_description TEXT,
                    features TEXT,
                    url TEXT,
                    image_url TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Verileri ekle
            successful_inserts = 0
            for i, item in enumerate(data):
                try:
                    # Veri temizleme ve mapping
                    name = item.get('name') or item.get('title') or f"Ürün {i+1}"
                    price = float(item.get('price', 0)) if item.get('price') else 0
                    rating = float(item.get('rating', 0)) if item.get('rating') else 0
                    brand = item.get('brand', '')
                    model = item.get('model', '')
                    description = item.get('description', '')
                    seller_description = item.get('seller_description', '')
                    features = json.dumps(item.get('features', []), ensure_ascii=False) if item.get('features') else ''
                    url = item.get('url', '')
                    image_url = item.get('image_url', '')
                    category = table_name
                    
                    cur.execute(f"""
                        INSERT INTO {table_name} 
                        (name, price, rating, brand, model, description, seller_description, features, url, image_url, category)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (name, price, rating, brand, model, description, seller_description, features, url, image_url, category))
                    
                    successful_inserts += 1
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"📝 {table_name}: {i+1}/{len(data)} kayıt işlendi")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {table_name} kayıt {i} hatası: {e}")
                    continue
            
            conn.commit()
            logger.info(f"✅ {table_name}: {successful_inserts} kayıt başarıyla eklendi")
        
        cur.close()
        conn.close()
        logger.info("✅ Tüm JSON dosyaları başarıyla aktarıldı")
        
    except Exception as e:
        logger.error(f"❌ JSON aktarım hatası: {e}")

def create_embeddings_for_tables():
    """Tablolar için embedding'leri oluştur"""
    
    from create_missing_embeddings import EmbeddingCreator
    
    try:
        creator = EmbeddingCreator()
        creator.create_missing_embeddings()
        logger.info("✅ Embedding oluşturma işlemi tamamlandı")
    except Exception as e:
        logger.error(f"❌ Embedding oluşturma hatası: {e}")

def main():
    """Ana fonksiyon"""
    
    logger.info("🚀 Telefon ve Kulaklık Tabloları Aktarım İşlemi Başlıyor...")
    
    # 1. JSON dosyalarını PostgreSQL'e aktar
    logger.info("📥 1. Adım: JSON dosyalarını veritabanına aktarma")
    import_json_to_postgres()
    
    # 2. Embedding'leri oluştur
    logger.info("🔨 2. Adım: Embedding'leri oluşturma")
    create_embeddings_for_tables()
    
    logger.info("🎉 İşlem tamamlandı!")

if __name__ == "__main__":
    main()