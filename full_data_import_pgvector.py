# import_all_tables.py - ESKİ VERİTABANINDAN YENİSİNE KOPYALA
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def copy_all_tables():
    """Eski veritabanından (5433) yeni veritabanına (5434) tüm tabloları kopyala"""

    try:
        # ESKİ VERİTABANI (5433)
        old_conn = psycopg2.connect(
            host="localhost", port=5433, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        old_cur = old_conn.cursor()
        logger.info("✅ Eski veritabanına bağlandı (port 5433)")

        # YENİ VERİTABANI (5434)
        new_conn = psycopg2.connect(
            host="localhost", port=5434, database="urun_risk_analiz",
            user="postgres", password="furkan"
        )
        new_cur = new_conn.cursor()
        logger.info("✅ Yeni veritabanına bağlandı (port 5434)")

        # Eski veritabanındaki tabloları listele
        old_cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name NOT LIKE '%embeddings%'
                        ORDER BY table_name
                        """)

        tables = [row[0] for row in old_cur.fetchall()]
        logger.info(f"📋 Bulunan tablolar: {tables}")

        if not tables:
            logger.error("❌ Eski veritabanında tablo bulunamadı!")
            return False

        for table_name in tables:
            try:
                logger.info(f"\n🔧 {table_name} kopyalanıyor...")

                # Kayıt sayısını kontrol et
                old_cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = old_cur.fetchone()[0]

                if record_count == 0:
                    logger.warning(f"⚠️ {table_name} boş, atlanıyor")
                    continue

                logger.info(f"📊 {table_name}: {record_count} kayıt bulundu")

                # Tablo yapısını al
                old_cur.execute(f"""
                    SELECT column_name, data_type, character_maximum_length, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                columns_info = old_cur.fetchall()

                # Yeni tabloda eski tabloyu sil ve yeniden oluştur
                new_cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")

                # CREATE TABLE statement
                column_defs = []
                for col_name, data_type, max_len, nullable in columns_info:
                    col_def = f'"{col_name}"'

                    if data_type == 'character varying':
                        if max_len:
                            col_def += f" VARCHAR({max_len})"
                        else:
                            col_def += " TEXT"
                    elif data_type == 'text':
                        col_def += " TEXT"
                    elif data_type == 'integer':
                        col_def += " INTEGER"
                    elif data_type == 'bigint':
                        col_def += " BIGINT"
                    elif data_type == 'numeric':
                        col_def += " DECIMAL(12,2)"
                    elif data_type == 'timestamp without time zone':
                        col_def += " TIMESTAMP"
                    elif data_type == 'boolean':
                        col_def += " BOOLEAN"
                    else:
                        col_def += f" {data_type.upper()}"

                    # Primary key kontrolü
                    if col_name == 'id':
                        col_def += " PRIMARY KEY"

                    column_defs.append(col_def)

                create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)});"
                new_cur.execute(create_sql)

                # Verileri kopyala - BATCH halinde
                old_cur.execute(f"SELECT * FROM {table_name}")

                # Sütun isimlerini al
                column_names = [desc[0] for desc in old_cur.description]
                placeholders = ', '.join(['%s'] * len(column_names))
                quoted_columns = ', '.join([f'"{col}"' for col in column_names])

                insert_sql = f'INSERT INTO {table_name} ({quoted_columns}) VALUES ({placeholders})'

                # Batch halinde kopyala
                batch_size = 1000
                inserted = 0

                while True:
                    rows = old_cur.fetchmany(batch_size)
                    if not rows:
                        break

                    try:
                        new_cur.executemany(insert_sql, rows)
                        inserted += len(rows)
                        new_conn.commit()
                        logger.info(f"📊 {table_name}: {inserted}/{record_count} kopyalandı")
                    except Exception as e:
                        logger.error(f"❌ Batch insert hatası: {e}")
                        new_conn.rollback()
                        break

                # Doğrulama
                new_cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                new_count = new_cur.fetchone()[0]

                logger.info(f"✅ {table_name}: {new_count} kayıt başarıyla kopyalandı")

            except Exception as e:
                logger.error(f"❌ {table_name} kopyalama hatası: {e}")
                new_conn.rollback()
                continue

        # Final özet
        new_cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name NOT LIKE '%embeddings%'
                        ORDER BY table_name
                        """)

        final_tables = [row[0] for row in new_cur.fetchall()]

        logger.info("\n" + "=" * 50)
        logger.info("📊 KOPYALAMA ÖZETİ")
        logger.info("=" * 50)

        total_records = 0
        for table_name in final_tables:
            new_cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = new_cur.fetchone()[0]
            total_records += count
            logger.info(f"📦 {table_name}: {count} kayıt")

        logger.info(f"📊 TOPLAM: {total_records} kayıt")
        logger.info("🎉 Tüm tablolar kopyalandı!")

        old_cur.close()
        old_conn.close()
        new_cur.close()
        new_conn.close()

        return True

    except Exception as e:
        logger.error(f"❌ Kopyalama hatası: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Tüm tablolar eski veritabanından yenisine kopyalanıyor...")

    if copy_all_tables():
        print("✅ Başarılı! Şimdi create_embeddings.py çalıştırabilirsin!")
    else:
        print("❌ Kopyalama başarısız!")