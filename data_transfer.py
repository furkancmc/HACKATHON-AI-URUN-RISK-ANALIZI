# import_all_categories.py
import psycopg2
import json
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_tables():
    """Eski veritabanındaki tüm tabloları listele"""
    try:
        old_conn = psycopg2.connect(
            host="localhost", port=5433, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        old_cur = old_conn.cursor()

        # Tüm tabloları listele
        old_cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_type = 'BASE TABLE'
                          AND table_name LIKE '%urunleri'
                        """)

        tables = [row[0] for row in old_cur.fetchall()]

        old_cur.close()
        old_conn.close()

        return tables

    except Exception as e:
        logger.error(f"❌ Tablo listeleme hatası: {e}")
        return []


def convert_table_to_vector_format(table_name: str, category: str) -> List[Dict]:
    """Diğer tabloları vector_products formatına çevir"""
    try:
        old_conn = psycopg2.connect(
            host="localhost", port=5433, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        old_cur = old_conn.cursor()

        # Tablo yapısını kontrol et
        old_cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in old_cur.fetchall()]

        # Verileri al
        old_cur.execute(f"SELECT * FROM {table_name}")
        rows = old_cur.fetchall()

        logger.info(f"📊 {table_name}: {len(rows)} kayıt, Sütunlar: {columns}")

        converted_data = []

        for i, row in enumerate(rows):
            try:
                # Row'u dictionary'e çevir
                row_dict = dict(zip(columns, row))

                # Vector format'a çevir
                vector_product = {
                    'id': row_dict.get('id', f'{table_name}_{i}'),
                    'embedding_text': create_embedding_text(row_dict, category),
                    'category': category,
                    'brand': row_dict.get('brand', 'Bilinmeyen Marka'),
                    'platform': row_dict.get('platform', 'Bilinmiyor'),
                    'price_range': determine_price_range(row_dict.get('price', 0)),
                    'risk_level': determine_risk_level(row_dict.get('risk_score', 5)),
                    'rating_category': determine_rating_category(row_dict.get('rating', 0)),
                    'sales_volume_category': determine_sales_category(row_dict.get('sales_volume', 0)),
                    'product_name': row_dict.get('product_name', 'Bilinmeyen Ürün'),
                    'price': float(row_dict.get('price', 0)),
                    'rating': float(row_dict.get('rating', 0)),
                    'review_count': int(row_dict.get('review_count', 0)),
                    'sales_volume': int(row_dict.get('sales_volume', 0)),
                    'profit_margin': float(row_dict.get('profit_margin', 0.25)),
                    'risk_score': int(row_dict.get('risk_score', 5)),
                    'product_url': row_dict.get('product_url', ''),
                    'seller_description': row_dict.get('seller_description', ''),
                    'profitability_analysis': row_dict.get('profitability_analysis', ''),
                    'sales_performance': row_dict.get('sales_performance', ''),
                    'competitive_positioning': row_dict.get('competitive_positioning', ''),
                    'inventory_strategy': row_dict.get('inventory_strategy', ''),
                    'pricing_opportunities': row_dict.get('pricing_opportunities', ''),
                    'customer_insights': row_dict.get('customer_insights', ''),
                    'marketing_angles': row_dict.get('marketing_angles', ''),
                    'risk_management': row_dict.get('risk_management', ''),
                    'operational_advice': row_dict.get('operational_advice', ''),
                    'financial_projections': row_dict.get('financial_projections', ''),
                    'seller_action_plan': row_dict.get('seller_action_plan', ''),
                    'seller_summary': row_dict.get('seller_summary', ''),
                    'search_keywords': json.dumps(row_dict.get('search_keywords', []))
                }

                converted_data.append(vector_product)

            except Exception as e:
                logger.error(f"❌ {table_name} row {i} dönüştürme hatası: {e}")

        old_cur.close()
        old_conn.close()

        return converted_data

    except Exception as e:
        logger.error(f"❌ {table_name} dönüştürme hatası: {e}")
        return []


def create_embedding_text(row_dict: Dict, category: str) -> str:
    """Embedding text'i oluştur"""
    product_name = row_dict.get('product_name', 'Bilinmeyen Ürün')
    brand = row_dict.get('brand', 'Bilinmeyen Marka')
    description = row_dict.get('seller_description', '')
    summary = row_dict.get('seller_summary', '')
    price = row_dict.get('price', 0)
    rating = row_dict.get('rating', 0)
    platform = row_dict.get('platform', 'Bilinmiyor')

    embedding_text = f"{product_name} {brand} {category} {description} {summary} Fiyat: {price} TL Rating: {rating} Platform: {platform}"

    return embedding_text.strip()


def determine_price_range(price: float) -> str:
    """Fiyat aralığını belirle"""
    if price < 1000:
        return 'budget'
    elif price < 5000:
        return 'standard'
    else:
        return 'premium'


def determine_risk_level(risk_score: int) -> str:
    """Risk seviyesini belirle"""
    if risk_score <= 3:
        return 'low'
    elif risk_score <= 6:
        return 'medium'
    else:
        return 'high'


def determine_rating_category(rating: float) -> str:
    """Rating kategorisini belirle"""
    if rating >= 4.5:
        return 'excellent'
    elif rating >= 4.0:
        return 'good'
    else:
        return 'average'


def determine_sales_category(sales_volume: int) -> str:
    """Satış kategorisini belirle"""
    if sales_volume >= 500:
        return 'high'
    elif sales_volume >= 100:
        return 'medium'
    else:
        return 'low'


def import_all_categories():
    """Tüm kategorileri içe aktar"""

    # Mevcut tabloları bul
    tables = get_all_tables()
    logger.info(f"🔍 Bulunan tablolar: {tables}")

    if not tables:
        logger.error("❌ Hiçbir tablo bulunamadı!")
        return False

    # Docker PostgreSQL'e bağlan
    try:
        new_conn = psycopg2.connect(
            host="localhost", port=5434, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        new_cur = new_conn.cursor()
        logger.info("✅ Docker PostgreSQL'e bağlandı")
    except Exception as e:
        logger.error(f"❌ Docker PostgreSQL bağlantı hatası: {e}")
        return False

    # Tablo mapping'i
    table_mapping = {
        'telefon_urunleri': 'telefon',
        'klima_urunleri': 'klima',
        'bilgisayar_urunleri': 'bilgisayar',
        'vector_products': 'kulaklık'  # Zaten var
    }

    total_imported = 0

    for table_name in tables:
        if table_name == 'vector_products':
            continue  # Zaten var

        category = table_mapping.get(table_name, table_name.replace('_urunleri', ''))

        logger.info(f"🔄 {table_name} -> {category} kategorisi işleniyor...")

        # Tabloyu dönüştür
        converted_data = convert_table_to_vector_format(table_name, category)

        if converted_data:
            # Vector_products'a ekle
            for item in converted_data:
                try:
                    columns = list(item.keys())
                    values = list(item.values())
                    placeholders = ['%s'] * len(values)

                    insert_sql = f"""
                    INSERT INTO vector_products ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                    ON CONFLICT (id) DO NOTHING
                    """

                    new_cur.execute(insert_sql, values)
                    total_imported += 1

                except Exception as e:
                    logger.error(f"❌ {category} ürün ekleme hatası: {e}")

            new_conn.commit()
            logger.info(f"✅ {category}: {len(converted_data)} ürün eklendi")

        else:
            logger.warning(f"⚠️ {table_name} dönüştürülemedi")

    # Final kontrol
    new_cur.execute("SELECT COUNT(*) FROM vector_products")
    final_count = new_cur.fetchone()[0]

    new_cur.execute("""
                    SELECT category, COUNT(*)
                    FROM vector_products
                    GROUP BY category
                    ORDER BY COUNT(*) DESC
                    """)
    category_counts = new_cur.fetchall()

    logger.info("=" * 50)
    logger.info("📊 İMPORT ÖZETİ")
    logger.info("=" * 50)
    logger.info(f"📦 Toplam ürün sayısı: {final_count}")
    logger.info(f"➕ Yeni eklenen: {total_imported}")

    logger.info("🏷️ Kategori dağılımı:")
    for category, count in category_counts:
        logger.info(f"  - {category}: {count} ürün")

    new_cur.close()
    new_conn.close()

    return True


if __name__ == "__main__":
    print("🚀 Tüm kategoriler içe aktarılıyor...")

    if import_all_categories():
        print("✅ Tüm kategoriler başarıyla içe aktarıldı!")
    else:
        print("❌ İçe aktarım başarısız!")