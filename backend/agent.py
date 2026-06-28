# -*- coding: utf-8 -*-
"""
Kişisel Finans AI Agent Controller
Bu dosya, finansal analiz akışını yönetir ve Gemini ile Groq API bağlantılarını kontrol eder.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

# Modül import yollarını destekle (Streamlit direct mod ve FastAPI mod desteği)
try:
    from backend.prompts import (
        SYSTEM_PROMPT,
        get_extraction_prompt,
        get_categorization_prompt,
        get_analysis_prompt,
        get_suggestion_prompt
    )
except ImportError:
    try:
        from prompts import (
            SYSTEM_PROMPT,
            get_extraction_prompt,
            get_categorization_prompt,
            get_analysis_prompt,
            get_suggestion_prompt
        )
    except ImportError:
        # Streamlit'in import yoluna destek
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from prompts import (
            SYSTEM_PROMPT,
            get_extraction_prompt,
            get_categorization_prompt,
            get_analysis_prompt,
            get_suggestion_prompt
        )

# .env dosyasını yükle
load_dotenv()

class FinanceAgent:
    def __init__(self):
        """
        Gemini ve Groq API istemcilerini hazırlar ve çevresel değişkenleri yükler.
        """
        # API Anahtarlarını Al
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Gemini Kurulumu
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=SYSTEM_PROMPT
            )
            print("🤖 Gemini API Client başarıyla oluşturuldu.")
        else:
            self.gemini_model = None
            print("⚠️ UYARI: GEMINI_API_KEY bulunamadı. Gemini devre dışı.")

        # Groq Kurulumu
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            print("🤖 Groq API Client başarıyla oluşturuldu.")
        else:
            self.groq_client = None
            print("⚠️ UYARI: GROQ_API_KEY bulunamadı. Groq devre dışı.")

    def _call_llm(self, prompt: str) -> str:
        """
        Öncelikle Gemini API'sini çağırır. Başarısız olursa Groq API (Llama 3) ile fallback yapar.
        """
        # 1. Gemini Denemesi
        if self.gemini_model:
            try:
                print("🔄 Gemini (gemini-2.0-flash) çağrılıyor...")
                response = self.gemini_model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
                raise Exception("Gemini'den boş yanıt döndü.")
            except Exception as e:
                print(f"⚠️ Gemini başarısız oldu. Hata: {str(e)}")
                print("🔄 Groq API fallback devreye giriyor...")
        else:
            print("⚠️ Gemini yapılandırılmadığı için doğrudan Groq kullanılacak.")

        # 2. Groq (Llama 3) Fallback Denemesi
        if self.groq_client:
            try:
                print("🔄 Groq (llama-3.1-8b-instant) çağrılıyor...")
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.2,
                )
                if chat_completion.choices and chat_completion.choices[0].message.content:
                    return chat_completion.choices[0].message.content.strip()
                raise Exception("Groq'tan boş yanıt döndü.")
            except Exception as e:
                print(f"❌ Groq API de başarısız oldu. Hata: {str(e)}")
                raise Exception(f"Her iki LLM de yanıt vermedi. Son hata: {str(e)}")
        else:
            raise Exception("Kullanılabilir aktif bir LLM API anahtarı bulunamadı (.env dosyanızı kontrol edin).")

    def analyze(self, user_input: str) -> dict:
        """
        Ham kullanıcı girdisini alıp 4 aşamalı pipeline'ı yürütür.
        """
        print("\n🚀 AI Finans Asistanı Analiz Süreci Başlatıldı...")
        try:
            # Adım 1: Harcama Ayıklama (Extraction)
            print("⏳ Adım 1/4: Harcama kalemleri ayıklanıyor...")
            extraction_prompt = get_extraction_prompt(user_input)
            extracted_expenses = self._call_llm(extraction_prompt)
            print("✅ Adım 1 tamamlandı: Harcamalar ayıklandı.")
            
            # Adım 2: Kategorizasyon (Categorization)
            print("⏳ Adım 2/4: Harcamalar kategorilere ayrılıyor...")
            categorization_prompt = get_categorization_prompt(extracted_expenses)
            categorized_expenses = self._call_llm(categorization_prompt)
            print("✅ Adım 2 tamamlandı: Harcamalar kategorize edildi.")
            
            # Adım 3: Analiz (Analysis)
            print("⏳ Adım 3/4: Harcamalar analiz ediliyor...")
            analysis_prompt = get_analysis_prompt(categorized_expenses)
            analysis_result = self._call_llm(analysis_prompt)
            print("✅ Adım 3 tamamlandı: Harcamalar analiz edildi.")
            
            # Adım 4: Öneriler (Suggestions)
            print("⏳ Adım 4/4: Tasarruf önerileri oluşturuluyor...")
            suggestion_prompt = get_suggestion_prompt(analysis_result)
            suggestions = self._call_llm(suggestion_prompt)
            print("✅ Adım 4 tamamlandı: Tasarruf önerileri oluşturuldu.")
            
            print("🎉 Analiz süreci başarıyla tamamlandı!\n")
            return {
                "status": "success",
                "extracted_expenses": extracted_expenses,
                "categorized_expenses": categorized_expenses,
                "analysis": analysis_result,
                "suggestions": suggestions
            }

        except Exception as e:
            print(f"❌ Analiz sürecinde hata oluştu: {str(e)}\n")
            return {
                "status": "error",
                "message": str(e)
            }

# Test amaçlı doğrudan çalıştırma desteği
if __name__ == "__main__":
    agent = FinanceAgent()
    test_input = "Kira için 12000 TL, market alışverişi 3200 TL, Netflix 140 TL ve dün akşam dışarıda yemek için 750 TL harcadım."
    result = agent.analyze(test_input)
    print("Test Sonucu:", result)
