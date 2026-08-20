import requests
import json
import random

TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

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

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
        # تم إزالة parse_mode نهائياً لضمان عدم رفض تيليجرام للرسالة
    }
    response = requests.post(url, json=payload, timeout=10)
    print("Telegram API Response:", response.text)

if __name__ == "__main__":
    symbol = get_random_cheap_stocks()[0]
    print(f"تم اختيار السهم: {symbol}")
    
    rsi = fetch_indicator("rsi", symbol).get("rsi", "N/A")
    macd_hist = fetch_indicator("macd", symbol).get("macd_hist", "N/A")
    cci = fetch_indicator("cci", symbol).get("cci", "N/A")
    adx = fetch_indicator("adx", symbol).get("adx", "N/A")
    sma50 = fetch_indicator("sma?time_period=50", symbol).get("sma", "N/A")
    
    ts_res = requests.get(f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}").json()
    candles = ts_res.get("values", [])
    
    if len(candles) > 0:
        latest = candles[0]
        close = float(latest.get("close", 1))
        open_p = float(latest.get("open", 1))
        high = float(latest.get("high", 1))
        low = float(latest.get("low", 1))
        volume = int(float(latest.get("volume", 0)))
        
        candle_trend = "صاعدة قوية (ايجابي)" if close > open_p else "هابطة (ضغط بيعي)"
        
        highs = [float(c["high"]) for c in candles if "high" in c]
        lows = [float(c["low"]) for c in candles if "low" in c]
        max_h = max(highs) if highs else high
        min_l = min(lows) if lows else low
        diff = max_h - min_l if max_h != min_l else 1
        fib_618 = round(max_h - (diff * 0.618), 2)
        
        stop_loss = round(low * 0.94, 2)
        target_1 = round(close * 1.07, 2)

        # تقرير نصي صافي وبسيط يصل بدون أي أخطاء
        report = f"""التقرير الفني للأسهم المضاربية
السهم: {symbol} (تحت 5 دولار)
السعر الحالي: {close} USD
حجم التداول: {volume:,}

1. الشمعة والسيولة:
- الحالة: {candle_trend}
- القمة والقاع: {high} / {low}

2. المؤشرات الفنية:
- RSI (14): {rsi}
- MACD Hist: {macd_hist}
- CCI: {cci}
- ADX: {adx}
- SMA 50: {sma50}

3. فيبوناتشي:
- المنطقة الذهبية (61.8%): {fib_618}

4. التوصية المضاربية:
- وقف الخسارة: {stop_loss}
- الهدف الأول: {target_1}
"""
        
        send_telegram_message(report)
