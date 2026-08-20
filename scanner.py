import requests
import json
import random

TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

# مفتاح Groq الخاص بك مدمج هنا وجاهز 100%
GROQ_API_KEY = "gsk_HvbdZD8AgQ2C3BUapLOQW Gdyb3FYz4t8j4lVAQr5dy2TSHakFxYO"

def get_random_cheap_stocks():
    pool = ["AMC", "SNDL", "ZOM", "VERU", "MULN", "AGBA", "BBIG", "CEI", "PROG", "TRKA", "IDEX", "SHIP", "OCGN"]
    random.shuffle(pool)
    for symbol in pool:
        try:
            price_res = requests.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}", timeout=5).json()
            if "price" in price_res:
                price = float(price_res["price"])
                if price <= 5.0:
                    return [symbol]
        except:
            continue
    return ["AMC"]

def fetch_indicator(endpoint, symbol):
    try:
        url = f"https://api.twelvedata.com/{endpoint}?symbol={symbol}&interval=1day&apikey={TWELVE_DATA_API_KEY}"
        res = requests.get(url, timeout=5).json()
        if "values" in res and len(res["values"]) > 0:
            return res["values"][0]
    except:
        pass
    return {}

def analyze_with_groq(stock_data_summary):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "content-type": "application/json"
    }
    
    prompt = f"""
    أنت محلل مالي محترف وخبير في الأسهم الأمريكية المضاربية (Penny Stocks أقل من 5$).
    لديك البيانات الفنية الكاملة لسهم مختار اليوم:
    {json.dumps(stock_data_summary, indent=2)}
    
    اكتب تقريراً فنياً واحترافياً باللغة العربية ومناسباً للإرسال عبر تيليجرام يوضح:
    1. تحليل حركة الشمعة اليابانية الحالية والسيولة وحجم التداول.
    2. قراءة مفصلة لأهم المؤشرات الفنية (RSI, MACD, Bollinger Bands, المتوسطات، CCI، ADX) وتحديد إيجابيتها أو سلبيتها.
    3. مستويات فيبوناتشي (مع التركيز على المنطقة الذهبية 61.8%).
    4. القرار المضاربي النهائي: سعر الدخول، وقف الخسارة، والأهداف السعرية.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_json = response.json()
        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"]
        else:
            return f"خطأ من استجابة Groq: {res_json}"
    except Exception as e:
        return f"استثناء أثناء الاتصال بـ Groq: {str(e)}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload, timeout=10)

if __name__ == "__main__":
    symbol = get_random_cheap_stocks()[0]
    
    stock_info = {
        "symbol": symbol,
        "rsi": fetch_indicator("rsi", symbol).get("rsi", "N/A"),
        "macd": fetch_indicator("macd", symbol),
        "bbands": fetch_indicator("bbands", symbol),
        "sma50": fetch_indicator("sma?time_period=50", symbol).get("sma", "N/A"),
        "sma200": fetch_indicator("sma?time_period=200", symbol).get("sma", "N/A"),
        "ema20": fetch_indicator("ema?time_period=20", symbol).get("ema", "N/A"),
        "cci": fetch_indicator("cci", symbol).get("cci", "N/A"),
        "adx": fetch_indicator("adx", symbol).get("adx", "N/A"),
        "stoch": fetch_indicator("stoch", symbol)
    }
    
    ts_res = requests.get(f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}").json()
    candles = ts_res.get("values", [])
    
    if len(candles) > 0:
        latest = candles[0]
        stock_info["latest_candle"] = latest
        highs = [float(c["high"]) for c in candles if "high" in c]
        lows = [float(c["low"]) for c in candles if "low" in c]
        max_h = max(highs) if highs else 1
        min_l = min(lows) if lows else 1
        diff = max_h - min_l if max_h != min_l else 1
        stock_info["fibonacci_golden_618"] = round(max_h - (diff * 0.618), 2)
    
    report = analyze_with_groq(stock_info)
    send_telegram_message(report)
