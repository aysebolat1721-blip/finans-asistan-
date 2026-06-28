# 💰 AI Agent Tabanlı Kişisel Finans & Harcama Asistanı (v1.0 MVP)

Bu proje, kullanıcının serbest metin olarak girdiği finansal verileri (banka SMS'leri, alışveriş notları, faturalar veya el yazısı günlük harcama kayıtları vb.) yapay zeka ajanları vasıtasıyla işleyen bir kişisel finans asistanıdır. Google Gemini ve Groq (Llama 3) modellerini bir arada kullanarak yüksek erişilebilirlik ve akıllı finansal içgörüler sunar.

---

## 🎯 Ne Yapar?

- **Harcama Kalemlerini Ayıklar:** Serbest metinden harcama adlarını ve tutarlarını ayrıştırır.
- **Akıllı Kategorizasyon:** Harcamaları *kira, yemek, ulaşım, eğlence, abonelik ve diğer* olmak üzere 6 kategoriye ayırır.
- **Finansal Sağlık & Bütçe Analizi:** İsteğe bağlı olarak girilen aylık gelire göre 50/30/20 bütçe kuralını uygular ve harcama sağlık skorunu hesaplar.
- **Görsel Grafikler:** Plotly entegrasyonu sayesinde harcama dağılımını pasta ve bar grafiklerle görselleştirir.
- **Tasarruf Önerileri:** Harcama alışkanlıklarınıza göre uygulanabilir, kişiselleştirilmiş 3-7 adet tasarruf tavsiyesi sunar.

---

## 🏗️ Mimari & Çalışma Akışı

AI Ajanı ardışık (sequential) bir pipeline şeklinde çalışır. Ajanın adımları şu şekildedir:

```
                  +-----------------------------------+
                  |  Kullanıcı Serbest Metin Girdisi  |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |      Adım 1: Harcama Ayıklama     | (prompts.get_extraction_prompt)
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |     Adım 2: Kategori Eşleme       | (prompts.get_categorization_prompt)
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |     Adım 3: Harcama Analizi       | (prompts.get_analysis_prompt)
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |    Adım 4: Tasarruf Önerileri     | (prompts.get_suggestion_prompt)
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |    Görsel Dashboard & Raporlama   | (Streamlit Arayüzü)
                  +-----------------------------------+
```

### 🔄 Modeller Arası Fallback (Yedekleme) Mekanizması
Ajanımız hata toleranslıdır. Birincil model olan **Google Gemini 1.5 Flash**'ta kota aşımı (rate limit) veya ağ hatası yaşandığında sistem otomatik olarak **Groq Llama 3 (8B)** modeline bağlanarak analizi kesintisiz tamamlar.

---

## 📁 Proje Dosya Yapısı

```
02 proje/
├── .env.example            # Örnek ortam değişkenleri şablonu
├── .env                    # Gerçek API anahtarlarının tutulduğu dosya (git'e eklenmez)
├── requirements.txt        # Gerekli kütüphaneler listesi
├── README.md               # Proje dökümantasyonu (bu dosya)
│
├── backend/
│   ├── __init__.py
│   ├── prompts.py          # LLM prompt şablonları
│   ├── agent.py            # Ajan akış denetleyicisi (FinanceAgent)
│   └── app.py              # FastAPI REST API sunucusu
│
└── frontend/
    └── streamlit_app.py    # Streamlit kullanıcı arayüzü ve grafikler
```

---

## ⚙️ Kurulum & Yerel Çalıştırma

### Gereksinimler
- Python 3.11 veya üzeri
- Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/)'dan ücretsiz alabilirsiniz)
- Groq API Key ([Groq Console](https://console.groq.com/)'dan ücretsiz alabilirsiniz)

### Adım Adım Kurulum

1. **Projeyi indirin/kullanın:**
   Proje dizinine geçin:
   ```bash
   cd "02 proje"
   ```

2. **Sanal Ortam (Virtual Environment) Oluşturun:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux için
   # Windows için: venv\Scripts\activate
   ```

3. **Gerekli Paketleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ortam Değişkenlerini Yapılandırın:**
   `.env` dosyasını oluşturun ve API anahtarlarınızı yazın:
   ```bash
   cp .env.example .env
   ```
   `.env` dosyasını açıp API keylerinizi düzenleyin:
   ```env
   GEMINI_API_KEY=AIzaSy...
   GROQ_API_KEY=gsk_...
   BACKEND_URL=http://localhost:8000
   ```

5. **FastAPI Backend Sunucusunu Başlatın:**
   ```bash
   python backend/app.py
   ```
   Backend varsayılan olarak `http://localhost:8000` adresinde çalışacaktır. API belgelerine `http://localhost:8000/docs` adresinden erişebilirsiniz.

6. **Streamlit Frontend Arayüzünü Başlatın (Ayrı bir terminalde):**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```
   Arayüz otomatik olarak tarayıcınızda açılacaktır (genellikle `http://localhost:8501`).

---

## 🚀 Streamlit Cloud Deployment Rehberi

Streamlit Cloud üzerinde FastAPI sunucusu doğrudan çalıştırılamaz. Bu sorunu çözmek için arayüze **"Doğrudan Ajan (Direct Mode)"** entegre edilmiştir. Bu mod aktif edildiğinde Streamlit doğrudan `FinanceAgent` sınıfını içeri aktararak analizleri kendi süreci içinde yürütür.

### Adımlar:
1. Projeyi kendi GitHub reponuza yükleyin ( `.env` dosyasını reponuza **eklemeyin**).
2. [share.streamlit.io](https://share.streamlit.io) adresine giderek GitHub hesabınızla giriş yapın.
3. **Deploy an App** butonuna tıklayın, ilgili repoyu ve `frontend/streamlit_app.py` dosyasını ana dosya olarak seçin.
4. **Advanced Settings** butonuna tıklayın ve Secrets bölümüne API anahtarlarınızı şu formatta ekleyin:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   GROQ_API_KEY = "gsk_..."
   ```
5. **Deploy** butonuna tıklayın. Uygulamanız canlıya alındığında sol menüden çalışma modunu "Doğrudan Ajan (Direct Mode)" olarak ayarlayarak kullanmaya başlayabilirsiniz.

---

## 📝 Örnek Kullanım Girdisi

```txt
Bu ay ev sahibi kirayı 14000 TL yaptı. Fatura ödemelerine 1200 TL verdim. Market alışverişleri için toplamda 3200 TL harcamışım. Netflix aboneliği 140 TL, Spotify 60 TL. Hafta sonu arkadaşlarla dışarıda yemek yedik 900 TL tuttu.
```

Ajan bu girdiden şunları üretir:
- **Ayıklama:** Her kalemi ve tutarı eşleştirir.
- **Kategori:** Kirayı "kira" kategorisine, Netflix'i "abonelik" kategorisine vb. atar.
- **Grafikler:** Harcama paylarını pasta grafik olarak çizer.
- **Analiz:** En çok harcamanın kira ve markette olduğunu tespit eder.
- **Öneri:** "Aboneliklerinizi gözden geçirin", "Dışarıda yemek yerine evde pişirmeyi deneyin" gibi maddeli tavsiyeler verir.

---

## 🛠️ Kullanılan Teknolojiler

- **Python 3.11** - Çekirdek programlama dili
- **FastAPI** - Yüksek performanslı backend REST API
- **Streamlit** - Hızlı ve modern web arayüzü geliştirme
- **Google Gemini API (1.5 Flash)** - Birincil LLM
- **Groq API (Llama 3 8B)** - Hızlı yedek (fallback) LLM
- **Plotly** - Dinamik, interaktif veri görselleştirme grafikleri
- **Pydantic** - Güvenli veri şeması doğrulama
- **python-dotenv** - Güvenli ortam değişkenleri yönetimi
