import requests
import json
import random
import os

TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

def get_random_cheap_stocks():
    pool = ["AMC", "SNDL", "ZOM", "VERU", "MULN", "AGBA", "BBIG", "CEI", "PROG", "TRKA", "IDEX", "SHIP", "OCGN"]
    random.shuffle(pool)
    selected = []
    for symbol in pool:
        try:
            price_res = requests.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}", timeout=5).json()
            if "price" in price_res:
                price = float(price_res["price"])
                if price <= 5.0:
                    selected.append(symbol)
            if len(selected) >= 1: # نختار سهم واحد ممتاز ليأخذ Claude وقته في تحليله بعمق
                break
        except:
            continue
    if not selected:
        selected = ["AMC"]
    return selected

def fetch_indicator(endpoint, symbol):
    try:
        url = f"https://api.twelvedata.com/{endpoint}?symbol={symbol}&interval=1day&apikey={TWELVE_DATA_API_KEY}"
        res = requests.get(url, timeout=5).json()
        if "values" in res and len(res["values"]) > 0:
            return res["values"][0]
    except:
        pass
    return {}

def analyze_with_claude(stock_data_summary):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    prompt = f"""
    أنت محلل مالي خبير في الأسهم الأمريكية المضاربية (Penny Stocks أقل من 5$).
    لديك البيانات الفنية الكاملة لسهم مختهر اليوم:
    {json.dumps(stock_data_summary, indent=2)}
    
    اكتب تقريراً فنياً واحترافياً باللغة العربية ومناسباً لتيليجرام يوضح:
    1. تحليل حركة الشمعة اليابانية والسيولة.
    2. قراءة مفصلة لأهم المؤشرات (RSI, MACD, Bollinger Bands, المتوسطات) وهل هي إيجابية أو سلبية.
    3. مستويات فيبوناتشي (خاصة المنطقة الذهبية 61.8%).
    4. القرار المضاربي: سعر الدخول، وقف الخسارة، والأهداف.
    """
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_json = response.json()
        return res_json["content"][0]["text"]
    except Exception as e:
        return f"تعذر التحليل عبر Claude حالياً: {str(e)}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

if __name__ == "__main__":
    stocks = get_random_cheap_stocks()
    for symbol in stocks:
        base_url = f"https://api.twelvedata.com"
        stock_info = {
            "symbol": symbol,
            "rsi": fetch_indicator("rsi", symbol).get("rsi", "N/A"),
            "macd": fetch_indicator("macd", symbol),
            "bbands": fetch_indicator("bbands", symbol),
            "sma50": fetch_indicator("sma?time_period=50", symbol).get("sma", "N/A"),
            "sma200": fetch_indicator("sma?time_period=200", symbol).get("sma", "N/A"),
            "ema20": fetch_indicator("ema?time_period=20", symbol).get("ema", "N/A"),
            "cci": fetch_indicator("cci", symbol).get("cci", "N/A"),
            "adx": fetch_indicator("adx", symbol).get("adx", "N/A")
        }
        
        ts_res = requests.get(f"{base_url}/time_series?symbol={symbol}&interval=1day&outputsize=50&apikey={TWELVE_DATA_API_KEY}").json()
        candles = ts_res.get("values", [])
        
        if len(candles) > 0:
            latest = candles[0]
            stock_info["latest_candle"] = latest
            highs = [float(c["high"]) for c in candles if "high" in c]
            lows = [float(c["low"]) for c in candles if "low" in c]
            max_h = max(highs) if highs else float(latest.get("high", 1))
            min_l = min(lows) if lows else float(latest.get("low", 1))
            diff = max_h - min_l if max_h != min_l else 1
            
            stock_info["fibonacci"] = {
                "max_high": max_h, "min_l": min_l,
                "fib_618_golden": round(max_h - (diff * 0.618), 2)
            }
            
            claude_report = analyze_with_claude(stock_info)
            send_telegram_message(claude_report)
