import requests
import json

# المفاتيح الأساسية الخاصة بك
GEMINI_API_KEY = "AQ.Ab8RN6Kd4JRZKUbft6jJoS1mdy-WOCxc8bJcaGz34qLx5rrL-Q"
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

# قائمة الأسهم الصغيرة والمضاربية
watchlist = ["SNDL", "ZOM", "VERU", "MULN", "AGBA"]

def get_stock_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    return response.json()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

def analyze_with_gemini(stock_data_collection):
    # إرسال البيانات إلى جيميني المعتمد والجاهز لتحليل الأسهم
    prompt = f"""
    أنت محلل مالي خبير في الأسهم الصغيرة (Penny Stocks). لديك بيانات الأسهم التالية:
    {json.dumps(stock_data_collection)}
    
    التعليمات الصارمة:
    1. افحص الأسهم وقدم تحليلاً فنياً موجزاً ومرتباً في أسطر منفصلة.
    2. ممنوع الحشو أو المقدمات. ابدأ بالفرصة والقرار فوراً.
    3. حدد لكل سهم: الإيجابية/السلبية، سعر الدخول، وقف الخسارة، وهدف الربح.
    4. إذا لم توجد فرصة صالحة، اكتب بوضوح: "القرار: لا توجد فرصة مناسبة حالياً".
    """
    
    # استخدام الموديل المستقر والمعتمد للـ API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    res_json = response.json()
    
    try:
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"تعذر التحليل عبر الذكاء الاصطناعي حالياً: {res_json}"

if __name__ == "__main__":
    print("جاري سحب بيانات الأسهم وتحليلها عبر جيميني...")
    
    all_stocks_data = {}
    for symbol in watchlist:
        data = get_stock_data(symbol)
        if "values" in data:
            all_stocks_data[symbol] = data

    if all_stocks_data:
        # توليد التقرير التحليلي بواسطة جيميني
        ai_report = analyze_with_gemini(all_stocks_data)
        
        final_message = "🤖 *تقرير التحليل الذكي للأسهم* 🤖\n\n" + ai_report
        
        # إرسال التقرير لجوالك على تيليجرام
        tg_response = send_telegram_message(final_message)
        
        if tg_response.get("ok"):
            print("تم إرسال التقرير التحليلي بنجاح إلى جوالك!")
        else:
            print("خطأ في تيليجرام:", tg_response)
    else:
        print("فشل جلب بيانات الأسهم.")
