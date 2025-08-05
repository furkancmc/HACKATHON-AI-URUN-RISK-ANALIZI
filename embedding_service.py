# embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        """Embedding servisi başlat"""
        logger.info("🔄 Embedding model yükleniyor...")

        # Türkçe destekli model
        try:
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ Embedding model yüklendi")
        except Exception as e:
            logger.error(f"❌ Model yükleme hatası: {e}")
            raise

    def create_embedding(self, text: str) -> List[float]:
        """Tek text için embedding oluştur"""
        try:
            if not text or text.strip() == "":
                return [0.0] * 384  # Boş text için sıfır embedding

            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Embedding oluşturma hatası: {e}")
            return [0.0] * 384

    def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Çoklu text için batch embedding"""
        try:
            logger.info(f"🔄 {len(texts)} text için batch embedding oluşturuluyor...")

            # Boş textleri temizle
            clean_texts = [text if text and text.strip() else "boş metin" for text in texts]

            embeddings = self.model.encode(clean_texts, show_progress_bar=True)
            result = embeddings.tolist()

            logger.info(f"✅ {len(result)} embedding oluşturuldu")
            return result
        except Exception as e:
            logger.error(f"❌ Batch embedding hatası: {e}")
            return [[0.0] * 384 for _ in texts]

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """İki embedding arasındaki cosine similarity"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Cosine similarity hesapla
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Similarity hesaplama hatası: {e}")
            return 0.0

    def test_embedding(self):
        """Test fonksiyonu"""
        test_text = "Apple iPhone kulaklık test"
        embedding = self.create_embedding(test_text)

        print(f"Test text: {test_text}")
        print(f"Embedding boyutu: {len(embedding)}")
        print(f"İlk 5 değer: {embedding[:5]}")

        return len(embedding) == 384  # Model boyutu kontrolü


# Test için
if __name__ == "__main__":
    service = EmbeddingService()
    service.test_embedding()