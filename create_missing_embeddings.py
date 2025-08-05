# create_missing_embeddings.py
import psycopg2
import json
from embedding_service import EmbeddingService
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingCreator:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.connection_params = {
            "host": "localhost",
            "port": 5434,
            "database": "urun_risk_analiz",
            "user": "postgres", 
            "password": "furkan"
        }
    
    def get_source_tables(self) -> List[str]:
        """Kaynak tabloları listele"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name NOT LIKE '%_embeddings'
                AND table_name NOT LIKE 'pg_%'
                AND table_name NOT LIKE 'information_schema%'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return tables
            
        except Exception as e:
            logger.error(f"❌ Tablo listesi alınamadı: {e}")
            return []
    
    def get_existing_embedding_tables(self) -> List[str]:
        """Mevcut embedding tablolarını listele"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%_embeddings'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return tables
            
        except Exception as e:
            logger.error(f"❌ Embedding tablo listesi alınamadı: {e}")
            return []
    
    def create_embedding_table(self, source_table: str) -> bool:
        """Embedding tablosu oluştur"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            embedding_table = f"{source_table}_embeddings"
            
            # Tablo oluştur
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {embedding_table} (
                    id SERIAL PRIMARY KEY,
                    product_id VARCHAR(255),
                    product_name TEXT,
                    combined_text TEXT,
                    embedding JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index oluştur
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{embedding_table}_embedding 
                ON {embedding_table} USING GIN (embedding)
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ {embedding_table} tablosu oluşturuldu")
            return True
            
        except Exception as e:
            logger.error(f"❌ {embedding_table} tablosu oluşturulamadı: {e}")
            return False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Tablo sütunlarını al"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return columns
            
        except Exception as e:
            logger.error(f"❌ {table_name} sütunları alınamadı: {e}")
            return []
    
    def create_combined_text(self, row_data: Dict[str, Any]) -> str:
        """Satır verilerinden combined text oluştur"""
        text_parts = []
        
        # Önemli alanları birleştir
        important_fields = ['name', 'title', 'product_name', 'brand', 'model', 'description', 'seller_description']
        
        for field in important_fields:
            if field in row_data and row_data[field]:
                text_parts.append(str(row_data[field]))
        
        # Diğer alanları da ekle (sayısal olmayan)
        for key, value in row_data.items():
            if key not in important_fields and value and not str(value).replace('.', '').replace(',', '').isdigit():
                text_parts.append(str(value))
        
        return ' '.join(text_parts)
    
    def populate_embeddings(self, source_table: str, limit: int = 100) -> bool:
        """Embedding tablosunu doldur"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            embedding_table = f"{source_table}_embeddings"
            
            # Kaynak tablo verilerini al
            columns = self.get_table_columns(source_table)
            if not columns:
                return False
            
            columns_sql = ', '.join(columns)
            cur.execute(f"SELECT {columns_sql} FROM {source_table} LIMIT %s", (limit,))
            
            rows = cur.fetchall()
            logger.info(f"📊 {source_table}: {len(rows)} satır işlenecek")
            
            # Her satır için embedding oluştur
            for i, row in enumerate(rows):
                try:
                    # Satır verilerini dict'e çevir
                    row_data = dict(zip(columns, row))
                    
                    # ID alanını bul
                    product_id = row_data.get('id') or row_data.get('product_id') or str(i)
                    
                    # Product name alanını bul
                    product_name = (
                        row_data.get('name') or 
                        row_data.get('title') or 
                        row_data.get('product_name') or 
                        f"Ürün {i+1}"
                    )
                    
                    # Combined text oluştur
                    combined_text = self.create_combined_text(row_data)
                    
                    if not combined_text.strip():
                        combined_text = f"{product_name} ürün"
                    
                    # Embedding oluştur
                    embedding = self.embedding_service.create_embedding(combined_text)
                    
                    if embedding:
                        # Embedding tablosuna ekle (conflict olmadan)
                        cur.execute(f"""
                            INSERT INTO {embedding_table} 
                            (product_id, product_name, combined_text, embedding)
                            VALUES (%s, %s, %s, %s)
                        """, (product_id, product_name, combined_text, json.dumps(embedding)))
                        
                        if (i + 1) % 10 == 0:
                            logger.info(f"📝 {source_table}: {i+1}/{len(rows)} embedding oluşturuldu")
                
                except Exception as e:
                    logger.warning(f"⚠️ Satır {i} embedding hatası: {e}")
                    continue
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ {embedding_table} tablosu dolduruldu")
            return True
            
        except Exception as e:
            logger.error(f"❌ {source_table} embedding doldurma hatası: {e}")
            return False
    
    def create_missing_embeddings(self):
        """Eksik embedding tablolarını oluştur"""
        source_tables = self.get_source_tables()
        existing_embedding_tables = self.get_existing_embedding_tables()
        
        logger.info(f"📋 Kaynak tablolar: {source_tables}")
        logger.info(f"📋 Mevcut embedding tabloları: {existing_embedding_tables}")
        
        for source_table in source_tables:
            embedding_table = f"{source_table}_embeddings"
            
            if embedding_table not in existing_embedding_tables:
                logger.info(f"🔨 {embedding_table} tablosu oluşturuluyor...")
                
                # Tablo oluştur
                if self.create_embedding_table(source_table):
                    # Embedding'leri doldur
                    self.populate_embeddings(source_table, limit=200)
            else:
                logger.info(f"✅ {embedding_table} zaten mevcut")

def main():
    creator = EmbeddingCreator()
    creator.create_missing_embeddings()

if __name__ == "__main__":
    main() 