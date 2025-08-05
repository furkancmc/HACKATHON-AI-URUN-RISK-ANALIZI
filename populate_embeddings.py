# populate_embeddings.py
import psycopg2
import logging
from embedding_service import EmbeddingService
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_tables():
    """Veritabanındaki tüm product tablolarını listele"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5434, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        cur = conn.cursor()

        # Tüm tabloları listele
        cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                        AND table_name LIKE '%urun%'
                       OR table_name LIKE '%klima%'
                       OR table_name LIKE '%product%'
                    ORDER BY table_name
                    """)

        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()

        return tables

    except Exception as e:
        logger.error(f"❌ Tablo listesi alınamadı: {e}")
        return []


def check_table_structure(table_name):
    """Tablonun yapısını kontrol et"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5434, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        cur = conn.cursor()

        # Tablo sütunlarını kontrol et
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)

        columns = cur.fetchall()
        cur.close()
        conn.close()

        return columns

    except Exception as e:
        logger.error(f"❌ {table_name} yapısı kontrol edilemedi: {e}")
        return []


def create_embeddings_table(table_name):
    """Her tablo için embeddings tablosu oluştur"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5433, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        cur = conn.cursor()

        embedding_table_name = f"{table_name}_embeddings"

        # Embeddings tablosunu oluştur
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {embedding_table_name} (
                id VARCHAR(255) PRIMARY KEY,
                product_id VARCHAR(255) REFERENCES {table_name}(id),
                product_name TEXT,
                combined_text TEXT,
                embedding VECTOR(768),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # İndeksler oluştur
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{embedding_table_name}_product_id ON {embedding_table_name}(product_id)")
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{embedding_table_name}_embedding ON {embedding_table_name} USING ivfflat (embedding vector_cosine_ops)")

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"✅ {embedding_table_name} tablosu hazır")
        return True

    except Exception as e:
        logger.error(f"❌ {embedding_table_name} oluşturulamadı: {e}")
        return False


def get_table_text_columns(table_name):
    """Tablodaki text sütunlarını belirle"""

    # Genel text sütunları
    text_columns = ['product_name', 'description', 'seller_description']

    # Analiz sütunları (klima tablosu için)
    analysis_columns = [
        'profitability_analysis', 'sales_performance', 'competitive_positioning',
        'inventory_strategy', 'pricing_opportunities', 'customer_insights',
        'marketing_angles', 'risk_management', 'operational_advice',
        'financial_projections', 'seller_action_plan', 'seller_summary'
    ]

    # Tabloya özel sütun seçimi
    if 'klima' in table_name.lower():
        return text_columns + analysis_columns
    else:
        return text_columns


def populate_table_embeddings(table_name):
    """Belirli bir tablo için embeddings oluştur"""

    embedding_service = EmbeddingService()
    embedding_table_name = f"{table_name}_embeddings"

    try:
        conn = psycopg2.connect(
            host="localhost", port=5433, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        cur = conn.cursor()

        # Tablo yapısını kontrol et
        columns = check_table_structure(table_name)
        column_names = [col[0] for col in columns]

        # Uygun text sütunlarını seç
        text_columns = get_table_text_columns(table_name)
        available_columns = [col for col in text_columns if col in column_names]

        logger.info(f"📋 {table_name} için kullanılacak sütunlar: {available_columns}")

        # Mevcut kayıt sayısını al
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = cur.fetchone()[0]

        logger.info(f"📊 {table_name}: {total_records} kayıt bulundu")

        if total_records == 0:
            logger.warning(f"⚠️ {table_name} tablosu boş, atlanıyor")
            return True

        # Mevcut embeddings'leri temizle
        cur.execute(f"DELETE FROM {embedding_table_name}")

        # Batch işleme için kayıtları al
        batch_size = 50
        offset = 0
        processed = 0

        while offset < total_records:
            # Batch halinde kayıtları al
            columns_sql = ', '.join(['id'] + available_columns)
            cur.execute(f"""
                SELECT {columns_sql}
                FROM {table_name}
                ORDER BY id
                LIMIT {batch_size} OFFSET {offset}
            """)

            batch_records = cur.fetchall()

            for record in batch_records:
                try:
                    record_id = record[0]

                    # Text sütunlarını birleştir
                    text_parts = []

                    for i, col_name in enumerate(available_columns):
                        value = record[i + 1]  # id'den sonraki sütunlar
                        if value and str(value).strip():
                            text_parts.append(f"{col_name}: {str(value)}")

                    combined_text = ' | '.join(text_parts)

                    if not combined_text.strip():
                        logger.warning(f"⚠️ {record_id} için text bulunamadı")
                        continue

                    # Embedding oluştur
                    embedding = embedding_service.create_embedding(combined_text)

                    if embedding:
                        # Embedding'i veritabanına kaydet
                        cur.execute(f"""
                            INSERT INTO {embedding_table_name} 
                            (id, product_id, product_name, combined_text, embedding)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            f"{table_name}_{record_id}",
                            record_id,
                            record[1] if len(record) > 1 else '',  # product_name
                            combined_text[:2000],  # İlk 2000 karakter
                            embedding
                        ))

                        processed += 1

                        if processed % 10 == 0:
                            conn.commit()
                            logger.info(f"📊 {table_name}: {processed}/{total_records} işlendi")

                    # Rate limiting
                    time.sleep(0.1)

                except Exception as e:
                    logger.error(f"❌ {record_id} embedding hatası: {e}")
                    continue

            offset += batch_size

        conn.commit()

        # Sonuçları kontrol et
        cur.execute(f"SELECT COUNT(*) FROM {embedding_table_name}")
        embedding_count = cur.fetchone()[0]

        logger.info(f"✅ {table_name}: {embedding_count} embedding oluşturuldu")

        cur.close()
        conn.close()

        return embedding_count > 0

    except Exception as e:
        logger.error(f"❌ {table_name} embedding oluşturma hatası: {e}")
        return False


def main():
    """Ana fonksiyon - Tüm tablolar için embeddings oluştur"""

    logger.info("🚀 Tüm tablolar için embedding oluşturuluyor...")

    # Tüm tabloları al
    tables = get_all_tables()

    if not tables:
        logger.error("❌ Hiç tablo bulunamadı!")
        return False

    logger.info(f"📋 Bulunan tablolar: {tables}")

    success_count = 0
    total_tables = len(tables)

    for table_name in tables:
        try:
            logger.info(f"\n🔧 {table_name} işleniyor...")

            # Tablo yapısını kontrol et
            columns = check_table_structure(table_name)
            if not columns:
                logger.warning(f"⚠️ {table_name} yapısı alınamadı, atlanıyor")
                continue

            # Embeddings tablosunu oluştur
            if not create_embeddings_table(table_name):
                logger.warning(f"⚠️ {table_name} için embeddings tablosu oluşturulamadı")
                continue

            # Embeddings oluştur
            if populate_table_embeddings(table_name):
                success_count += 1
                logger.info(f"✅ {table_name} başarıyla tamamlandı")
            else:
                logger.warning(f"⚠️ {table_name} embeddings oluşturulamadı")

        except Exception as e:
            logger.error(f"❌ {table_name} işleme hatası: {e}")

    logger.info("\n" + "=" * 50)
    logger.info("📊 EMBEDDING ÖZETİ")
    logger.info("=" * 50)
    logger.info(f"📦 Toplam tablo: {total_tables}")
    logger.info(f"✅ Başarılı: {success_count}")
    logger.info(f"❌ Başarısız: {total_tables - success_count}")

    if success_count > 0:
        logger.info("🎉 Embedding oluşturma tamamlandı!")
        logger.info("💡 Şimdi main_app.py'yi çalıştırabilirsin!")
        return True
    else:
        logger.error("❌ Hiçbir tablo için embedding oluşturulamadı!")
        return False


if __name__ == "__main__":
    main()