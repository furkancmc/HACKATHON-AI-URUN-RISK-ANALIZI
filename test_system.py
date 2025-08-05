# test_system.py
import sys
import logging
from rag_service import RAGService
from embedding_service import EmbeddingService
from gemini_service import GeminiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_service():
    """Embedding servisini test et"""
    print("\n🔍 Embedding Servisi Test Ediliyor...")
    
    try:
        service = EmbeddingService()
        
        # Test embedding oluştur
        test_text = "Samsung inverter klima 18000 BTU"
        embedding = service.create_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Embedding oluşturuldu (boyut: {len(embedding)})")
            print(f"📊 İlk 5 değer: {embedding[:5]}")
            return True
        else:
            print("❌ Embedding oluşturulamadı")
            return False
            
    except Exception as e:
        print(f"❌ Embedding servisi hatası: {e}")
        return False

def test_rag_service():
    """RAG servisini test et"""
    print("\n🔍 RAG Servisi Test Ediliyor...")
    
    try:
        rag = RAGService()
        
        # Mevcut tabloları kontrol et
        tables = rag.get_available_tables()
        print(f"📋 Embedding tabloları: {tables}")
        
        if not tables:
            print("⚠️ Hiç embedding tablosu bulunamadı")
            return False
        
        # İstatistikleri kontrol et
        stats = rag.get_table_stats()
        print(f"📊 Tablo istatistikleri: {len(stats)} tablo")
        
        for table_name, table_stats in stats.items():
            print(f"  📦 {table_name}: {table_stats['embeddings_count']} embedding")
        
        # Test araması
        test_query = "Samsung klima"
        results = rag.search_products(test_query, limit=3)
        
        if results:
            print(f"✅ Arama başarılı: {len(results)} sonuç")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['product_name']} (Benzerlik: {result['similarity']:.3f})")
            return True
        else:
            print("❌ Arama sonucu bulunamadı")
            return False
            
    except Exception as e:
        print(f"❌ RAG servisi hatası: {e}")
        return False

def test_gemini_service():
    """Gemini servisini test et"""
    print("\n🔍 Gemini Servisi Test Ediliyor...")
    
    try:
        gemini = GeminiService()
        
        # Test yanıtı
        test_prompt = "Merhaba, bu bir test mesajıdır."
        response = gemini.generate_response(test_prompt)
        
        if response and len(response) > 0:
            print(f"✅ Gemini yanıtı alındı (uzunluk: {len(response)})")
            print(f"📝 Yanıt: {response[:100]}...")
            return True
        else:
            print("❌ Gemini yanıtı alınamadı")
            return False
            
    except Exception as e:
        print(f"❌ Gemini servisi hatası: {e}")
        return False

def test_database_connection():
    """Veritabanı bağlantısını test et"""
    print("\n🔍 Veritabanı Bağlantısı Test Ediliyor...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host='localhost',
            port=5434,
            database='urun_risk_analiz',
            user='postgres',
            password='furkan'
        )
        
        cur = conn.cursor()
        
        # Tabloları listele
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tables = cur.fetchall()
        
        print(f"✅ Veritabanı bağlantısı başarılı")
        print(f"📋 Toplam tablo sayısı: {len(tables)}")
        
        # İlk 5 tabloyu göster
        for i, table in enumerate(tables[:5]):
            print(f"  {i+1}. {table[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 AI Ürün Arama Sistemi Test Ediliyor...")
    print("=" * 50)
    
    tests = [
        ("Veritabanı Bağlantısı", test_database_connection),
        ("Embedding Servisi", test_embedding_service),
        ("RAG Servisi", test_rag_service),
        ("Gemini Servisi", test_gemini_service)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test hatası: {e}")
            results[test_name] = False
    
    # Sonuçları özetle
    print("\n" + "=" * 50)
    print("📊 TEST SONUÇLARI:")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Genel Sonuç: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Sistem hazır.")
    else:
        print("⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 