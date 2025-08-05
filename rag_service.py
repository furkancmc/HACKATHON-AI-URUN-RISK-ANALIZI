# rag_service.py
import psycopg2
import logging
from typing import List, Dict, Any, Optional
from embedding_service import EmbeddingService
import numpy as np
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cosine_similarity_np(a, b):
    """NumPy ile cosine similarity hesapla"""
    try:
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        
        # Sıfır vektör kontrolü
        if np.all(a == 0) or np.all(b == 0):
            return 0.0
            
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    except Exception as e:
        logger.warning(f"Similarity hesaplama hatası: {e}")
        return 0.0

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        # Veritabanı konfigürasyonunu yükle
        try:
            from create_missing_embeddings import load_db_config
            db_config = load_db_config()
            self.connection_params = db_config
        except Exception as e:
            logger.error(f"Veritabanı konfigürasyonu yüklenemedi: {e}")
            # Fallback konfigürasyon
            self.connection_params = {
                "host": "localhost",
                "port": 5432,
                "database": "ai_seller_analysis",
                "user": "postgres", 
                "password": "your_password"
            }
    
    def get_available_tables(self) -> List[str]:
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
            
            logger.info(f"📋 Bulunan embedding tabloları: {tables}")
            return tables
            
        except Exception as e:
            logger.error(f"❌ Tablo listesi alınamadı: {e}")
            return []
    
    def parse_embedding(self, embedding_data) -> Optional[List[float]]:
        """Embedding verisini parse et"""
        try:
            if embedding_data is None:
                return None
                
            # String ise JSON parse et
            if isinstance(embedding_data, str):
                try:
                    parsed = json.loads(embedding_data)
                    if isinstance(parsed, list):
                        return [float(x) for x in parsed]
                    else:
                        logger.warning(f"JSON string list değil: {type(parsed)}")
                        return None
                except json.JSONDecodeError:
                    logger.warning("JSON parse hatası")
                    return None
            
            # List/array ise direkt kullan
            elif hasattr(embedding_data, '__iter__') and not isinstance(embedding_data, str):
                return [float(x) for x in embedding_data]
            
            # Diğer durumlar
            else:
                logger.warning(f"Bilinmeyen embedding formatı: {type(embedding_data)}")
                return None
                
        except Exception as e:
            logger.warning(f"Embedding parse hatası: {e}")
            return None
    
    def search_products(self, query: str, table_names: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ürünleri arama - Text-based embedding ile
        
        Args:
            query: Arama sorgusu
            table_names: Aranacak tablolar (None ise tüm tablolar)
            limit: Maksimum sonuç sayısı
        """
        try:
            logger.info(f"🔍 Arama başlatılıyor: '{query}'")
            
            # Query embedding'ini oluştur
            query_embedding = self.embedding_service.create_embedding(query)
            if not query_embedding:
                logger.error("❌ Query embedding oluşturulamadı")
                return []
            
            logger.info(f"✅ Query embedding oluşturuldu (boyut: {len(query_embedding)})")
            
            # Eğer tablo belirtilmemişse tüm tabloları kullan
            if table_names is None:
                table_names = self.get_available_tables()
            
            if not table_names:
                logger.error("❌ Hiç embedding tablosu bulunamadı")
                return []
            
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            all_results = []
            
            # Her tablo için arama yap
            for table_name in table_names:
                try:
                    logger.info(f"🔍 {table_name} aranıyor...")
                    
                    # Embedding'leri al
                    cur.execute(f"""
                        SELECT 
                            product_id,
                            product_name,
                            combined_text,
                            embedding
                        FROM {table_name}
                        WHERE embedding IS NOT NULL
                        LIMIT 200
                    """)
                    
                    results = cur.fetchall()
                    logger.info(f"📊 {table_name}: {len(results)} kayıt bulundu")
                    
                    # Her sonuç için similarity hesapla
                    for result in results:
                        try:
                            product_id, product_name, combined_text, embedding_vector = result
                            
                            # Embedding'i parse et
                            parsed_embedding = self.parse_embedding(embedding_vector)
                            if not parsed_embedding:
                                continue
                            
                            # Similarity hesapla
                            similarity = cosine_similarity_np(query_embedding, parsed_embedding)
                            
                            if similarity > 0.05:  # Düşük threshold
                                all_results.append({
                                    'product_id': product_id,
                                    'product_name': product_name, 
                                    'combined_text': combined_text,
                                    'similarity': float(similarity),
                                    'source_table': table_name.replace('_embeddings', '')
                                })
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Similarity hesaplama hatası: {e}")
                            continue
                        
                except Exception as e:
                    logger.warning(f"⚠️ {table_name} arama hatası: {e}")
                    continue
            
            # Sonuçları benzerlik skoruna göre sırala
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            cur.close()
            conn.close()
            
            logger.info(f"✅ {len(all_results)} sonuç bulundu")
            
            # Limit uygula
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Arama hatası: {e}")
            return []
    
    def get_product_details(self, product_id: str, source_table: str) -> Optional[Dict[str, Any]]:
        """Ürün detaylarını getir - TÜM veriler dahil"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            # Tablo sütunlarını al
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{source_table}'
                ORDER BY ordinal_position
            """)
            
            columns = [row[0] for row in cur.fetchall()]
            
            # Ürün detaylarını al - TÜM SÜTUNLAR
            columns_sql = ', '.join(columns)
            # Tablo yapısına göre doğru ID sütununu kullan
            id_column = 'product_id' if 'product_id' in columns else 'id'
            cur.execute(f"SELECT {columns_sql} FROM {source_table} WHERE {id_column} = %s", (product_id,))
            
            result = cur.fetchone()
            
            if result:
                product_data = dict(zip(columns, result))
                
                # Risk analizi için ek hesaplamalar
                product_data = self._calculate_risk_metrics(product_data, source_table)
                
                cur.close()
                conn.close()
                return product_data
            
            # Kaynak tabloda bulunamazsa embedding tablosundan al
            embedding_table = f"{source_table}_embeddings"
            try:
                logger.info(f"🔍 Embedding tablosunda aranıyor: {embedding_table}")
                
                cur.execute(f"""
                    SELECT 
                        product_id,
                        product_name,
                        combined_text,
                        created_at
                    FROM {embedding_table}
                    WHERE product_id = %s
                """, (product_id,))
                
                result = cur.fetchone()
                
                if result:
                    product_data = {
                        'product_id': result[0],
                        'name': result[1],
                        'description': result[2],
                        'created_at': result[3],
                        'source': 'embedding_table'
                    }
                    
                    # Basit risk analizi ekle
                    product_data['risk_analysis'] = {
                        'overall_risk': 5.0,
                        'price_risk': 5.0,
                        'rating_risk': 5.0,
                        'competition_risk': 5.0,
                        'risk_level': 'Orta',
                        'seller_recommendation': 'Embedding tablosundan veri. Daha detaylı analiz için kaynak tabloyla eşleştirin.'
                    }
                    
                    cur.close()
                    conn.close()
                    return product_data
                    
            except Exception as e:
                logger.warning(f"⚠️ Embedding tablosunda da bulunamadı: {e}")
            
            cur.close()
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"❌ Ürün detay hatası: {e}")
            return None
    
    def _calculate_risk_metrics(self, product_data: Dict[str, Any], source_table: str) -> Dict[str, Any]:
        """Satıcı için risk metriklerini hesapla"""
        try:
            # Fiyat analizi
            price = float(product_data.get('price', 0))
            
            # Rating analizi  
            rating = float(product_data.get('rating', 0))
            
            # Risk skorları hesapla (1-10 arası, 10 en riskli)
            price_risk = self._calculate_price_risk(price, source_table)
            rating_risk = self._calculate_rating_risk(rating)
            competition_risk = self._calculate_competition_risk(product_data, source_table)
            
            # Genel risk skoru
            overall_risk = (price_risk + rating_risk + competition_risk) / 3
            
            # Risk analizini ekle
            product_data['risk_analysis'] = {
                'price_risk': price_risk,
                'rating_risk': rating_risk, 
                'competition_risk': competition_risk,
                'overall_risk': round(overall_risk, 2),
                'risk_level': self._get_risk_level(overall_risk),
                'seller_recommendation': self._get_seller_recommendation(overall_risk, product_data)
            }
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Risk metrik hesaplama hatası: {e}")
            return product_data
    
    def _calculate_price_risk(self, price: float, source_table: str) -> float:
        """Fiyat risk analizi"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            # Aynı kategorideki ortalama fiyat
            cur.execute(f"""
                SELECT AVG(price), MIN(price), MAX(price)
                FROM {source_table} 
                WHERE price > 0
            """)
            
            result = cur.fetchone()
            if result and result[0]:
                avg_price, min_price, max_price = result
                
                # Fiyat pozisyonuna göre risk
                if price > avg_price * 1.5:
                    return 8.0  # Yüksek fiyat riski
                elif price > avg_price * 1.2:
                    return 6.0  # Orta-yüksek risk
                elif price < avg_price * 0.8:
                    return 4.0  # Düşük fiyat riski
                else:
                    return 3.0  # Optimal fiyat
            
            cur.close()
            conn.close()
            return 5.0  # Varsayılan
            
        except Exception as e:
            logger.warning(f"Fiyat risk hesaplama hatası: {e}")
            return 5.0
    
    def _calculate_rating_risk(self, rating: float) -> float:
        """Rating risk analizi"""
        if rating >= 4.5:
            return 2.0  # Düşük risk
        elif rating >= 4.0:
            return 3.0  # Düşük-orta risk
        elif rating >= 3.5:
            return 5.0  # Orta risk
        elif rating >= 3.0:
            return 7.0  # Yüksek risk
        else:
            return 9.0  # Çok yüksek risk
    
    def _calculate_competition_risk(self, product_data: Dict[str, Any], source_table: str) -> float:
        """Rekabet risk analizi"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            brand = product_data.get('brand', '')
            
            # Aynı markadan kaç ürün var
            cur.execute(f"""
                SELECT COUNT(*) 
                FROM {source_table} 
                WHERE brand ILIKE %s
            """, (f"%{brand}%",))
            
            brand_count = cur.fetchone()[0]
            
            # Rekabet yoğunluğu
            if brand_count > 50:
                return 8.0  # Yüksek rekabet
            elif brand_count > 20:
                return 6.0  # Orta rekabet
            elif brand_count > 10:
                return 4.0  # Düşük rekabet
            else:
                return 2.0  # Çok düşük rekabet
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Rekabet risk hesaplama hatası: {e}")
            return 5.0
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Risk seviyesi belirle"""
        if risk_score >= 7:
            return "YÜKSEK RİSK"
        elif risk_score >= 5:
            return "ORTA RİSK"
        elif risk_score >= 3:
            return "DÜŞÜK RİSK"
        else:
            return "ÇOK DÜŞÜK RİSK"
    
    def _get_seller_recommendation(self, risk_score: float, product_data: Dict[str, Any]) -> str:
        """Satıcı önerisi"""
        if risk_score >= 7:
            return "SATIŞ ÖNERİLMEZ - Yüksek risk faktörleri mevcut"
        elif risk_score >= 5:
            return "DİKKATLİ SATIŞ - Risk faktörlerini değerlendirin"
        elif risk_score >= 3:
            return "SATIŞ YAPILABİLİR - Makul risk seviyesi"
        else:
            return "ÖNERİLEN ÜRÜN - Düşük risk, yüksek potansiyel"
    
    def search_with_filters(self, query: str, filters: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Filtreli arama
        
        Args:
            query: Arama sorgusu
            filters: Filtreler (örn: {'price_min': 1000, 'brand': 'Samsung'})
            limit: Maksimum sonuç sayısı
        """
        
        # Önce basic arama yap
        search_results = self.search_products(query, limit=limit*2)  # Daha fazla sonuç al
        
        if not search_results:
            logger.warning("❌ Hiç arama sonucu bulunamadı")
            return []
        
        if not filters:
            # Filtre yoksa ürün detaylarını ekle
            for result in search_results:
                try:
                    product_details = self.get_product_details(
                        result['product_id'], 
                        result['source_table']
                    )
                    if product_details:
                        result['product_details'] = product_details
                except Exception as e:
                    logger.warning(f"Ürün detay hatası: {e}")
            
            return search_results[:limit]
        
        filtered_results = []
        
        for result in search_results:
            try:
                # Ürün detaylarını al
                product_details = self.get_product_details(
                    result['product_id'], 
                    result['source_table']
                )
                
                if not product_details:
                    continue
                
                # Filtreleri uygula
                passes_filters = True
                
                for filter_key, filter_value in filters.items():
                    if filter_key == 'price_min' and 'price' in product_details:
                        try:
                            price = float(product_details['price'] or 0)
                            if price < filter_value:
                                passes_filters = False
                                break
                        except (ValueError, TypeError):
                            continue
                    
                    elif filter_key == 'price_max' and 'price' in product_details:
                        try:
                            price = float(product_details['price'] or 0)
                            if price > filter_value:
                                passes_filters = False
                                break
                        except (ValueError, TypeError):
                            continue
                    
                    elif filter_key == 'brands' and 'brand' in product_details:
                        # Çoklu marka filtresi
                        if isinstance(filter_value, list):
                            brand_match = any(
                                str(product_details['brand']).lower() == str(brand).lower() 
                                for brand in filter_value
                            )
                            if not brand_match:
                                passes_filters = False
                                break
                        else:
                            # Tek marka filtresi
                            if str(product_details['brand']).lower() != str(filter_value).lower():
                                passes_filters = False
                                break
                    
                    elif filter_key == 'rating_min' and 'rating' in product_details:
                        try:
                            rating = float(product_details['rating'] or 0)
                            if rating < filter_value:
                                passes_filters = False
                                break
                        except (ValueError, TypeError):
                            continue
                
                if passes_filters:
                    result['product_details'] = product_details
                    filtered_results.append(result)
                    
                if len(filtered_results) >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️ Filtre uygulama hatası: {e}")
                continue
        
        logger.info(f"✅ Filtreli arama: {len(filtered_results)} sonuç")
        return filtered_results
    
    def get_table_stats(self) -> Dict[str, Dict[str, Any]]:
        """Tablo istatistiklerini getir - SADECE mevcut embedding tabloları için"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            stats = {}
            embedding_tables = self.get_available_tables()
            
            logger.info(f"📊 İstatistik hesaplanacak embedding tabloları: {embedding_tables}")
            
            for table_name in embedding_tables:
                source_table = table_name.replace('_embeddings', '')
                
                try:
                    # Önce kaynak tablonun var olduğunu kontrol et
                    cur.execute(f"""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_name = '{source_table}' 
                        AND table_schema = 'public'
                    """)
                    
                    table_exists = cur.fetchone()[0] > 0
                    
                    if not table_exists:
                        logger.warning(f"⚠️ Kaynak tablo bulunamadı: {source_table}")
                        continue
                    
                    # Embedding sayısı
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    embedding_count = cur.fetchone()[0]
                    
                    # Orjinal tablo istatistikleri
                    cur.execute(f"""
                        SELECT 
                            COUNT(*) as total_products,
                            AVG(CASE WHEN price > 0 THEN price END) as avg_price,
                            AVG(CASE WHEN rating > 0 THEN rating END) as avg_rating
                        FROM {source_table}
                    """)
                    
                    result = cur.fetchone()
                    
                    if result and result[0] > 0:  # Sadece veri olan tabloları dahil et
                        stats[source_table] = {
                            'total_products': result[0],
                            'embeddings_count': embedding_count,
                            'avg_price': float(result[1] or 0),
                            'avg_rating': float(result[2] or 0),
                            'embedding_coverage': round((embedding_count / result[0]) * 100, 2) if result[0] > 0 else 0
                        }
                        
                        logger.info(f"✅ {source_table}: {result[0]} ürün, {embedding_count} embedding")
                    
                except Exception as e:
                    logger.warning(f"⚠️ {table_name} istatistik hatası: {e}")
                    continue
            
            cur.close()
            conn.close()
            
            logger.info(f"📊 Toplam aktif tablo sayısı: {len(stats)}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ İstatistik hatası: {e}")
            return {}

    def get_all_brands(self) -> List[str]:
        """Tüm tablolardan benzersiz markaları getir"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            all_brands = set()
            tables = self.get_available_tables()
            
            for table_name in tables:
                base_table_name = table_name.replace('_embeddings', '')
                
                try:
                    # Her tablodan brand sütununu al
                    cur.execute(f"""
                        SELECT DISTINCT brand 
                        FROM {base_table_name} 
                        WHERE brand IS NOT NULL 
                        AND brand IS NOT DISTINCT FROM '' 
                        AND brand != 'null'
                        ORDER BY brand
                    """)
                    
                    brands = [row[0] for row in cur.fetchall()]
                    all_brands.update(brands)
                    
                except Exception as e:
                    logger.warning(f"❌ {base_table_name} tablosundan markalar alınamadı: {e}")
                    continue
            
            cur.close()
            conn.close()
            
            # Benzersiz markaları sırala
            sorted_brands = sorted(list(all_brands))
            logger.info(f"🏷️ Bulunan markalar: {len(sorted_brands)} adet")
            
            return sorted_brands
            
        except Exception as e:
            logger.error(f"❌ Marka listesi alınamadı: {e}")
            return []

    def get_sales_data_for_dashboard(self) -> List[Dict[str, Any]]:
        """Dashboard için satış verilerini getir"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            sales_data = []
            tables = self.get_available_tables()
            
            for table_name in tables:
                base_table_name = table_name.replace('_embeddings', '')
                
                try:
                    # Her tablodan satış verilerini al
                    cur.execute(f"""
                        SELECT 
                            name,
                            brand,
                            price,
                            rating,
                            seller_name,
                            stock_status,
                            availability
                        FROM {base_table_name} 
                        WHERE price IS NOT NULL 
                        AND price > 0
                        ORDER BY price DESC
                        LIMIT 10
                    """)
                    
                    products = cur.fetchall()
                    
                    for product in products:
                        sales_data.append({
                            'product_name': product[0] or 'Bilinmeyen Ürün',
                            'brand': product[1] or 'Bilinmeyen Marka',
                            'price': float(product[2]) if product[2] else 0,
                            'rating': float(product[3]) if product[3] else 0,
                            'seller': product[4] or 'Bilinmeyen Satıcı',
                            'stock_status': product[5] or 'Bilinmeyen',
                            'availability': product[6] or 'Bilinmeyen',
                            'source_table': base_table_name,
                            'progress': min(100, max(0, float(product[3] or 0) * 20)),  # Rating * 20
                            'risk_score': self._calculate_quick_risk_score(float(product[2] or 0), float(product[3] or 0))
                        })
                    
                except Exception as e:
                    logger.warning(f"❌ {base_table_name} tablosundan satış verileri alınamadı: {e}")
                    continue
            
            cur.close()
            conn.close()
            
            # Fiyata göre sırala
            sales_data.sort(key=lambda x: x['price'], reverse=True)
            
            logger.info(f"📊 Dashboard için {len(sales_data)} satış verisi hazırlandı")
            return sales_data
            
        except Exception as e:
            logger.error(f"❌ Satış verileri alınamadı: {e}")
            return []

    def _calculate_quick_risk_score(self, price: float, rating: float) -> float:
        """Hızlı risk skoru hesapla"""
        try:
            # Fiyat riski (yüksek fiyat = yüksek risk)
            price_risk = min(10, price / 1000) if price > 0 else 5
            
            # Rating riski (düşük rating = yüksek risk)
            rating_risk = max(0, 10 - (rating * 2)) if rating > 0 else 10
            
            # Ortalama risk
            overall_risk = (price_risk + rating_risk) / 2
            
            return round(overall_risk, 1)
            
        except Exception as e:
            logger.warning(f"Risk skoru hesaplama hatası: {e}")
            return 5.0

# Test fonksiyonu
def test_rag_service():
    """RAG servisini test et"""
    
    rag = RAGService()
    
    print("🔍 RAG Servisi Test Ediliyor...")
    
    # Mevcut tabloları listele
    tables = rag.get_available_tables()
    print(f"📋 Mevcut embedding tabloları: {tables}")
    
    # İstatistikleri göster
    stats = rag.get_table_stats()
    print("\n📊 Tablo İstatistikleri:")
    for table_name, table_stats in stats.items():
        print(f"  📦 {table_name}:")
        print(f"    - Toplam ürün: {table_stats['total_products']}")
        print(f"    - Embedding sayısı: {table_stats['embeddings_count']}")
        print(f"    - Embedding kapsama: %{table_stats['embedding_coverage']}")
    
    # Test araması
    test_queries = [
        "Samsung klima",
        "enerji verimli soğutucu",
        "18000 BTU inverter"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test sorgusu: '{query}'")
        results = rag.search_products(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['product_name']} (Benzerlik: {result['similarity']:.3f})")
                print(f"     Tablo: {result['source_table']}")
        else:
            print("  ❌ Sonuç bulunamadı")

if __name__ == "__main__":
    test_rag_service()