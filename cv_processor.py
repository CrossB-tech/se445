import os
import json
import PyPDF2
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import requests
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def analyze_cv_with_gemini(cv_text):
    api_key = os.environ.get("Gemini_API")
    if not api_key:
        raise ValueError("Gemini_API eksik (.env dosyasını kontrol edin)")
        
    genai.configure(api_key=api_key)
    
    # Selecting the latest model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    Aşağıdaki CV metnini analiz et ve sonucu SADECE şu JSON formatında döndür. Hiçbir ek açıklama veya Markdown bloğu kullanma, katıksız bir JSON nesnesi olsun:
    {
      "isim": "Adayın Tam Adı",
      "email": "E-posta",
      "telefon": "Telefon",
      "yetenekler": "Anahtar yetenekler virgülle ayrılmış (max 5)",
      "seniority": "Junior veya Senior",
      "deneyim_yili": "Örn: 3",
      "egitim": "En son / En yüksek eğitim seviyesi (örn: Üniversite mezunu)",
      "siniflandirma": "screen, reject veya interview",
      "puan": "Adayın teknik puanı (0-100 arası bir sayı). Değerlendirme rolü: 'Full stack developer becerisi olucak react ve mongodb bilmesi lazım'. Bu role uygunluğa göre puanla.",
      "ozet": "Aday hakkında kısa bir değerlendirme özeti (max 2 cümle)"
    }
    
    Sınıflandırma Mantığı (Buna uymak KRİTİKTİR):
    - Adayın aranan role (React, MongoDB full stack) yetenekleri tam, deneyimi iyiyse sonucunu "interview" yap.
    - Adayın yetenekleri role potansiyel gösteriyor ama bazı eksikleri varsa veya ön görüşme yapmak gerekliyse "screen" yap.
    - Aday aranan rolden tamamen uzaksa "reject" yap.
    - Eğer CV'de isim, email, telefon, yetenekler, eğitim, deneyim yılı gibi alanlar bulunmuyorsa değerlerini boş bırak ("").
    
    CV Metni:
    """ + cv_text

    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean up markdown JSON wrapper
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    try:
        data = json.loads(response_text)
        return data
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {response_text}")
        raise ValueError("Gemini yanıtı geçerli bir JSON değil. Lütfen tekrar deneyin.")

def append_to_gsheet(data):
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    creds_file = os.environ.get("CREDENTIALS_FILE", "credentials.json")
    
    if not sheet_id or sheet_id == "GOOGLE_SHEET_ID":
        raise ValueError("Lütfen geçerli bir GOOGLE_SHEET_ID girin.")
        
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        credentials = Credentials.from_service_account_file(creds_file, scopes=scopes)
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(sheet_id).sheet1
        
        # Determine if headers exist
        try:
            headers = sheet.row_values(1)
        except Exception:
            headers = []
            
        expected_headers = ["İsim", "Email", "Telefon", "Yetenekler", "Seniority", "Deneyim Yılı", "Eğitim", "Sınıflandırma", "Puan", "Özet"]
        if not headers or headers != expected_headers:
            # If the sheet is completely empty or headers mismatch exactly, inject our standard headers
            sheet.insert_row(expected_headers, index=1)
            
        def get_val(key):
            val = str(data.get(key, "")).strip()
            return val if val else "Invalid"

        row_data = [
            get_val("isim"),
            get_val("email"),
            get_val("telefon"),
            get_val("yetenekler"),
            get_val("seniority"),
            get_val("deneyim_yili"),
            get_val("egitim"),
            get_val("siniflandirma"),
            get_val("puan"),
            get_val("ozet")
        ]
        
        sheet.append_row(row_data)
    except Exception as e:
        print(f"Google Sheets Hatası: {str(e)}")
        raise

def send_slack_notification(data):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url or webhook_url == "SLACK_WEBHOOK_URL":
        return
        
    message = {
        "text": f"🎉 *Yeni Bir Aday İncelendi!* 🎉\n"
                f"*İsim:* {data.get('isim', 'Bilinmiyor')}\n"
                f"*Sınıflandırma:* `{data.get('siniflandirma', 'Belirsiz').upper()}`\n"
                f"*Özet:* {data.get('ozet', '')}\n"
                f"*Yetenekler:* {data.get('yetenekler', '')}\n"
                f"Lütfen Google Sheets tablosunu kontrol edin."
    }
    
    try:
        requests.post(webhook_url, json=message)
    except Exception as e:
        print(f"Slack Bildirim Hatası: {e}")

def process_cv(filepath):
    # 1. Parse PDF
    text = extract_text_from_pdf(filepath)
    if not text.strip():
        raise ValueError("PDF'den metin çıkartılamadı veya yüklenen dosya bozuk/boş.")
        
    # 2. Analyze with Gemini
    data = analyze_cv_with_gemini(text)
    
    # 3. Log to Google Sheets
    append_to_gsheet(data)
    
    # 4. Notify via Slack sadece interview ise
    siniflandirma_karari = str(data.get('siniflandirma', '')).lower().strip()
    if 'interview' in siniflandirma_karari:
        send_slack_notification(data)
    
    return data
