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
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload, timeout=10)
    # طباعة رد تيليجرام لنتمكن من رؤيته في سجلات GitHub Actions
    print("Telegram API Response:", response.text)

if __name__ == "__main__":
    symbol = get_random_cheap_stocks()[0]
    print(f"تم اختيار السهم: {symbol}")
    
    # سحب المؤشرات الفنية المتقدمة
    rsi_data = fetch_indicator("rsi", symbol)
    rsi = rsi_data.get("rsi", "N/A")
    
    macd_data = fetch_indicator("macd", symbol)
    macd_hist = macd_data.get("macd_hist", "N/A")
    
    bbands = fetch_indicator("bbands", symbol)
    bb_upper = bb_upper_val = bbands.get("upper_band", "N/A")
    bb_lower = bb_lower_val = bbands.get("lower_band", "N/A")
    
    sma50 = fetch_indicator("sma?time_period=50", symbol).get("sma", "N/A")
    sma200 = fetch_indicator("sma?time_period=200", symbol).get("sma", "N/A")
    cci = fetch_indicator("cci", symbol).get("cci", "N/A")
    adx = fetch_indicator("adx", symbol).get("adx", "N/A")
    stoch = fetch_indicator("stoch", symbol)
    stoch_k = stoch.get("slow_k", "N/A")
    
    # جلب حركة الشموع التاريخية
    ts_res = requests.get(f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}").json()
    candles = ts_res.get("values", [])
    
    if len(candles) > 0:
        latest = candles[0]
        close = float(latest.get("close", 1))
        open_p = float(latest.get("open", 1))
        high = float(latest.get("high", 1))
        low = float(latest.get("low", 1))
        volume = int(float(latest.get("volume", 0)))
        
        candle_trend = "🟢 شمعة صاعدة قوية تعكس هيمنة المشترين" if close > open_p else "🔴 شمعة هابطة وضغط بيعي مسيطر"
        
        try:
            r_val = float(rsi)
            rsi_eval = "إيجابي وزخم صاعد" if r_val > 50 else "سلبي وتحت خط المنتصف"
        except:
            rsi_eval = "حيادي"
            
        try:
            m_val = float(macd_hist)
            macd_eval = "إيجابي (عزم صعودي)" if m_val > 0 else "سلبي (عزم هبوطي)"
        except:
            macd_eval = "حيادي"

        highs = [float(c["high"]) for c in candles if "high" in c]
        lows = [float(c["low"]) for c in candles if "low" in c]
        max_h = max(highs) if highs else high
        min_l = min(lows) if lows else low
        diff = max_h - min_l if max_h != min_l else 1
        
        fib_382 = round(max_h - (diff * 0.382), 2)
        fib_500 = round(max_h - (diff * 0.500), 2)
        fib_618 = round(max_h - (diff * 0.618), 2)
        
        stop_loss = round(low * 0.94, 2)
        target_1 = round(close * 1.07, 2)
        target_2 = round(close * 1.12, 2)

        report = f"""🚀 *التقرير الفني الاحترافي* 🚀
• السهم: *{symbol}* (أقل من 5$)
• السعر الحالي: `{close} USD`
• حجم التداول: `{volume:,}`

═════════════════
🕯️ *1. تحليل الشمعة والسيولة:*
• الحالة: *{candle_trend}*
• النطاق: قمة `{high}` | قاع `{low}`

═════════════════
📊 *2. المؤشرات الفنية المتقدمة:*
• RSI (14): `{rsi}` ⟵ {rsi_eval}
• MACD Hist: `{macd_hist}` ⟵ {macd_eval}
• CCI: `{cci}`
• ADX: `{adx}`
• SMA 50: `{sma50}`
• Bollinger: `{bb_upper_val}` / `{bb_lower_val}`

═════════════════
📐 *3. مستويات فيبوناتشي:*
• قمة المدى: `{max_h}` | قاع المدى: `{min_l}`
• ⭐ المنطقة الذهبية (61.8%): `{fib_618}`

═════════════════
🎯 *4. التوصية المضاربية:*
• 🛑 وقف الخسارة: `{stop_loss}`
• 🎯 الهدف الأول: `{target_1}`
• 🎯 الهدف الثاني: `{target_2}`
═════════════════"""
        
        send_telegram_message(report)
