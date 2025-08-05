# gemini_service.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
import time

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        """Gemini API servisini başlat"""
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY çevre değişkeni bulunamadı! .env dosyasını kontrol et.")

        # Gemini'yi yapılandır
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        logger.info("✅ Gemini API başlatıldı")

    def analyze_product_with_context(
            self,
            user_query: str,
            context: str,
            user_product_info: str = ""
    ) -> str:
        """Satıcı için ürün risk analizi yap"""

        system_prompt = """
Sen uzman bir SATICI KOÇU ve e-ticaret strateji danışmanısın. 

SATICI'nın satışlarını artırması ve karlılığını maksimize etmesi için KAPSAMLI STRATEJİK ANALİZ yapacaksın.
Veritabanındaki tüm veriler ve risk skorları kullanılarak satıcıya özel tavsiyeler sun.

📊 SATICI KOÇLUK ANALİZ FORMATI:

## 🎯 ÜRÜN SATIŞ POTANSİYELİ
- Bu ürünü satmanın avantajları ve dezavantajları
- Pazar talebi ve büyüme potansiyeli
- Satış yapılabilirlik skoru ve gerekçesi

## 📈 FİYATLANDIRMA & REKABET STRATEJİSİ
- Optimal fiyat aralığı önerisi
- Rekabet analizi ve farklılaşma fırsatları
- Dinamik fiyatlandırma stratejileri

## ⚠️ SATICI İÇİN KRİTİK RİSKLER
- Fiyat riski ve piyasa pozisyonu
- Müşteri memnuniyeti ve rating etkisi
- Rekabet yoğunluğu ve pazar payı
- Stok yönetimi ve talep tahmini

## 💰 KARLILIK OPTİMİZASYONU
- Tahmini kar marjı ve optimizasyon önerileri
- Satış hızı artırma stratejileri
- Yatırım geri dönüş süresi ve ROI
- Risk/getiri dengesi

## 🚀 SATICI EYLEM PLANI
- Haftalık/aylık satış hedefleri
- Pazarlama ve promosyon stratejileri
- Stok yönetimi ve tedarik planı
- Müşteri hizmetleri ve destek stratejisi

## ⚡ SATICI KARARI
- 🟢 HEMEN BAŞLA / 🟡 HAZIRLIK YAP / 🔴 BEKLE
- Öncelik seviyesi: YÜKSEK/ORTA/DÜŞÜK
- İlk 30 günlük aksiyon planı

ÖNEMLİ: 
- Satıcı perspektifinden koçluk yap
- Somut ve uygulanabilir öneriler ver
- Sayısal hedefler ve KPI'lar belirle
- Rekabet avantajı yaratma stratejileri sun
- Türkçe ve motivasyonel dil kullan
"""

        user_prompt = f"""
🔍 KULLANICI SORUSU: {user_query}

{f"🛍️ KULLANICI ÜRÜN BİLGİSİ: {user_product_info}" if user_product_info else ""}

📊 VERİTABANINDAN BULUNAN BENZER ÜRÜNLER:
{context}

Lütfen yukarıdaki format ile kapsamlı analiz yap ve kullanıcıya en iyi stratejik önerileri sun.
"""

        try:
            logger.info("🔄 Gemini API'ye analiz isteği gönderiliyor...")

            # Rate limiting için kısa bekleme
            time.sleep(0.5)

            response = self.model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                    top_p=0.9,
                    top_k=40
                )
            )

            if response and response.text:
                logger.info("✅ Gemini API analizi tamamlandı")
                return response.text
            else:
                logger.error("❌ Gemini API boş yanıt döndü")
                return "❌ Analiz sırasında bir sorun oluştu. Lütfen tekrar deneyin."

        except Exception as e:
            logger.error(f"❌ Gemini API hatası: {e}")
            return f"❌ Analiz sırasında hata oluştu: {str(e)}"

    def generate_quick_summary(self, products: List[Dict[str, Any]]) -> str:
        """Hızlı ürün özeti oluştur"""

        products_info = ""
        for i, product in enumerate(products[:3], 1):  # İlk 3 ürün
            products_info += f"""
{i}. {product['product_name']}
   - Fiyat: {product['price']} TL
   - Rating: {product['rating']}/5
   - Risk: {product['risk_score']}/10
   - Benzerlik: %{product.get('similarity_score', 0) * 100:.1f}
"""

        prompt = f"""
Aşağıdaki ürünler için KISA bir özet yap:

{products_info}

Format:
📋 ÖZET:
- En uygun seçenek: [ürün adı ve nedeni]
- Ortalama fiyat aralığı: [min-max TL]
- Genel risk seviyesi: [düşük/orta/yüksek]
- Öneriler: [2-3 kısa madde]

Maksimum 300 kelime.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else "Özet oluşturulamadı."
        except Exception as e:
            logger.error(f"❌ Özet oluşturma hatası: {e}")
            return "Özet oluşturma sırasında hata oluştu."

    def generate_response(self, prompt: str) -> str:
        """Satıcı odaklı yanıt oluştur"""
        try:
            logger.info("🔄 Gemini API'ye satıcı koçluk isteği gönderiliyor...")
            
            # Satıcı odaklı sistem prompt'u ekle
            system_prompt = """
Sen uzman bir SATICI KOÇU'sun. Kullanıcılar satıcı ve sen onların satışlarını artırmalarına, 
karlılıklarını maksimize etmelerine ve rekabet avantajı elde etmelerine yardımcı oluyorsun.

Yanıtlarında:
- Satıcı perspektifinden konuş
- Somut ve uygulanabilir öneriler ver
- Sayısal hedefler ve KPI'lar belirle
- Motivasyonel ve destekleyici ol
- Türkçe kullan
- Satış stratejileri, fiyatlandırma, stok yönetimi, müşteri hizmetleri konularında tavsiye ver
"""
            
            full_prompt = f"{system_prompt}\n\nKULLANICI SORUSU: {prompt}\n\nSATICI KOÇU YANITI:"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                    top_p=0.9,
                    top_k=40
                )
            )
            
            if response and response.text:
                logger.info("✅ Satıcı koçluk yanıtı alındı")
                return response.text
            else:
                logger.error("❌ Gemini API boş yanıt döndü")
                return "❌ Yanıt oluşturulamadı. Lütfen tekrar deneyin."
                
        except Exception as e:
            logger.error(f"❌ Gemini API hatası: {e}")
            return f"❌ Yanıt oluşturma hatası: {str(e)}"

    def test_api(self):
        """API test fonksiyonu"""
        try:
            test_prompt = "Bu bir test mesajıdır. 'Test başarılı' yanıtını ver."
            response = self.model.generate_content(test_prompt)

            if response and response.text:
                print("✅ Gemini API test başarılı!")
                print(f"Yanıt: {response.text}")
                return True
            else:
                print("❌ Gemini API test başarısız - boş yanıt")
                return False

        except Exception as e:
            print(f"❌ Gemini API test hatası: {e}")
            return False


# Test için
if __name__ == "__main__":
    service = GeminiService()
    service.test_api()