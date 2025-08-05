# main_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rag_service import RAGService
from gemini_service import GeminiService
import json

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🤖 AI Satıcı Risk Analiz Sistemi",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }

    .search-result {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }

    .similarity-score {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_services():
    """Servisleri başlat (cache ile)"""
    try:
        rag_service = RAGService()
        gemini_service = GeminiService()
        return rag_service, gemini_service
    except Exception as e:
        st.error(f"❌ Servis başlatma hatası: {e}")
        return None, None


def main():
    """Ana uygulama"""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Destekli Satıcı Risk Analiz Sistemi</h1>
        <p>Satıcılar için akıllı ürün risk analizi, karlılık değerlendirmesi ve satış stratejileri</p>
    </div>
    """, unsafe_allow_html=True)

    # Servisleri başlat
    rag_service, gemini_service = initialize_services()

    if not rag_service or not gemini_service:
        st.error("❌ Sistem servisleri başlatılamadı!")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🎛️ Kontrol Paneli")

        # Sistem durumu
        st.subheader("📊 Sistem Durumu")

        with st.spinner("Sistem bilgileri yükleniyor..."):
            try:
                stats = rag_service.get_table_stats()

                total_products = sum(s['total_products'] for s in stats.values())
                total_embeddings = sum(s['embeddings_count'] for s in stats.values())
                avg_coverage = sum(s['embedding_coverage'] for s in stats.values()) / len(stats) if stats else 0

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Toplam Ürün", total_products)
                    st.metric("Embedding Sayısı", total_embeddings)

                with col2:
                    st.metric("Tablo Sayısı", len(stats))
                    st.metric("Ortalama Kapsama", f"%{avg_coverage:.1f}")

                # Tablo detayları
                st.subheader("📋 Tablo Detayları")
                for table_name, table_stats in stats.items():
                    with st.expander(f"📦 {table_name.title().replace('_', ' ')}"):
                        st.write(f"**Ürün Sayısı:** {table_stats['total_products']}")
                        st.write(f"**Embedding:** {table_stats['embeddings_count']}")
                        st.write(f"**Kapsama:** %{table_stats['embedding_coverage']}")
                        st.write(f"**Ort. Fiyat:** ₺{table_stats['avg_price']:.2f}")
                        st.write(f"**Ort. Rating:** {table_stats['avg_rating']:.2f}⭐")

            except Exception as e:
                st.error(f"❌ Sistem bilgileri alınamadı: {e}")

        # Gelişmiş filtreler
        st.subheader("🔧 Gelişmiş Filtreler")

        price_range = st.slider(
            "💰 Fiyat Aralığı (₺)",
            min_value=0,
            max_value=100000,
            value=(0, 100000),
            step=1000
        )

        min_rating = st.slider(
            "⭐ Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.1
        )

        selected_brands = st.multiselect(
            "🏷️ Markalar",
            options=["Samsung", "LG", "Arçelik", "Vestel", "Bosch", "Siemens"],
            default=[]
        )

        search_limit = st.slider(
            "📊 Sonuç Sayısı",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )

    # Ana içerik
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Ürün Risk Arama", "📊 Satış Dashboard", "🤖 AI Satış Danışmanı", "⚙️ Sistem Yönetimi"])

    # TAB 1: Ürün Risk Arama
    with tab1:
        st.header("🔍 Ürün Risk Analizi ve Arama")

        # Arama formu
        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "🔎 Hangi ürün için risk analizi yapmak istiyorsunuz?",
                placeholder="Örn: Samsung inverter klima, iPhone kulaklık, LG buzdolabı...",
                help="Ürün adı yazın, AI risk analizi ile birlikte en uygun sonuçları bulacak."
            )

        with col2:
            search_button = st.button("🚀 Risk Analizi Yap", type="primary", use_container_width=True)

        # Risk analizi sonuçları
        if search_query and search_button:
            with st.spinner("🤖 AI risk analizi yapıyor..."):
                try:
                    # Filtreleri hazırla
                    filters = {}
                    if price_range != (0, 100000):
                        filters['price_min'] = price_range[0]
                        filters['price_max'] = price_range[1]
                    if min_rating > 0:
                        filters['rating_min'] = min_rating
                    if selected_brands:
                        filters['brands'] = selected_brands

                    # Arama yap
                    results = rag_service.search_with_filters(
                        search_query,
                        filters=filters if filters else None,
                        limit=search_limit
                    )
                    
                    # Debug bilgisi
                    st.info(f"🔍 Arama sorgusu: '{search_query}'")
                    st.info(f"📊 Filtreler: {filters}")
                    st.info(f"📋 Bulunan sonuç sayısı: {len(results) if results else 0}")

                    if results:
                        st.success(f"✅ {len(results)} ürün bulundu!")

                        # Sonuçları göster
                        for i, result in enumerate(results, 1):
                            with st.container():
                                st.markdown(f"""
                                <div class="search-result">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <h4>#{i} {result['product_name']}</h4>
                                        <span class="similarity-score">%{result['similarity'] * 100:.1f} uygun</span>
                                    </div>
                                """, unsafe_allow_html=True)

                                col1, col2, col3 = st.columns([2, 1, 1])

                                with col1:
                                    if 'product_details' in result:
                                        details = result['product_details']
                                        st.write(f"**Marka:** {details.get('brand', 'N/A')}")
                                        st.write(f"**Kaynak:** {result['source_table'].replace('_', ' ').title()}")

                                        # Açıklama kısmı
                                        description = details.get('seller_description', '') or details.get(
                                            'description', '')
                                        if description:
                                            st.write(f"**Açıklama:** {description[:200]}...")

                                with col2:
                                    if 'product_details' in result:
                                        details = result['product_details']
                                        price = details.get('price', 0)
                                        rating = details.get('rating', 0)

                                        if price and float(price) > 0:
                                            st.metric("💰 Fiyat", f"₺{float(price):,.2f}")

                                        if rating and float(rating) > 0:
                                            st.metric("⭐ Rating", f"{float(rating):.1f}/5")

                                with col3:
                                    # Detay butonu
                                    if st.button(f"📋 Detayları Gör", key=f"detail_{i}"):
                                        st.session_state[f'show_detail_{i}'] = True

                                    # AI analiz butonu
                                    if st.button(f"🤖 Risk Analizi", key=f"ai_{i}"):
                                        st.session_state[f'show_analysis_{i}'] = True

                                st.markdown("</div>", unsafe_allow_html=True)

                                # Detay görüntüleme
                                if st.session_state.get(f'show_detail_{i}', False):
                                    with st.expander(f"📋 {result['product_name']} - Detaylı Bilgiler", expanded=True):
                                        # Ürün detaylarını getir
                                        product_details = rag_service.get_product_details(
                                            result['product_id'], 
                                            result['source_table']
                                        )
                                        
                                        if product_details:
                                            # Risk analizi bilgilerini öne çıkar
                                            if 'risk_analysis' in product_details:
                                                st.subheader("⚠️ Risk Analizi")
                                                risk_info = product_details['risk_analysis']
                                                
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    st.metric("🎯 Genel Risk", f"{risk_info['overall_risk']}/10")
                                                with col2:
                                                    st.metric("📊 Risk Seviyesi", risk_info['risk_level'])
                                                with col3:
                                                    st.metric("💰 Fiyat Riski", f"{risk_info['price_risk']:.1f}/10")
                                                
                                                st.info(f"💡 **Satıcı Önerisi:** {risk_info['seller_recommendation']}")
                                            
                                            # Tüm ürün bilgileri
                                            st.subheader("📊 Tüm Ürün Bilgileri")
                                            st.json(product_details)
                                            
                                            # Kapat butonu
                                            if st.button(f"❌ Kapat", key=f"close_detail_{i}"):
                                                st.session_state[f'show_detail_{i}'] = False
                                                st.rerun()
                                        else:
                                            st.error("❌ Ürün detayları yüklenemedi")

                                # AI Risk Analizi
                                if st.session_state.get(f'show_analysis_{i}', False):
                                    with st.expander(f"🤖 {result['product_name']} - Satıcı Risk Analizi", expanded=True):
                                        with st.spinner("🧠 Risk analizi yapılıyor..."):
                                            try:
                                                # Ürün detaylarını getir
                                                product_details = rag_service.get_product_details(
                                                    result['product_id'], 
                                                    result['source_table']
                                                )
                                                
                                                if product_details:
                                                    # Risk analizi için context hazırla
                                                    risk_data = product_details.get('risk_analysis', {})
                                                    
                                                    context = f"""
                                                    ÜRÜN BİLGİLERİ:
                                                    - Ürün Adı: {result['product_name']}
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
                                                    {json.dumps(product_details, ensure_ascii=False, indent=2)}
                                                    """

                                                    # AI analiz promptu
                                                    query = f"Bu ürün için satıcı risk analizi yap: {result['product_name']}"

                                                    analysis = gemini_service.analyze_product_with_context(
                                                        query, context, ""
                                                    )
                                                    st.markdown(analysis)
                                                    
                                                    # Kapat butonu
                                                    if st.button(f"❌ Kapat", key=f"close_analysis_{i}"):
                                                        st.session_state[f'show_analysis_{i}'] = False
                                                        st.rerun()
                                                else:
                                                    st.error("❌ Ürün detayları yüklenemedi")

                                            except Exception as e:
                                                st.error(f"❌ AI analiz hatası: {e}")
                    else:
                        st.warning("🤔 Arama kriterlerinize uygun ürün bulunamadı. Farklı terimler deneyin.")

                        # Önerilen aramalar
                        st.info(
                            "💡 **Öneri:** 'Samsung klima', 'enerji verimli buzdolabı', '18000 BTU inverter' gibi spesifik terimler deneyin.")

                except Exception as e:
                    st.error(f"❌ Arama hatası: {e}")

    # TAB 2: Satış Dashboard
    with tab2:
        st.header("📊 Satıcı Dashboard - Risk ve Karlılık Analizi")

        try:
            stats = rag_service.get_table_stats()

            # Genel metrikler
            col1, col2, col3, col4 = st.columns(4)

            total_products = sum(s['total_products'] for s in stats.values())
            total_embeddings = sum(s['embeddings_count'] for s in stats.values())
            avg_price = sum(s['avg_price'] * s['total_products'] for s in
                            stats.values()) / total_products if total_products > 0 else 0
            avg_rating = sum(s['avg_rating'] * s['total_products'] for s in
                             stats.values()) / total_products if total_products > 0 else 0

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{total_products:,}</h3>
                    <p>Toplam Ürün</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{total_embeddings:,}</h3>
                    <p>AI Embeddings</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>₺{avg_price:,.0f}</h3>
                    <p>Ortalama Fiyat</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{avg_rating:.1f}⭐</h3>
                    <p>Ortalama Rating</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Grafik alanı
            col1, col2 = st.columns(2)

            with col1:
                # Tablo bazında ürün dağılımı
                if stats:
                    df_tables = pd.DataFrame([
                        {
                            'Tablo': table_name.replace('_', ' ').title(),
                            'Ürün Sayısı': table_stats['total_products'],
                            'Embedding Kapsama': table_stats['embedding_coverage']
                        }
                        for table_name, table_stats in stats.items()
                    ])

                    fig = px.bar(
                        df_tables,
                        x='Tablo',
                        y='Ürün Sayısı',
                        title="📊 Tablo Bazında Ürün Dağılımı",
                        color='Embedding Kapsama',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Embedding kapsama grafiği
                if stats:
                    fig = px.pie(
                        df_tables,
                        values='Ürün Sayısı',
                        names='Tablo',
                        title="🥧 Ürün Dağılım Oranları"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Detaylı tablo
            st.subheader("📋 Detaylı İstatistikler")

            if stats:
                df_detailed = pd.DataFrame([
                    {
                        'Tablo': table_name.replace('_', ' ').title(),
                        'Toplam Ürün': table_stats['total_products'],
                        'Embedding Sayısı': table_stats['embeddings_count'],
                        'Kapsama (%)': f"{table_stats['embedding_coverage']:.1f}%",
                        'Ort. Fiyat (₺)': f"{table_stats['avg_price']:,.2f}",
                        'Ort. Rating': f"{table_stats['avg_rating']:.1f}⭐"
                    }
                    for table_name, table_stats in stats.items()
                ])

                st.dataframe(df_detailed, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Dashboard yüklenirken hata: {e}")

    # TAB 3: AI Asistan
    with tab3:
        st.header("🤖 AI Satış Danışmanı")

        st.markdown("""
        **Satıcı odaklı AI danışmanınız size yardımcı olmaya hazır!** 

        Ürünler hakkında risk analizi, satış stratejileri, fiyatlandırma önerileri ve rekabet analizi yapabilirsiniz.
        
        **Örnek Sorular:**
        - "Bu ürünü satmak riskli mi?"
        - "Hangi ürünler daha karlı?"
        - "Fiyat stratejim nasıl olmalı?"
        - "Rekabet durumu nasıl?"
        """)

        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant",
                 "content": "Merhaba! 👋 Ben sizin satış danışmanınızım. Ürün risk analizleri, satış stratejileri, fiyatlandırma önerileri ve rekabet durumu hakkında sorularınızı yanıtlayabilirim. Size nasıl yardımcı olabilirim?"}
            ]

        # Mesaj geçmişi
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Yeni mesaj
        if user_input := st.chat_input("Sorunuzu yazın..."):
            # Kullanıcı mesajını ekle
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            # AI yanıtı
            with st.chat_message("assistant"):
                with st.spinner("🤖 Düşünüyorum..."):
                    try:
                        # Önce ürün araması yap
                        search_results = rag_service.search_products(user_input, limit=5)

                        # Kontext oluştur
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
                        
                        Satıcı sorusu: {user_input}

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
                        st.markdown(response)

                        # Yanıtı kaydet
                        st.session_state.messages.append({"role": "assistant", "content": response})

                    except Exception as e:
                        error_msg = f"❌ Üzgünüm, bir hata oluştu: {e}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Hazır sorular - Satıcı odaklı
        st.markdown("### 💡 Satıcı İçin Örnek Sorular")
        example_questions = [
            "Hangi ürünleri satmak daha karlı?",
            "Samsung klimalar için risk analizi yap",
            "Yüksek fiyatlı ürünlerin satış riski nedir?",
            "Düşük rating'li ürünleri satmalı mıyım?",
            "Rekabet yoğun kategoriler hangileri?"
        ]

        cols = st.columns(len(example_questions))
        for i, question in enumerate(example_questions):
            with cols[i]:
                if st.button(question, key=f"example_{i}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()

    # TAB 4: Sistem Yönetimi
    with tab4:
        st.header("⚙️ Sistem Yönetimi")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔧 Sistem Durumu")

            # Sistem testleri
            if st.button("🧪 Sistem Testlerini Çalıştır"):
                with st.spinner("Testler çalışıyor..."):
                    try:
                        # RAG testi
                        test_results = rag_service.search_products("test", limit=1)
                        rag_status = "✅ Çalışıyor" if test_results is not None else "❌ Hata"

                        # Gemini testi
                        test_response = gemini_service.generate_response("Test")
                        gemini_status = "✅ Çalışıyor" if test_response else "❌ Hata"

                        # Veritabanı testi
                        stats = rag_service.get_table_stats()
                        db_status = "✅ Çalışıyor" if stats else "❌ Hata"

                        st.success("Test sonuçları:")
                        st.write(f"**RAG Servisi:** {rag_status}")
                        st.write(f"**Gemini AI:** {gemini_status}")
                        st.write(f"**Veritabanı:** {db_status}")

                    except Exception as e:
                        st.error(f"Test hatası: {e}")

            # Bellek temizleme
            if st.button("🧹 Cache Temizle"):
                st.cache_resource.clear()
                st.success("✅ Cache temizlendi!")
                st.rerun()

        with col2:
            st.subheader("📊 Performans Metrikleri")

            try:
                stats = rag_service.get_table_stats()

                # Performans göstergeleri
                if stats:
                    total_embeddings = sum(s['embeddings_count'] for s in stats.values())
                    total_products = sum(s['total_products'] for s in stats.values())

                    st.metric("Embedding Verimliliği",
                              f"%{(total_embeddings / total_products * 100) if total_products > 0 else 0:.1f}")
                    st.metric("Aktif Tablolar", len(stats))
                    st.metric("Sistem Sağlığı", "🟢 İyi" if len(stats) > 0 else "🔴 Sorunlu")

            except Exception as e:
                st.error(f"Metrik hatası: {e}")

        # Sistem logları
        st.subheader("📝 Sistem Logları")

        if st.checkbox("Detaylı Log Göster"):
            st.text_area(
                "Son sistem aktiviteleri:",
                value="[INFO] Sistem başlatıldı\n[INFO] RAG servisi aktif\n[INFO] Gemini AI bağlantısı başarılı\n[INFO] Dashboard yüklendi",
                height=200,
                disabled=True
            )


if __name__ == "__main__":
    main()