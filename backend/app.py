# -*- coding: utf-8 -*-
"""
FastAPI REST API Sunucusu (app.py)
Kişisel finans analiz ajanı için API uç noktalarını sağlar.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ajan denetleyicisini içe aktar
try:
    from backend.agent import FinanceAgent
except ImportError:
    from agent import FinanceAgent

# FastAPI Uygulaması
app = FastAPI(
    title="AI Personal Finance Agent API",
    description="Kullanıcı metinlerinden harcamaları ayıklayan, kategorize eden, analiz eden ve tasarruf önerileri sunan API.",
    version="1.0"
)

# CORS Ayarları (Streamlit ve diğer istemcilerin bağlanabilmesi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Ajan Örneği (Her istekte yeniden oluşturmak yerine bir kez oluşturup önbellekliyoruz)
try:
    agent = FinanceAgent()
except Exception as e:
    print(f"⚠️ Ajan başlatılamadı. API anahtarlarınızı kontrol edin: {str(e)}")
    agent = None

# Pydantic İstek Modeli
class AnalyzeRequest(BaseModel):
    user_input: str = Field(
        ...,
        min_length=10,
        description="Analiz edilecek finansal metin (SMS, el yazısı notu vb.)",
        json_schema_extra={"example": "Bu ay kira 7500 TL, market alışverişi 3400 TL, Spotify aboneliği 59 TL ve Netflix 139 TL ödedim."}
    )

# Pydantic Yanıt Modeli
class AnalyzeResponse(BaseModel):
    status: str = Field(..., description="Analiz durumu (success veya error)")
    extracted_expenses: str = Field(..., description="Ayıklanmış harcamalar")
    categorized_expenses: str = Field(..., description="Kategorize edilmiş harcamalar")
    analysis: str = Field(..., description="Harcama analizi ve riskler")
    suggestions: str = Field(..., description="Tasarruf önerileri")

@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Harcama Verisini Analiz Et",
    description="Kullanıcı metninden 4 aşamalı AI finans analizini yürüterek sonuçları döner."
)
async def analyze_expense(request: AnalyzeRequest):
    """
    Kullanıcı metnini alır, finans ajanını çalıştırır ve 4 aşamalı analizin sonuçlarını döner.
    """
    global agent
    if agent is None:
        # Eğer başlangıçta hata aldıysa, her istekte tekrar kurmayı dene (canlı ortam güncellemeleri için)
        try:
            agent = FinanceAgent()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI Finans Ajanı başlatılamadı: {str(e)}"
            )

    # Ajan analizini çalıştır
    result = agent.analyze(request.user_input)

    # Hata durumunu kontrol et
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Bilinmeyen bir AI analiz hatası oluştu.")
        )

    return AnalyzeResponse(
        status=result["status"],
        extracted_expenses=result["extracted_expenses"],
        categorized_expenses=result["categorized_expenses"],
        analysis=result["analysis"],
        suggestions=result["suggestions"]
    )

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Sağlık Kontrolü",
    description="API'nin çalışır durumda olup olmadığını kontrol eder."
)
async def health_check():
    """
    API'nin durumunu kontrol eden basit endpoint.
    """
    return {"status": "ok", "message": "Finans Asistanı API'si çalışıyor."}

if __name__ == "__main__":
    # FastAPI uygulamasını uvicorn ile başlat
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
