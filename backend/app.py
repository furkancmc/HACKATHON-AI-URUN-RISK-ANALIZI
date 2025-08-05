# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rag_service import RAGService
    from gemini_service import GeminiService  
    from create_missing_embeddings import EmbeddingCreator
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("Ana dizindeki Python dosyalarına erişilemiyor.")
    print("Backend'i ana dizinden çalıştırmayı deneyin: python backend/app.py")
    sys.exit(1)
import logging
import json
from decimal import Decimal

# JSON serializer for various types
def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    from datetime import datetime, date
    import numpy as np
    
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, '__dict__'):
        return str(obj)
    
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

app = Flask(__name__)
CORS(app)  # React frontend için CORS'u etkinleştir

# Flask JSON encoder'ını Decimal destekleyecek şekilde ayarla
app.json.default = json_serializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Servisleri başlat
try:
    rag_service = RAGService()
    gemini_service = GeminiService()
    embedding_creator = EmbeddingCreator()
    logger.info("✅ Tüm servisler başlatıldı")
except Exception as e:
    logger.error(f"❌ Servis başlatma hatası: {e}")
    rag_service = None
    gemini_service = None
    embedding_creator = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sistem durumu kontrolü"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'rag_service': rag_service is not None,
            'gemini_service': gemini_service is not None,
            'embedding_creator': embedding_creator is not None
        }
    })

@app.route('/api/tables/stats', methods=['GET'])
def get_table_stats():
    """Tablo istatistiklerini getir"""
    try:
        if not rag_service:
            return jsonify({'error': 'RAG service not available'}), 500
            
        stats = rag_service.get_table_stats()
        
        # React için uygun format
        formatted_stats = []
        for table_name, table_data in stats.items():
            formatted_stats.append({
                'name': table_name.replace('_', ' ').title(),
                'total_products': table_data['total_products'],
                'embeddings_count': table_data['embeddings_count'],
                'avg_price': table_data['avg_price'],
                'avg_rating': table_data['avg_rating'],
                'embedding_coverage': table_data['embedding_coverage']
            })
        
        return jsonify({
            'success': True,
            'data': formatted_stats,
            'total_tables': len(formatted_stats)
        })
        
    except Exception as e:
        logger.error(f"❌ Tablo istatistik hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """Tüm markaları getir"""
    try:
        if not rag_service:
            return jsonify({'error': 'RAG service not available'}), 500
            
        brands = rag_service.get_all_brands()
        
        return jsonify({
            'success': True,
            'data': brands
        })
        
    except Exception as e:
        logger.error(f"❌ Marka listesi hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/sales-data', methods=['GET'])
def get_sales_data():
    """Dashboard için satış verilerini getir"""
    try:
        if not rag_service:
            return jsonify({'error': 'RAG service not available'}), 500
            
        sales_data = rag_service.get_sales_data_for_dashboard()
        
        return jsonify({
            'success': True,
            'data': sales_data
        })
        
    except Exception as e:
        logger.error(f"❌ Satış verileri hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_products():
    """Ürün arama ve risk analizi"""
    try:
        if not rag_service:
            return jsonify({'error': 'RAG service not available'}), 500
            
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Arama yap
        results = rag_service.search_with_filters(query, filters, limit)
        
        # React için format düzenle
        formatted_results = []
        for result in results:
            formatted_result = {
                'id': result['product_id'],
                'name': result['product_name'],
                'similarity': result['similarity'],
                'source_table': result['source_table'],
                'combined_text': result.get('combined_text', ''),
                'details': result.get('product_details', {}),
                'risk_analysis': result.get('product_details', {}).get('risk_analysis', {})
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'success': True,
            'data': formatted_results,
            'total': len(formatted_results),
            'query': query,
            'filters': filters
        })
        
    except Exception as e:
        logger.error(f"❌ Arama hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/product/<product_id>/details', methods=['GET'])
def get_product_details(product_id):
    """Ürün detaylarını getir"""
    try:
        if not rag_service:
            return jsonify({'error': 'RAG service not available'}), 500
            
        source_table = request.args.get('source_table')
        if not source_table:
            return jsonify({'error': 'source_table is required'}), 400
        
        details = rag_service.get_product_details(product_id, source_table)
        
        if not details:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'success': True,
            'data': details
        })
        
    except Exception as e:
        logger.error(f"❌ Ürün detay hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze_product():
    """AI ile ürün risk analizi"""
    try:
        if not gemini_service or not rag_service:
            return jsonify({'error': 'AI services not available'}), 500
            
        data = request.json
        product_id = data.get('product_id')
        source_table = data.get('source_table')
        query = data.get('query', 'Bu ürün için risk analizi yap')
        
        if not product_id or not source_table:
            return jsonify({'error': 'product_id and source_table are required'}), 400
        
        # Ürün detaylarını al
        product_details = rag_service.get_product_details(product_id, source_table)
        
        if not product_details:
            return jsonify({'error': 'Product not found'}), 404
        
        # AI analizi için context hazırla
        risk_data = product_details.get('risk_analysis', {})
        
        context = f"""
        ÜRÜN BİLGİLERİ:
        - Ürün Adı: {product_details.get('name', 'N/A')}
        - Fiyat: {product_details.get('price', 'N/A')} TL
        - Rating: {product_details.get('rating', 'N/A')}/5
        - Marka: {product_details.get('brand', 'N/A')}
        
        RİSK ANALİZİ:
        - Genel Risk Skoru: {risk_data.get('overall_risk', 'N/A')}/10
        - Fiyat Riski: {risk_data.get('price_risk', 'N/A')}/10
        - Rating Riski: {risk_data.get('rating_risk', 'N/A')}/10
        - Rekabet Riski: {risk_data.get('competition_risk', 'N/A')}/10
        - Risk Seviyesi: {risk_data.get('risk_level', 'N/A')}
        - Satıcı Önerisi: {risk_data.get('seller_recommendation', 'N/A')}
        
        TÜM ÜRÜN VERİLERİ:
        {json.dumps(product_details, ensure_ascii=False, indent=2, default=json_serializer)}
        """
        
        # AI analizi yap
        analysis = gemini_service.analyze_product_with_context(query, context, "")
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis,
                'product_details': product_details,
                'risk_analysis': risk_data
            }
        })
        
    except Exception as e:
        logger.error(f"❌ AI analiz hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI ile sohbet"""
    try:
        if not gemini_service or not rag_service:
            return jsonify({'error': 'AI services not available'}), 500
            
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # İlgili ürünleri ara
        search_results = rag_service.search_products(message, limit=5)
        
        # Context oluştur
        context = ""
        if search_results:
            context = "İlgili ürünler:\n"
            for i, result in enumerate(search_results, 1):
                context += f"{i}. {result['product_name']} (Benzerlik: {result['similarity']:.2f})\n"
                if 'product_details' in result:
                    details = result['product_details']
                    context += f"   - Fiyat: ₺{details.get('price', 'N/A')}\n"
                    context += f"   - Marka: {details.get('brand', 'N/A')}\n"
                    context += f"   - Rating: {details.get('rating', 'N/A')}\n\n"
        
        # Satıcı odaklı AI prompt
        prompt = f"""
        Sen uzman bir e-ticaret satış danışmanısın. Satıcıya yönelik tavsiyelerde bulun.
        
        Satıcı sorusu: {message}

        İlgili ürün verileri:
        {context}

        SATIÇI PERSPEKTİFİNDEN yanıt ver:
        - Risk analizleri yap
        - Karlılık değerlendirmesi sun
        - Satış stratejileri öner
        - Rekabet durumunu analiz et
        - Fiyatlandırma tavsiyeleri ver
        
        Türkçe, profesyonel ve satıcı odaklı bir dille cevap ver.
        """
        
        response = gemini_service.generate_response(prompt)
        
        return jsonify({
            'success': True,
            'data': {
                'response': response,
                'context_products': len(search_results) if search_results else 0
            }
        })
        
    except Exception as e:
        logger.error(f"❌ AI sohbet hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/create', methods=['POST'])
def create_embeddings():
    """Eksik embedding'leri oluştur"""
    try:
        if not embedding_creator:
            return jsonify({'error': 'Embedding creator not available'}), 500
            
        # Embedding oluşturma işlemini başlat
        embedding_creator.create_missing_embeddings()
        
        return jsonify({
            'success': True,
            'message': 'Embedding creation process started'
        })
        
    except Exception as e:
        logger.error(f"❌ Embedding oluşturma hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_services():
    """Servisleri test et"""
    try:
        results = {}
        
        # RAG service test
        if rag_service:
            try:
                tables = rag_service.get_available_tables()
                results['rag_service'] = {
                    'status': 'ok',
                    'tables': len(tables),
                    'table_names': tables
                }
            except Exception as e:
                results['rag_service'] = {'status': 'error', 'error': str(e)}
        else:
            results['rag_service'] = {'status': 'not_available'}
        
        # Gemini service test
        if gemini_service:
            try:
                test_response = gemini_service.generate_response("Test mesajı")
                results['gemini_service'] = {
                    'status': 'ok',
                    'response_length': len(test_response) if test_response else 0
                }
            except Exception as e:
                results['gemini_service'] = {'status': 'error', 'error': str(e)}
        else:
            results['gemini_service'] = {'status': 'not_available'}
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"❌ Test hatası: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)