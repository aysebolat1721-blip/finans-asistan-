# -*- coding: utf-8 -*-
"""
Kişisel Finans AI Agent Prompt Şablonları
Bu dosya, finansal verileri işleyen ajanımızın farklı aşamalardaki prompt şablonlarını içerir.
"""

# Deneyimli bir finans danışmanı rolündeki ana sistem promptu
SYSTEM_PROMPT = """Sen deneyimli bir kişisel finans danışmanısın.
Kullanıcıların harcama alışkanlıklarını analiz eder, gereksiz giderleri tespit eder ve net, uygulanabilir tasarruf önerileri sunarsın.
Cevapların açık, maddeli, profesyonel ve sade olmalıdır. Türkçe yanıt vermelisin.
Karşılaştırma veya analiz yaparken para birimlerini (özellikle TL / ₺) tutarlı ve doğru şekilde kullan."""


def get_extraction_prompt(user_input: str) -> str:
    """
    Kullanıcının girdiği ham metinden harcama kalemlerini ve tutarlarını ayıklayan prompt.
    """
    return f"""Aşağıdaki ham metinden harcama kalemlerini ve tutarlarını ayıkla.

Kurallar:
- Tutarı olmayan kalemler için tutar tahmini yapma, "belirtilmemiş" yaz.
- Para birimlerini standart hale getir (örneğin: "TL", "lira", "₺" -> "TL" yap).
- Çıktıyı SADECE aşağıdaki formatta ver, ek açıklama veya giriş/gelişme cümleleri ekleme.

Format:
Kalem: [isim] | Tutar: [değer veya "belirtilmemiş"]

Ham Metin:
{user_input}"""


def get_categorization_prompt(expense_list: str) -> str:
    """
    Ayıklanmış harcama listesini belirlenen kategorilere ayıran prompt.
    """
    return f"""Aşağıdaki harcama listesini analiz et ve şu kategorilerden en uygun olanına ata:
Kategoriler: kira, yemek, ulaşım, eğlence, abonelik, diğer

Kurallar:
- Her harcamayı sadece bir kategoriye ata.
- Listelenen kategoriler dışında yeni kategori oluşturma.
- Çıktı formatına kesinlikle sadık kal, başka hiçbir metin veya açıklama ekleme.
- Çıktıda harcama kalemlerinin yanındaki tutar bilgilerini koru.

Format:
Kategori: [kategori adı]
- Kalem: [isim] | Tutar: [değer]
- Kalem: [isim] | Tutar: [değer]

Harcama Listesi:
{expense_list}"""


def get_analysis_prompt(categorized_data: str) -> str:
    """
    Kategorize edilmiş harcama verilerinden analiz raporu oluşturan prompt.
    """
    return f"""Aşağıdaki kategorize edilmiş harcama verilerini analiz et.

Senden istenenler:
1. En yüksek harcama yapılan ilk 3 alanı (kategoriyi veya kalemi) belirle ve analiz et.
2. Riskli, gereksiz veya bütçeyi zorlayan harcama kalemlerini tespit et.
3. Kullanıcının genel harcama örüntüsü/davranışı hakkında kısa ve yapıcı bir yorum yap.

Analiz edilecek veriler:
{categorized_data}"""


def get_suggestion_prompt(analysis_result: str) -> str:
    """
    Finansal analiz sonucuna göre net ve uygulanabilir tasarruf önerileri üreten prompt.
    """
    return f"""Aşağıdaki harcama analizi sonuçlarına dayanarak kullanıcıya özel tasarruf önerileri üret.

Kurallar:
- Öneriler net, somut ve maddeler halinde yazılmalıdır.
- Gerçekçi ve günlük hayatta kolayca uygulanabilir öneriler olmalıdır.
- En az 3, en fazla 7 öneri sun.
- Her öneriyi neden sunduğunu, kullanıcının hangi harcamasıyla ilişkili olduğunu kısaca açıkla.
- Üslubun motive edici ve yapıcı olsun.

Analiz Sonuçları:
{analysis_result}"""
