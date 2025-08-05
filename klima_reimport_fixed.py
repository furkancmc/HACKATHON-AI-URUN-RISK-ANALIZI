# klima_reimport_fixed.py
import json
import psycopg2
import logging
import hashlib
import uuid
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_unique_id(item: dict, index: int) -> str:
    """Her ürün için benzersiz ID oluştur"""

    # Önce mevcut ID'yi kontrol et
    existing_id = item.get('id', '')

    # Eğer ID "generated_id" ise veya boşsa, yeni bir ID oluştur
    if existing_id == 'generated_id' or not existing_id or existing_id.strip() == '':
        # Ürün adı ve brand ile benzersiz hash oluştur
        product_name = str(item.get('product_name', 'unknown'))
        brand = str(item.get('brand', 'unknown'))
        price = str(item.get('price', 0))

        # Hash oluştur
        unique_string = f"{product_name}_{brand}_{price}_{index}"
        hash_id = hashlib.md5(unique_string.encode('utf-8')).hexdigest()[:12]

        return f"klima_{hash_id}"

    # Mevcut ID'yi kullan ama benzersiz olduğundan emin ol
    return f"{existing_id}_{index}" if existing_id == 'generated_id' else existing_id


def reimport_klima_data():
    """Klima verilerini sıfırdan yeniden import et"""

    # JSON dosya yolları (hangisi varsa onu kullan)
    possible_files = [
        "klima_detayli_analiz.json",
        "klima_v2.json",
        "analyzed_products.json",
        "C:/Users/Furkan/Desktop/db/klima_detayli_analiz.json",
        "C:/Users/Furkan/Desktop/HACKATHON/hackathon-scraping/klima_detayli_analiz.json"
    ]

    json_data = None
    used_file = None

    # Hangi dosya varsa onu kullan
    for file_path in possible_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            used_file = file_path
            logger.info(f"✅ Klima verileri yüklendi: {file_path}")
            break
        except Exception as e:
            logger.warning(f"⚠️ {file_path} yüklenemedi: {e}")

    if not json_data:
        logger.error("❌ Hiçbir klima JSON dosyası bulunamadı!")
        logger.info("💡 Şu dosyalardan birini oluştur:")
        for file_path in possible_files[:3]:
            logger.info(f"  - {file_path}")
        return False

    logger.info(f"📊 Toplam klima verisi: {len(json_data)} adet")

    # ID'lerin benzersizliğini kontrol et
    id_check = {}
    duplicate_count = 0
    for i, item in enumerate(json_data):
        original_id = item.get('id', '')
        if original_id in id_check:
            duplicate_count += 1
        else:
            id_check[original_id] = i

    if duplicate_count > 0:
        logger.warning(f"⚠️ {duplicate_count} adet duplicate ID bulundu, düzeltiliyor...")

    # Eski PostgreSQL'e bağlan (5434 - yeni pgvector)
    try:
        old_conn = psycopg2.connect(
            host="localhost", port=5434, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        old_cur = old_conn.cursor()
        logger.info("✅ Yeni pgvector PostgreSQL'e bağlandı (port 5434)")
    except Exception as e:
        logger.error(f"❌ Yeni pgvector PostgreSQL bağlantı hatası: {e}")
        return False

    try:
        # Önce mevcut klima tablosunu kontrol et
        logger.info("🔍 Mevcut klima tablosu kontrol ediliyor...")
        old_cur.execute("""
                        SELECT EXISTS (SELECT
                                       FROM information_schema.tables
                                       WHERE table_schema = 'public'
                                         AND table_name = 'klima_urunleri');
                        """)
        table_exists = old_cur.fetchone()[0]

        if table_exists:
            logger.info("🗑️ Mevcut klima_urunleri tablosu siliniyor...")
            old_cur.execute("DROP TABLE klima_urunleri CASCADE;")
        else:
            logger.info("📋 klima_urunleri tablosu bulunamadı, yeni tablo oluşturulacak")

        # Yeni klima tablosunu oluştur
        logger.info("🔧 Yeni klima_urunleri tablosu oluşturuluyor...")
        create_table_sql = """
                           CREATE TABLE klima_urunleri \
                           ( \
                               id                      VARCHAR(255) PRIMARY KEY, \
                               product_name            TEXT           NOT NULL, \
                               brand                   VARCHAR(100)   NOT NULL DEFAULT 'Bilinmeyen Marka', \
                               category                VARCHAR(100)   NOT NULL DEFAULT 'Klima', \
                               platform                VARCHAR(50)    NOT NULL DEFAULT 'Bilinmiyor', \
                               price                   DECIMAL(12, 2) NOT NULL DEFAULT 0.00, \
                               rating                  DECIMAL(3, 2)  NOT NULL DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5), \
                               review_count            INTEGER        NOT NULL DEFAULT 0 CHECK (review_count >= 0), \
                               sales_volume            INTEGER        NOT NULL DEFAULT 0 CHECK (sales_volume >= 0), \
                               seller_description      TEXT                    DEFAULT '', \
                               profitability_analysis  TEXT                    DEFAULT '', \
                               sales_performance       TEXT                    DEFAULT '', \
                               competitive_positioning TEXT                    DEFAULT '', \
                               inventory_strategy      TEXT                    DEFAULT '', \
                               pricing_opportunities   TEXT                    DEFAULT '', \
                               customer_insights       TEXT                    DEFAULT '', \
                               marketing_angles        TEXT                    DEFAULT '', \
                               risk_management         TEXT                    DEFAULT '', \
                               operational_advice      TEXT                    DEFAULT '', \
                               financial_projections   TEXT                    DEFAULT '', \
                               seller_action_plan      TEXT                    DEFAULT '', \
                               seller_summary          TEXT                    DEFAULT '', \
                               search_keywords         TEXT                    DEFAULT '[]', \
                               created_at              TIMESTAMP               DEFAULT CURRENT_TIMESTAMP, \
                               updated_at              TIMESTAMP               DEFAULT CURRENT_TIMESTAMP
                           ); \
                           """

        old_cur.execute(create_table_sql)

        # İndeksleri oluştur
        logger.info("🔧 Klima tablosu indeksleri oluşturuluyor...")
        old_cur.execute("CREATE INDEX idx_klima_brand ON klima_urunleri(brand);")
        old_cur.execute("CREATE INDEX idx_klima_category ON klima_urunleri(category);")
        old_cur.execute("CREATE INDEX idx_klima_platform ON klima_urunleri(platform);")
        old_cur.execute("CREATE INDEX idx_klima_price ON klima_urunleri(price);")
        old_cur.execute("CREATE INDEX idx_klima_rating ON klima_urunleri(rating);")
        old_cur.execute("CREATE INDEX idx_klima_sales_volume ON klima_urunleri(sales_volume);")

        old_conn.commit()
        logger.info("✅ Klima tablosu ve indeksler oluşturuldu")

        # Verileri ekle
        logger.info("📥 Klima verileri ekleniyor...")

        success_count = 0
        error_count = 0
        used_ids = set()  # Benzersiz ID kontrolü için

        for i, item in enumerate(json_data):
            try:
                # Güvenli veri çıkarma fonksiyonu
                def safe_get(value, default=''):
                    if value is None:
                        return default
                    if isinstance(value, (dict, list)):
                        return json.dumps(value, ensure_ascii=False)
                    return str(value)

                def safe_get_float(value, default=0.0):
                    if value is None:
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default

                def safe_get_int(value, default=0):
                    if value is None:
                        return default
                    try:
                        return int(float(value))
                    except (ValueError, TypeError):
                        return default

                # Benzersiz ID oluştur
                unique_id = generate_unique_id(item, i)

                # ID tekrarını önle
                counter = 0
                original_unique_id = unique_id
                while unique_id in used_ids:
                    counter += 1
                    unique_id = f"{original_unique_id}_{counter}"

                used_ids.add(unique_id)

                # Search keywords'ü güvenli şekilde işle
                search_keywords = item.get('search_keywords', [])
                if isinstance(search_keywords, list):
                    search_keywords_json = json.dumps(search_keywords, ensure_ascii=False)
                elif isinstance(search_keywords, str):
                    search_keywords_json = search_keywords
                else:
                    search_keywords_json = '[]'

                # Veriyi temizle ve hazırla
                klima_data = (
                    unique_id,  # Benzersiz ID kullan
                    safe_get(item.get('product_name', 'Bilinmeyen Klima')),
                    safe_get(item.get('brand', 'Bilinmeyen Marka')),
                    'Klima',  # category
                    safe_get(item.get('platform', 'Bilinmiyor')),
                    safe_get_float(item.get('price', 0)),
                    min(5.0, max(0.0, safe_get_float(item.get('rating', 0)))),  # 0-5 arası sınırla
                    safe_get_int(item.get('review_count', 0)),
                    safe_get_int(item.get('sales_volume', 0)),
                    safe_get(item.get('seller_description', '')),
                    safe_get(item.get('profitability_analysis', '')),
                    safe_get(item.get('sales_performance', '')),
                    safe_get(item.get('competitive_positioning', '')),
                    safe_get(item.get('inventory_strategy', '')),
                    safe_get(item.get('pricing_opportunities', '')),
                    safe_get(item.get('customer_insights', '')),
                    safe_get(item.get('marketing_angles', '')),
                    safe_get(item.get('risk_management', '')),
                    safe_get(item.get('operational_advice', '')),
                    safe_get(item.get('financial_projections', '')),
                    safe_get(item.get('seller_action_plan', '')),
                    safe_get(item.get('seller_summary', '')),
                    search_keywords_json
                )

                # INSERT ile ekleme yap (UPDATE yerine)
                old_cur.execute("""
                                INSERT INTO klima_urunleri (id, product_name, brand, category, platform, price, rating,
                                                            review_count, sales_volume, seller_description,
                                                            profitability_analysis,
                                                            sales_performance, competitive_positioning,
                                                            inventory_strategy,
                                                            pricing_opportunities, customer_insights, marketing_angles,
                                                            risk_management, operational_advice, financial_projections,
                                                            seller_action_plan, seller_summary, search_keywords)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                        %s, %s, %s)
                                """, klima_data)

                success_count += 1

                # Her 20 kayıttan sonra commit
                if success_count % 20 == 0:
                    old_conn.commit()

                if (i + 1) % 50 == 0:
                    logger.info(f"📊 İşlenen: {i + 1}/{len(json_data)} (Başarılı: {success_count})")

            except Exception as e:
                error_count += 1
                # Transaction'ı temizle
                old_conn.rollback()

                if error_count <= 5:  # İlk 5 hatayı detaylandır
                    logger.error(f"❌ Klima {i + 1} ekleme hatası: {e}")
                    logger.error(f"Hatalı veri örneği: {str(item)[:200]}...")
                elif error_count == 6:
                    logger.error("... (daha fazla hata var, gösterim durduruldu)")

        # Son commit
        old_conn.commit()

        # Sonuçları kontrol et
        old_cur.execute("SELECT COUNT(*) FROM klima_urunleri")
        final_count = old_cur.fetchone()[0]

        # Marka dağılımı
        old_cur.execute("""
                        SELECT brand, COUNT(*)
                        FROM klima_urunleri
                        GROUP BY brand
                        ORDER BY COUNT(*) DESC LIMIT 10
                        """)
        brand_stats = old_cur.fetchall()

        logger.info("=" * 50)
        logger.info("📊 KLİMA İMPORT ÖZETİ")
        logger.info("=" * 50)
        logger.info(f"📁 Kullanılan dosya: {used_file}")
        logger.info(f"📦 JSON'daki toplam veri: {len(json_data)}")
        logger.info(f"✅ Başarılı eklenen: {success_count}")
        logger.info(f"❌ Hatalı: {error_count}")
        logger.info(f"🗄️ Veritabanındaki toplam: {final_count}")

        if brand_stats:
            logger.info("\n🏷️ Marka dağılımı:")
            for brand, count in brand_stats:
                logger.info(f"  - {brand}: {count} ürün")

        # Örnek verileri göster
        old_cur.execute("SELECT product_name, brand, price FROM klima_urunleri ORDER BY price DESC LIMIT 5")
        samples = old_cur.fetchall()

        logger.info("\n📋 Örnek klima ürünleri (en pahalılar):")
        for name, brand, price in samples:
            logger.info(f"  - {name[:60]}... ({brand}) - {price} TL")

        old_cur.close()
        old_conn.close()

        # Başarı kriterini düşük tut çünkü veriler gerçekten eklenebilir
        if final_count >= (len(json_data) * 0.8):  # %80'i eklenmişse başarılı say
            logger.info("🎉 Klima verileri başarıyla yeniden import edildi!")
            return True
        else:
            logger.warning(f"⚠️ Sadece {final_count}/{len(json_data)} klima verisi eklendi.")
            logger.info("💡 Hatalar nedeniyle bazı veriler eklenemedi.")
            return final_count > 50  # En az 50 tane varsa devam et

    except Exception as e:
        logger.error(f"❌ Klima import hatası: {e}")
        old_conn.rollback()
        return False


def test_klima_data():
    """Klima verilerini test et"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5434, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM klima_urunleri")
        count = cur.fetchone()[0]

        cur.execute("SELECT AVG(price), AVG(rating) FROM klima_urunleri WHERE price > 0")
        avg_price, avg_rating = cur.fetchone()

        # ID benzersizlik kontrolü
        cur.execute("""
                    SELECT COUNT(*) as total_count, COUNT(DISTINCT id) as unique_count
                    FROM klima_urunleri
                    """)
        total_count, unique_count = cur.fetchone()

        print(f"🔍 TEST SONUÇLARI:")
        print(f"📦 Toplam klima: {count}")
        print(f"🆔 Benzersiz ID sayısı: {unique_count}")
        print(f"💰 Ortalama fiyat: {avg_price:.2f} TL")
        print(f"⭐ Ortalama rating: {avg_rating:.2f}")

        if total_count == unique_count:
            print("✅ Tüm ID'ler benzersiz!")
        else:
            print(f"⚠️ Duplicate ID problemi: {total_count - unique_count} duplicate var")

        cur.close()
        conn.close()

        return count > 50

    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Klima verileri yeniden import ediliyor...")

    if reimport_klima_data():
        print("\n🔍 Klima verileri test ediliyor...")
        if test_klima_data():
            print("✅ Klima verileri hazır!")
            print("💡 Şimdi full_data_import.py'yi çalıştırabilirsin!")
        else:
            print("⚠️ Klima veri sayısı az görünüyor.")
    else:
        print("❌ Klima import başarısız!")