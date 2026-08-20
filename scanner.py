import requests
import json

# المفاتيح الأساسية الخاصة بك
GEMINI_API_KEY = "AQ.Ab8RN6LA82vfh_dxZktGxhEyGFR0qKx6UB54-jmnoM0j32n9zA"
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"

# معلومات تيليجرام الخاصة بك
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

# قائمة الأسهم الصغيرة والمضاربية المقترحة
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

def analyze_and_filter(stock_data_collection):
    prompt = f"""
    أنت نظام فحص واكتشاف فرص مالية آلي للأسهم الصغيرة ومنخفضة السعر (Penny/Low-Priced Stocks). لديك بيانات الأسهم التالية:
    {json.dumps(stock_data_collection)}
    
    التعليمات الصارمة جداً:
    1. افحص جميع الأسهم، وابحث حصرياً عن السهم الذي تنطبق عليه الشروط الإيجابية (مثل RSI صحي، دعم قوي، وعدم وجود تشبع سلبي خطير).
    2. ممنوع نهائياً حشو الكلام أو المقدمات. ابدأ بالنتيجة والقرار فوراً.
    3. أي سعر، رقم، نسبة مئوية، أو قيمة مؤشر، يجب أن يُكتب في سطر جديد مستقل تماماً.
    4. اذكر مؤشرات التشبع الفني للأسهم المختارة بدقة:
       - RSI (14) وقيمته وحالته.
       - MACD Histogram وقيمته.
       - المتوسطات المتحركة (SMA50, SMA200, EMA20) وموقع السعر منها.
       - Bollinger Bands والاتجاه.
       - ADX ومؤشرات التشبع الأخرى (Stochastic RSI, Williams %R, CCI, MFI, VWAP, Supertrend).
    5. الشموع اليابانية: اشرح الشمعة الأخيرة بأسلوب معركة المشترين والبائعين (الجسم والفتيل ورفض القمم أو القيعان).
    6. أدوات فيبوناتشي (على 52 أسبوع + آخر قمة وقاع فعلي مع تحديد التصحيح البسيط والمتوسط والمنطقة الذهبية للشراء).
    7. القرار النهائي:
       - هل التحليل إيجابي أم سلبي؟
       - سعر الدخول المناسب.
       - وقف الخسارة.
       - هدف الربح.
       - إذا لم يكن هناك فرصة صالحة، قل بوضوح تام: "القرار: ابتعد عن الأسهم الحالية ولا توجد فرصة مناسبة".
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
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
        return f"حدث خطأ أثناء الفحص والفلترة: {res_json}"

if __name__ == "__main__":
    print("جاري فحص الأسهم وسحب البيانات وتحليلها وإرسالها لتيليجرام...")
    
    all_stocks_data = {}
    for symbol in watchlist:
        data = get_stock_data(symbol)
        if "code" not in data or data["code"] == 200:
            all_stocks_data[symbol] = data

    if all_stocks_data:
        final_report = analyze_and_filter(all_stocks_data)
        tg_response = send_telegram_message(final_report)
        
        if tg_response.get("ok"):
            print("تم إرسال التقرير بنجاح تام إلى جوالك عبر تيليجرام!")
        else:
            print("حدث خطأ في إرسال التيليجرام:", tg_response)
    else:
        print("فشل جلب بيانات الأسهم.")
