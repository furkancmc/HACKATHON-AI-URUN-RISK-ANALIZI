# bulletproof_embeddings_clean.py - TEMİZ VERSİYON
import psycopg2
import logging
import time
import json
from embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BulletproofEmbeddings:
    def __init__(self):
        self.embedding_service = None
        self.conn = None
        self.cur = None

    def connect_database(self):
        """Veritabanına bağlan - tüm portları dene"""
        ports = [5434, 5433, 5432]

        for port in ports:
            try:
                self.conn = psycopg2.connect(
                    host="localhost", port=port, database="urun_risk_analiz",
                    user="postgres", password="furkan"
                )
                self.conn.autocommit = False
                self.cur = self.conn.cursor()
                logger.info(f"✅ Veritabanına bağlandı (port {port})")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Port {port} bağlantı hatası: {e}")
                continue

        logger.error("❌ Hiçbir portta PostgreSQL bulunamadı!")
        return False

    def init_embedding_service(self):
        """Embedding servisini başlat"""
        try:
            self.embedding_service = EmbeddingService()
            logger.info("✅ Embedding servisi hazır")
            return True
        except Exception as e:
            logger.error(f"❌ Embedding servisi başlatılamadı: {e}")
            return False

    def get_embedding_dimension(self):
        """Model'in embedding boyutunu öğren"""
        try:
            test_embedding = self.embedding_service.create_embedding("test")
            if test_embedding:
                return len(test_embedding)
            return 384  # default
        except:
            return 384  # fallback

    def get_primary_key_column(self, table_name):
        """Tablonun primary key sütununu bul"""
        try:
            # Önce 'id' sütunu var mı kontrol et
            self.cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'id'
            """)

            if self.cur.fetchone():
                return 'id'

            # 'id' yoksa primary key'i bul
            self.cur.execute(f"""
                SELECT column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = '{table_name}' 
                AND tc.constraint_type = 'PRIMARY KEY'
                LIMIT 1
            """)

            result = self.cur.fetchone()
            if result:
                return result[0]

            # Primary key yoksa ilk sütunu kullan
            self.cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                LIMIT 1
            """)

            result = self.cur.fetchone()
            return result[0] if result else 'id'

        except Exception as e:
            logger.warning(f"⚠️ {table_name} primary key bulunamadı: {e}")
            return 'id'  # fallback

    def get_tables(self):
        """Mevcut tabloları al"""
        try:
            self.cur.execute("""
                             SELECT table_name
                             FROM information_schema.tables
                             WHERE table_schema = 'public'
                               AND table_name NOT LIKE '%embeddings%'
                               AND table_name != 'spatial_ref_sys'
                             ORDER BY table_name
                             """)

            tables = [row[0] for row in self.cur.fetchall()]
            logger.info(f"📋 Bulunan tablolar: {tables}")
            return tables
        except Exception as e:
            logger.error(f"❌ Tablo listesi alınamadı: {e}")
            return []

    def get_table_columns(self, table_name):
        """Tablo sütunlarını al"""
        try:
            self.cur.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)

            columns = self.cur.fetchall()
            return [col[0] for col in columns]
        except Exception as e:
            logger.error(f"❌ {table_name} sütunları alınamadı: {e}")
            return []

    def get_text_columns(self, all_columns):
        """Text sütunlarını belirle - esnek"""
        text_columns = []

        # Öncelikli sütunlar
        priority_columns = [
            'product_name', 'name', 'title', 'description', 'seller_description',
            'details', 'summary', 'content', 'text', 'info'
        ]

        # Analiz sütunları
        analysis_columns = [
            'profitability_analysis', 'sales_performance', 'competitive_positioning',
            'inventory_strategy', 'pricing_opportunities', 'customer_insights',
            'marketing_angles', 'risk_management', 'operational_advice',
            'financial_projections', 'seller_action_plan', 'seller_summary',
            'analysis', 'recommendation', 'insight', 'strategy'
        ]

        # Öncelikli sütunları ekle
        for col in priority_columns:
            if col in all_columns:
                text_columns.append(col)

        # Analiz sütunlarını ekle
        for col in analysis_columns:
            if col in all_columns:
                text_columns.append(col)

        return text_columns

    def create_embedding_table(self, table_name, dimension):
        """Embedding tablosu oluştur - esnek boyut"""
        try:
            embedding_table = f"{table_name}_embeddings"

            # Mevcut tabloyu sil
            self.cur.execute(f"DROP TABLE IF EXISTS {embedding_table} CASCADE;")

            # Yeni tablo oluştur
            self.cur.execute(f"""
                CREATE TABLE {embedding_table} (
                    id VARCHAR(255) PRIMARY KEY,
                    product_id VARCHAR(255),
                    product_name TEXT,
                    combined_text TEXT,
                    embedding VECTOR({dimension}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # İndeks oluştur - hata olursa devam et
            try:
                self.cur.execute(f"CREATE INDEX idx_{embedding_table}_product_id ON {embedding_table}(product_id)")
                self.cur.execute(
                    f"CREATE INDEX idx_{embedding_table}_embedding ON {embedding_table} USING ivfflat (embedding vector_cosine_ops)")
            except Exception as e:
                logger.warning(f"⚠️ İndeks oluşturulamadı: {e}")

            self.conn.commit()
            logger.info(f"✅ {embedding_table} tablosu oluşturuldu (boyut: {dimension})")
            return True

        except Exception as e:
            logger.error(f"❌ {embedding_table} oluşturulamadı: {e}")
            self.conn.rollback()
            return False

    def process_table(self, table_name):
        """Tablodaki tüm verileri işle - ultra esnek"""
        try:
            # Primary key sütununu bul
            pk_column = self.get_primary_key_column(table_name)
            logger.info(f"🔑 {table_name} primary key: {pk_column}")

            # Kayıt sayısını kontrol et
            self.cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records = self.cur.fetchone()[0]

            if total_records == 0:
                logger.warning(f"⚠️ {table_name} boş, atlanıyor")
                return 0

            logger.info(f"📊 {table_name}: {total_records} kayıt bulundu")

            # Sütunları al
            all_columns = self.get_table_columns(table_name)
            text_columns = self.get_text_columns(all_columns)

            if not text_columns:
                logger.warning(f"⚠️ {table_name} için text sütunu bulunamadı")
                return 0

            logger.info(f"📝 {table_name} kullanılacak sütunlar: {text_columns}")

            # Embedding boyutunu öğren
            dimension = self.get_embedding_dimension()

            # Embedding tablosu oluştur
            if not self.create_embedding_table(table_name, dimension):
                return 0

            embedding_table = f"{table_name}_embeddings"
            processed = 0
            errors = 0

            # Küçük batch'lerle işle
            batch_size = 5
            offset = 0

            while offset < total_records:
                try:
                    # Batch al - primary key kullan
                    columns_sql = ', '.join([pk_column] + text_columns)
                    self.cur.execute(f"""
                        SELECT {columns_sql}
                        FROM {table_name}
                        ORDER BY {pk_column}
                        LIMIT {batch_size} OFFSET {offset}
                    """)

                    rows = self.cur.fetchall()

                    if not rows:
                        break

                    # Her satırı işle
                    for row in rows:
                        try:
                            record_id = row[0]

                            # Text'leri birleştir - güvenli
                            text_parts = []
                            product_name = ""

                            for i, col_name in enumerate(text_columns):
                                try:
                                    value = row[i + 1] if i + 1 < len(row) else None
                                    if value and str(value).strip() and str(value) != 'None':
                                        clean_value = str(value)[:500]  # Maksimum 500 karakter
                                        text_parts.append(f"{col_name}: {clean_value}")

                                        # İlk text sütununu product_name olarak kullan
                                        if not product_name and col_name in ['product_name', 'name', 'title']:
                                            product_name = clean_value[:100]
                                except:
                                    continue

                            combined_text = ' | '.join(text_parts)

                            if not combined_text.strip():
                                logger.warning(f"⚠️ {record_id} için text bulunamadı")
                                continue

                            # Embedding oluştur - güvenli
                            try:
                                embedding = self.embedding_service.create_embedding(combined_text)
                                if not embedding:
                                    continue
                            except Exception as e:
                                logger.warning(f"⚠️ {record_id} embedding oluşturulamadı: {e}")
                                continue

                            # Veritabanına kaydet - güvenli
                            try:
                                self.cur.execute(f"""
                                    INSERT INTO {embedding_table} 
                                    (id, product_id, product_name, combined_text, embedding)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (
                                    f"{table_name}_{record_id}",
                                    str(record_id),
                                    product_name[:100] if product_name else str(record_id),
                                    combined_text[:1000],
                                    embedding
                                ))

                                processed += 1

                                # Her 3 kayıtta commit
                                if processed % 3 == 0:
                                    self.conn.commit()

                            except Exception as e:
                                logger.warning(f"⚠️ {record_id} kaydetme hatası: {e}")
                                self.conn.rollback()
                                errors += 1
                                continue

                            # Rate limiting
                            time.sleep(0.05)

                        except Exception as e:
                            logger.warning(f"⚠️ Satır işleme hatası: {e}")
                            errors += 1
                            continue

                    # Batch sonrası güvenli commit
                    try:
                        self.conn.commit()
                    except:
                        self.conn.rollback()

                    # Progress
                    if processed % 10 == 0 or processed < 20:
                        logger.info(f"📊 {table_name}: {processed}/{total_records} işlendi")

                    offset += batch_size

                    # Güvenlik: çok fazla hata varsa dur
                    if errors > 50:
                        logger.warning(f"⚠️ Çok fazla hata ({errors}), {table_name} için durduruluyor")
                        break

                except Exception as e:
                    logger.error(f"❌ {table_name} batch hatası: {e}")
                    self.conn.rollback()
                    offset += batch_size
                    continue

            # Final commit
            try:
                self.conn.commit()
            except:
                pass

            logger.info(f"✅ {table_name}: {processed} embedding oluşturuldu")
            return processed

        except Exception as e:
            logger.error(f"❌ {table_name} işleme hatası: {e}")
            try:
                self.conn.rollback()
            except:
                pass
            return 0

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        logger.info("🚀 BULLETPROOF EMBEDDING BAŞLIYOR...")

        # Veritabanına bağlan
        if not self.connect_database():
            return False

        # Embedding servisi başlat
        if not self.init_embedding_service():
            return False

        # Tabloları al
        tables = self.get_tables()
        if not tables:
            logger.error("❌ Hiç tablo bulunamadı!")
            return False

        # Her tabloyu işle
        total_embeddings = 0
        successful_tables = 0

        for table_name in tables:
            try:
                logger.info(f"\n🔧 {table_name} işleniyor...")

                embeddings_count = self.process_table(table_name)

                if embeddings_count > 0:
                    total_embeddings += embeddings_count
                    successful_tables += 1
                    logger.info(f"✅ {table_name}: BAŞARILI ({embeddings_count} embedding)")
                else:
                    logger.warning(f"⚠️ {table_name}: BAŞARISIZ")

            except Exception as e:
                logger.error(f"❌ {table_name} genel hatası: {e}")
                continue

        # Özet
        logger.info("\n" + "=" * 60)
        logger.info("📊 BULLETPROOF EMBEDDING ÖZETİ")
        logger.info("=" * 60)
        logger.info(f"📦 Toplam tablo: {len(tables)}")
        logger.info(f"✅ Başarılı tablo: {successful_tables}")
        logger.info(f"❌ Başarısız tablo: {len(tables) - successful_tables}")
        logger.info(f"🧠 Toplam embedding: {total_embeddings}")

        if total_embeddings > 0:
            logger.info("🎉 EN AZ BAZI EMBEDDINGS OLUŞTURULDU!")
            logger.info("💡 Şimdi main_app.py çalıştırabilirsin!")
            return True
        else:
            logger.error("❌ HİÇ EMBEDDING OLUŞTURULAMADI!")
            return False


def main():
    """Ana fonksiyon"""
    bulletproof = BulletproofEmbeddings()

    try:
        return bulletproof.run()
    except Exception as e:
        logger.error(f"❌ Kritik hata: {e}")
        return False
    finally:
        # Cleanup
        try:
            if bulletproof.cur:
                bulletproof.cur.close()
            if bulletproof.conn:
                bulletproof.conn.close()
        except:
            pass


if __name__ == "__main__":
    print("🛡️ BULLETPROOF EMBEDDING STARTING...")

    if main():
        print("✅ BAŞARILI! EN AZ BAZI EMBEDDINGS OLUŞTURULDU!")
    else:
        print("❌ BAŞARISIZ! AMA SISTEM ÇÖKMEDI!")

    print("🎯 Her durumda main_app.py dene!")