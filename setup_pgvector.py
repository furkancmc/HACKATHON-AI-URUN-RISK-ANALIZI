# setup_pgvector_fixed.py
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection(port, container_name=""):
    """Bağlantıyı test et"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=port,
            database="urun_risk_analiz",
            user="postgres",
            password="furkan"
        )

        conn.autocommit = True
        cur = conn.cursor()

        logger.info(f"✅ PostgreSQL'e bağlandı (port {port}) {container_name}")

        # Extension kontrolü
        cur.execute("SELECT name FROM pg_available_extensions WHERE name = 'vector';")
        available = cur.fetchone()

        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        installed = cur.fetchone()

        if available:
            logger.info("📦 pgvector extension mevcut")
        else:
            logger.error("❌ pgvector extension mevcut değil!")

        if installed:
            logger.info("✅ pgvector extension kurulu")
        else:
            logger.warning("⚠️ pgvector extension kurulu değil, kuruluyor...")
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("✅ pgvector extension kuruldu!")
            except Exception as e:
                logger.error(f"❌ Extension kurma hatası: {e}")
                return False

        # Vector test
        try:
            logger.info("🧪 Vector test ediliyor...")
            cur.execute("""
                        CREATE
                        TEMP TABLE vector_test (
                    id SERIAL PRIMARY KEY,
                    embedding VECTOR(3)
                );
                        """)

            cur.execute("INSERT INTO vector_test (embedding) VALUES ('[1,2,3]');")
            cur.execute("SELECT embedding FROM vector_test;")
            result = cur.fetchone()

            logger.info(f"✅ Vector test başarılı: {result}")

        except Exception as e:
            logger.error(f"❌ Vector test başarısız: {e}")
            return False

        cur.close()
        conn.close()

        return True

    except Exception as e:
        logger.error(f"❌ PostgreSQL bağlantı hatası (port {port}): {e}")
        return False


def main():
    """Ana fonksiyon - Mevcut tüm PostgreSQL instance'larını test et"""

    print("🚀 PostgreSQL ve pgvector test ediliyor...")

    # Test edilecek portlar
    test_configs = [
        (5434, "- Yeni pgvector container"),
        (5433, "- Eski PostgreSQL"),
        (5432, "- Docker default port")
    ]

    success = False

    for port, description in test_configs:
        print(f"\n🔍 Port {port} test ediliyor {description}")

        if test_connection(port, description):
            print(f"✅ Port {port} başarılı! Bu portu kullanabilirsin.")
            success = True

            # Config dosyası oluştur
            with open("db_config.txt", "w") as f:
                f.write(f"WORKING_PORT={port}\n")
                f.write(f"HOST=localhost\n")
                f.write(f"DATABASE=urun_risk_analiz\n")
                f.write(f"USER=postgres\n")
                f.write(f"PASSWORD=furkan\n")

            print(f"📝 Çalışan port {port} db_config.txt dosyasına kaydedildi")
            break
        else:
            print(f"❌ Port {port} çalışmıyor")

    if success:
        print("\n🎉 pgvector hazır! Şimdi populate_embeddings.py'yi çalıştırabilirsin!")
        return True
    else:
        print("\n❌ Hiçbir PostgreSQL instance'ı bulunamadı!")
        print("💡 Docker container'ının çalıştığından emin ol:")
        print("   docker ps")
        return False


if __name__ == "__main__":
    main()