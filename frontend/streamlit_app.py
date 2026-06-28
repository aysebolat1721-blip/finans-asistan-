# -*- coding: utf-8 -*-
"""
AI Kişisel Finans Asistanı Streamlit Arayüzü (streamlit_app.py)
Kullanıcılara harcama analizi, görsel grafikler ve tasarruf önerileri sunan modern arayüz.
"""

import streamlit as st
import requests
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Root dizinini sys.path'e ekle (backend klasörüne erişebilmek için)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AI Kişisel Finans Asistanı",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS (Aesthetics & Animations)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Font ve Arka Plan */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Başlık Alanı Gradiyenti */
    .title-gradient {
        background: linear-gradient(135deg, #8A2387 0%, #E94057 50%, #F27121 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        color: #718096;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Glassmorphism Kart Tasarımı */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Buton Micro-Animation */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
        transition: all 0.3s ease-in-out;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(118, 75, 162, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        color: white;
    }
    
    div.stButton > button:first-child:active {
        transform: translateY(1px);
    }
    
    /* Tab Tasarımları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #a0aec0;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Test Senaryoları (Section 5.1)
TEST_SCENARIOS = {
    "Seçiniz...": "",
    "🎓 Öğrenci Senaryosu (Düşük gelir, yüksek eğlence)": 
        "Aylık harçlığım 4000 TL. Bu ay yurt ücretine 1200 TL verdim. Kahve zincirlerinde ve kafelerde 1100 TL harcamışım. Netflix aboneliği 140 TL, Spotify 60 TL. Kitap ve kırtasiyeye 350 TL verdim. Hafta sonu konser bileti için 800 TL ödedim. Yemekhane dışındaki yemeklere ise 600 TL gitti.",
    "💼 Çalışan Senaryosu (Orta gelir, düzenli giderler)": 
        "Ev kirası olarak 15000 TL ödedim. Aidat 750 TL. Bu ay Migros market alışverişim 4800 TL tuttu. İşe gidiş geliş yol ücretim ve benzin toplamda 3200 TL. Elektrik ve internet faturalarına 1300 TL ödedim. Hafta sonu tiyatro ve akşam yemeğine 1800 TL harcadım. Spor salonu üyeliği 1200 TL.",
    "📱 Banka SMS Formatı": 
        "Sayin Uye, 24/06/2026 14:32 tarihli Hepsiburada harcamaniz 2350.00 TL. 25/06/2026 19:10 tarihli Migros harcamaniz 1240.50 TL. 25/06/2026 21:05 tarihli Shell benzin harcamaniz 1500.00 TL. 26/06/2026 09:15 tarihli Netflix harcamaniz 139.99 TL.",
    "✍️ Dağınık / Serbest Metin": 
        "Dostlar bu ay ipin ucu kaçtı. Ev sahibine 14 bin yolladım. Arabanın yıllık bakımı ve kış lastiği değişimi için servise 7800 TL bıraktım. Dün çocukların okul kıyafetleri ve kırtasiye malzemeleri için 2400 TL harcadık. Eşimle dışarıda yediğimiz akşam yemekleri de 1900 TL'yi bulmuş. Abonelikleri unuttum, Youtube premium 80 lira, BluTV 100 lira gitmiş.",
    "🌐 Karışık Dil (Türkçe - İngilizce)": 
        "This month expenditures: Rent fee 11000 TL. Market shopping for food 3500 TL. Bus tickets and taxi 1200 TL. Cinema and concerts total cost is 1800 ₺. I paid my AWS cloud subscription 450 TL. gym membership için 900 TL ödeme yaptım."
}

# Sidebar Alanı
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953423.png", width=80)
    st.markdown("### 💰 AI Finans Asistanı")
    st.write("Serbest metin halindeki harcama verilerinizi analiz eden akıllı finansal agent.")
    
    st.markdown("---")
    
    # Çalışma Modu Seçimi
    run_mode = st.radio(
        "🖥️ Çalışma Modu",
        ["FastAPI Backend", "Doğrudan Ajan (Direct Mode)"],
        help="FastAPI backend üzerinden veya doğrudan Streamlit içerisinden analiz yapar."
    )
    
    if run_mode == "FastAPI Backend":
        backend_url = st.text_input("🔗 Backend API URL", value="http://localhost:8000")
    else:
        backend_url = None
        st.info("Direct Mode: FastAPI sunucusuna ihtiyaç duymadan doğrudan API anahtarlarıyla çalışır.")
        
    st.markdown("---")
    
    # API Key Overrides
    st.markdown("🔑 **API Anahtarları**")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="Boş bırakılırsa .env kullanılır")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="Boş bırakılırsa .env kullanılır")
    
    # Set Keys in Environment if provided
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
        
    st.markdown("---")
    st.markdown("### 📚 Nasıl Çalışır?")
    st.markdown("""
    1. Harcama metninizi yazın veya örneklerden seçin.
    2. İsteğe bağlı olarak aylık gelirinizi girin.
    3. **Analiz Et** butonuna tıklayın.
    4. AI ajanının aşamalı analizini ve grafiklerini inceleyin.
    """)

# Ana İçerik
st.markdown('<div class="title-gradient">AI Finans Danışmanı Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Serbest metin notları, faturalar veya banka SMS\'lerini akıllı harcama raporlarına dönüştürün.</div>', unsafe_allow_html=True)

# Örnek Senaryo Yükleyici
selected_scenario = st.selectbox("💡 Örnek Senaryo Yükle", list(TEST_SCENARIOS.keys()))
default_text = ""
if selected_scenario != "Seçiniz...":
    default_text = TEST_SCENARIOS[selected_scenario]

# Form Alanı
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_area(
            "📝 Harcama Detaylarını Girin",
            value=default_text,
            placeholder="Örnek: Bu ay kira 7500 TL, Migros 1800 TL, Spotify 59 TL, Netflix 139 TL, benzin 800 TL ödedim...",
            height=150
        )
    with col2:
        monthly_income = st.number_input(
            "💼 Aylık Net Gelir (TL - Opsiyonel)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            help="Bütçe analizi ve tasarruf oranlarının hesaplanması için kullanılır."
        )
    
    analyze_clicked = st.button("🔍 Harcamaları Analiz Et", type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Helper Function to Call Local Finance Agent (Direct Mode)
def call_agent_directly(text: str) -> dict:
    try:
        from backend.agent import FinanceAgent
        agent = FinanceAgent()
        return agent.analyze(text)
    except Exception as e:
        return {"status": "error", "message": f"Doğrudan Ajan Modu Başlatılamadı: {str(e)}"}

# Helper Function to Call API (Backend Mode)
def call_api(text: str, api_url: str) -> dict:
    try:
        response = requests.post(
            f"{api_url}/analyze",
            json={"user_input": text},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"API Hata Kodu {response.status_code}: {response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Backend API bağlantı hatası: {str(e)}"}

# Parser for Expense Text to DataFrame
def parse_categorized_expenses(categorized_text: str):
    expenses = []
    current_category = "diğer"
    
    lines = categorized_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Kategori kontrolü
        cat_match = re.search(r"Kategori:\s*([a-zA-ZçıiğgöoşsüşIİĞÖŞÜ]+)", line, re.IGNORECASE)
        if cat_match:
            current_category = cat_match.group(1).lower().strip()
            continue
            
        # Kalem kontrolü: - Kalem: [isim] | Tutar: [değer]
        # Veya - [isim] | Tutar: [değer]
        item_match = re.search(r"-\s*(?:Kalem:\s*)?([^|]+)\|\s*Tutar:\s*([^|]+)", line, re.IGNORECASE)
        if item_match:
            item_name = item_match.group(1).strip()
            tutar_str = item_match.group(2).strip()
            
            # Sayısal değeri çek
            num_match = re.search(r"([\d\.,\s]+)", tutar_str)
            if num_match:
                # Boşlukları temizle, binlik ayıracı kaldır, ondalığı noktaya çevir
                clean_num = num_match.group(1).replace(" ", "").replace(".", "").replace(",", ".")
                try:
                    amount = float(clean_num)
                except ValueError:
                    amount = 0.0
            else:
                amount = 0.0
                
            expenses.append({
                "Category": current_category.capitalize(),
                "Item": item_name,
                "Amount": amount
            })
    return pd.DataFrame(expenses)

# Processing Analysis
if analyze_clicked:
    if len(user_input.strip()) < 10:
        st.error("⚠️ Lütfen analizin başlayabilmesi için en az 10 karakterlik bir harcama metni girin.")
    else:
        with st.spinner("🤖 AI Ajanı finansal verilerinizi analiz ediyor, lütfen bekleyin..."):
            if run_mode == "FastAPI Backend":
                result = call_api(user_input, backend_url)
            else:
                result = call_agent_directly(user_input)
                
        if result.get("status") == "success":
            st.balloons()
            st.success("✅ Analiz başarıyla tamamlandı!")
            
            # Parse expenses for charts
            df_expenses = parse_categorized_expenses(result["categorized_expenses"])
            total_spent = df_expenses["Amount"].sum() if not df_expenses.empty else 0.0
            
            # --- TOP METRICS PANEL ---
            st.markdown("### 📊 Genel Finansal Özet")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            
            with m_col1:
                st.metric("Toplam Harcama", f"{total_spent:,.2f} TL")
            with m_col2:
                if monthly_income > 0:
                    savings = monthly_income - total_spent
                    st.metric("Kalan Bütçe / Tasarruf", f"{savings:,.2f} TL", delta=f"{(savings/monthly_income)*100:.1f}% Tasarruf Oranı")
                else:
                    st.metric("Kalan Bütçe", "Gelir Belirtilmedi")
            with m_col3:
                # Calculate Health Score (Section 6.1)
                if monthly_income > 0:
                    savings_ratio = (monthly_income - total_spent) / monthly_income
                    if savings_ratio >= 0.2:
                        health_score = int(80 + min(20, (savings_ratio - 0.2) * 100))
                    elif savings_ratio >= 0:
                        health_score = int(50 + savings_ratio * 150)
                    else:
                        health_score = max(0, int(50 + savings_ratio * 50))
                else:
                    # Estimate based on categories count and risky items
                    risky_count = result["analysis"].lower().count("risk") + result["analysis"].lower().count("gereksiz")
                    health_score = max(10, 80 - (risky_count * 12))
                
                st.metric("Finansal Sağlık Skoru", f"{health_score} / 100")
            with m_col4:
                top_cat = "Yok"
                if not df_expenses.empty:
                    top_cat = df_expenses.groupby("Category")["Amount"].sum().idxmax()
                st.metric("En Yüksek Harcama Grubu", top_cat)
            
            # --- VISUALIZATIONS SECTION (Section 6.1) ---
            if not df_expenses.empty and total_spent > 0:
                st.markdown("---")
                st.markdown("### 📈 Harcama Dağılımı ve Grafikler")
                g_col1, g_col2 = st.columns(2)
                
                with g_col1:
                    # 1. Pasta Grafik (Kategorilere Göre Harcama Dağılımı)
                    df_cat = df_expenses.groupby("Category")["Amount"].sum().reset_index()
                    fig_pie = px.pie(
                        df_cat, 
                        values='Amount', 
                        names='Category', 
                        title='Kategorilere Göre Harcama Dağılımı',
                        color_discrete_sequence=px.colors.sequential.RdBu,
                        hole=0.4
                    )
                    fig_pie.update_layout(margin=dict(t=40, b=20, l=20, r=20))
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with g_col2:
                    # 2. Bar Grafik (En yüksek harcama kalemleri)
                    df_sorted = df_expenses.sort_values(by="Amount", ascending=False).head(5)
                    fig_bar = px.bar(
                        df_sorted,
                        x='Amount',
                        y='Item',
                        orientation='h',
                        title='En Yüksek 5 Harcama Kalemi',
                        labels={'Amount': 'Tutar (TL)', 'Item': 'Harcama Kalemi'},
                        color='Amount',
                        color_continuous_scale='Purples'
                    )
                    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=40, b=20, l=20, r=20))
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                # 3. Gauge Grafik - Finansal Sağlık Skoru
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = health_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Harcama Sağlık Skoru", 'font': {'size': 20}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "#764ba2"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': '#ffccd5'},
                            {'range': [50, 80], 'color': '#ffe3e0'},
                            {'range': [80, 100], 'color': '#d8f3dc'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': health_score
                        }
                    }
                ))
                fig_gauge.update_layout(height=250, margin=dict(t=60, b=20, l=20, r=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # --- BUDGET COMPARISON SECTION (50/30/20 Rule) ---
                if monthly_income > 0:
                    st.markdown("### 💼 Bütçe Analizi (50/30/20 Kuralı)")
                    
                    # Group items into Needs, Wants, Savings
                    # Needs: Kira, Yemek, Ulaşım
                    # Wants: Eğlence, Abonelik, Diğer
                    needs_cats = ["Kira", "Yemek", "Ulaşım"]
                    wants_cats = ["Eğlence", "Abonelik", "Diğer"]
                    
                    needs_total = df_expenses[df_expenses["Category"].isin(needs_cats)]["Amount"].sum()
                    wants_total = df_expenses[df_expenses["Category"].isin(wants_cats)]["Amount"].sum()
                    savings_total = max(0, monthly_income - total_spent)
                    
                    needs_pct = (needs_total / monthly_income) * 100
                    wants_pct = (wants_total / monthly_income) * 100
                    savings_pct = (savings_total / monthly_income) * 100
                    
                    b_col1, b_col2, b_col3 = st.columns(3)
                    
                    with b_col1:
                        st.markdown("**İhtiyaçlar (Kira, Yemek, Ulaşım)**")
                        st.write(f"Mevcut: **{needs_total:,.2f} TL** ({needs_pct:.1f}%)")
                        st.progress(min(1.0, needs_total / (monthly_income * 0.5)))
                        st.caption("Hedef: Maksimum 50% (İdeal bütçe dilimi)")
                        if needs_pct > 50:
                            st.warning("⚠️ İhtiyaç harcamalarınız bütçenizin yarısını aşmış.")
                        else:
                            st.success("✅ İhtiyaç harcamaları bütçe sınırı içinde.")
                            
                    with b_col2:
                        st.markdown("**İstekler (Eğlence, Abonelik, Diğer)**")
                        st.write(f"Mevcut: **{wants_total:,.2f} TL** ({wants_pct:.1f}%)")
                        st.progress(min(1.0, wants_total / (monthly_income * 0.3)))
                        st.caption("Hedef: Maksimum 30% (Keyfi harcamalar)")
                        if wants_pct > 30:
                            st.warning("⚠️ Keyfi harcamalarınız bütçe limitinin üzerinde. Kısıntı yapabilirsiniz.")
                        else:
                            st.success("✅ İstek harcamaları dengeli durumda.")
                            
                    with b_col3:
                        st.markdown("**Tasarruf ve Yatırım**")
                        st.write(f"Mevcut: **{savings_total:,.2f} TL** ({savings_pct:.1f}%)")
                        st.progress(min(1.0, savings_total / (monthly_income * 0.2)))
                        st.caption("Hedef: Minimum 20% (Geleceğe yatırım)")
                        if savings_pct < 20:
                            st.info("💡 Tasarruf oranınız %20'nin altında. Öneriler sekmesine göz atın.")
                        else:
                            st.success("🎉 Harika! Hedef tasarruf oranına ulaştınız.")
            
            # --- DETAILED ANALYSIS TABS ---
            st.markdown("---")
            st.markdown("### 🔍 Detaylı AI Ajan Analiz Sonuçları")
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Harcama Listesi", 
                "🗂️ Kategoriler", 
                "📈 Analiz & Riskler", 
                "💡 Tasarruf Önerileri"
            ])
            
            with tab1:
                st.markdown("#### Ayıklanmış Harcama Kalemleri")
                st.code(result["extracted_expenses"], language="txt")
                
            with tab2:
                st.markdown("#### Kategorilere Göre Dağılım")
                st.code(result["categorized_expenses"], language="txt")
                if not df_expenses.empty:
                    st.markdown("##### Veri Tablosu")
                    st.dataframe(df_expenses, use_container_width=True)
                
            with tab3:
                st.markdown("#### Risk ve Alışkanlık Analizi")
                st.info(result["analysis"])
                
            with tab4:
                st.markdown("#### Kişiselleştirilmiş Tasarruf Önerileri")
                st.success(result["suggestions"])
                
        else:
            st.error(f"❌ Hata: {result.get('message', 'Analiz yapılırken bilinmeyen bir hata oluştu.')}")

# Alt Bilgi / Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #a0aec0; font-size: 0.8rem;'>"
    "Bu uygulama Google Gemini 1.5 Flash ve Groq Llama 3 API'lerini kullanmaktadır.<br>"
    "AI Finans Ajanı v1.0 MVP | 2026"
    "</div>", 
    unsafe_allow_html=True
)
