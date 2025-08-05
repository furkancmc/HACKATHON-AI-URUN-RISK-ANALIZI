import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import time
from typing import List, Dict, Any
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingCreator:
    def __init__(self, db_config: Dict[str, str], model_name: str = 'all-MiniLM-L6-v2'):
        """
        Embedding oluşturucu sınıfı
        
        Args:
            db_config: Veritabanı bağlantı bilgileri
            model_name: Kullanılacak embedding modeli
        """
        self.db_config = db_config
        self.model = SentenceTransformer(model_name)
        self.connection = None
        
    def connect_db(self):
        """Veritabanına bağlan"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("Veritabanına başarıyla bağlandı")
        except Exception as e:
            logger.error(f"Veritabanı bağlantı hatası: {e}")
            raise
    
    def close_db(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection:
            self.connection.close()
            logger.info("Veritabanı bağlantısı kapatıldı")
    
    def get_products_without_embeddings(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Embedding'i olmayan ürünleri getir
        
        Args:
            table_name: Tablo adı
            limit: Maksimum ürün sayısı
            
        Returns:
            Embedding'i olmayan ürünler listesi
        """
        try:
            cursor = self.connection.cursor()
            
            # Embedding'i olmayan ürünleri getir
            query = f"""
                SELECT id, title, description, brand, category, price, rating
                FROM {table_name}
                WHERE embedding IS NULL
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            products = cursor.fetchall()
            
            # Sonuçları dictionary formatına çevir
            columns = ['id', 'title', 'description', 'brand', 'category', 'price', 'rating']
            result = []
            
            for product in products:
                product_dict = dict(zip(columns, product))
                result.append(product_dict)
            
            cursor.close()
            logger.info(f"{len(result)} adet embedding'i olmayan ürün bulundu")
            return result
            
        except Exception as e:
            logger.error(f"Ürün getirme hatası: {e}")
            raise
    
    def create_text_for_embedding(self, product: Dict[str, Any]) -> str:
        """
        Ürün bilgilerinden embedding için metin oluştur
        
        Args:
            product: Ürün bilgileri
            
        Returns:
            Embedding için hazırlanmış metin
        """
        text_parts = []
        
        # Başlık
        if product.get('title'):
            text_parts.append(f"Ürün: {product['title']}")
        
        # Açıklama
        if product.get('description'):
            text_parts.append(f"Açıklama: {product['description']}")
        
        # Marka
        if product.get('brand'):
            text_parts.append(f"Marka: {product['brand']}")
        
        # Kategori
        if product.get('category'):
            text_parts.append(f"Kategori: {product['category']}")
        
        # Fiyat
        if product.get('price'):
            text_parts.append(f"Fiyat: {product['price']} TL")
        
        # Rating
        if product.get('rating'):
            text_parts.append(f"Değerlendirme: {product['rating']}/5")
        
        return " | ".join(text_parts)
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Metin için embedding oluştur
        
        Args:
            text: Embedding oluşturulacak metin
            
        Returns:
            Embedding vektörü
        """
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding oluşturma hatası: {e}")
            raise
    
    def update_product_embedding(self, table_name: str, product_id: int, embedding: List[float]):
        """
        Ürünün embedding'ini güncelle
        
        Args:
            table_name: Tablo adı
            product_id: Ürün ID'si
            embedding: Embedding vektörü
        """
        try:
            cursor = self.connection.cursor()
            
            query = f"""
                UPDATE {table_name}
                SET embedding = %s
                WHERE id = %s
            """
            
            cursor.execute(query, (embedding, product_id))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Ürün {product_id} için embedding güncellendi")
            
        except Exception as e:
            logger.error(f"Embedding güncelleme hatası: {e}")
            self.connection.rollback()
            raise
    
    def process_table(self, table_name: str, batch_size: int = 50):
        """
        Tablodaki eksik embedding'leri oluştur
        
        Args:
            table_name: İşlenecek tablo adı
            batch_size: Toplu işlem boyutu
        """
        try:
            logger.info(f"{table_name} tablosu için embedding oluşturma başlatılıyor...")
            
            total_processed = 0
            
            while True:
                # Embedding'i olmayan ürünleri getir
                products = self.get_products_without_embeddings(table_name, batch_size)
                
                if not products:
                    logger.info(f"Tüm embedding'ler tamamlandı. Toplam {total_processed} ürün işlendi.")
                    break
                
                logger.info(f"{len(products)} ürün işleniyor...")
                
                for product in products:
                    try:
                        # Embedding için metin oluştur
                        text = self.create_text_for_embedding(product)
                        
                        # Embedding oluştur
                        embedding = self.create_embedding(text)
                        
                        # Veritabanını güncelle
                        self.update_product_embedding(table_name, product['id'], embedding)
                        
                        total_processed += 1
                        
                        # Kısa bekleme (rate limiting için)
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Ürün {product.get('id')} işlenirken hata: {e}")
                        continue
                
                logger.info(f"Batch tamamlandı. Toplam {total_processed} ürün işlendi.")
                
        except Exception as e:
            logger.error(f"Tablo işleme hatası: {e}")
            raise

def load_db_config(config_file: str = 'db_config.txt') -> Dict[str, str]:
    """
    Veritabanı konfigürasyonunu yükle
    
    Args:
        config_file: Konfigürasyon dosyası
        
    Returns:
        Veritabanı bağlantı bilgileri
    """
    config = {}
    try:
        # Ana dizindeki db_config.txt dosyasını bul
        import os
        current_dir = os.getcwd()
        
        # Eğer backend klasöründeyse, bir üst dizine çık
        if os.path.basename(current_dir) == 'backend':
            config_path = os.path.join(os.path.dirname(current_dir), config_file)
        else:
            config_path = config_file
            
        with open(config_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
        
        # Port'u integer'a çevir
        if 'port' in config:
            config['port'] = int(config['port'])
            
        logger.info("Veritabanı konfigürasyonu yüklendi")
        return config
        
    except Exception as e:
        logger.error(f"Konfigürasyon yükleme hatası: {e}")
        raise

def main():
    """Ana fonksiyon"""
    try:
        # Veritabanı konfigürasyonunu yükle
        db_config = load_db_config()
        
        # Embedding oluşturucuyu başlat
        creator = EmbeddingCreator(db_config)
        
        # Veritabanına bağlan
        creator.connect_db()
        
        # Tabloları işle
        tables = ['telephone_products', 'computer_products', 'klima_products', 'kulaklık_products']
        
        for table in tables:
            try:
                creator.process_table(table)
            except Exception as e:
                logger.error(f"{table} tablosu işlenirken hata: {e}")
                continue
        
        logger.info("Tüm tablolar için embedding oluşturma tamamlandı!")
        
    except Exception as e:
        logger.error(f"Ana fonksiyon hatası: {e}")
    finally:
        if 'creator' in locals():
            creator.close_db()

if __name__ == "__main__":
    main() 