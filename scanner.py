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
    requests.post(url, json=payload, timeout=10)

if __name__ == "__main__":
    symbol = get_random_cheap_stocks()[0]
    
    # سحب المؤشرات الفنية المتقدمة
    rsi_data = fetch_indicator("rsi", symbol)
    rsi = rsi_data.get("rsi", "N/A")
    
    macd_data = fetch_indicator("macd", symbol)
    macd_hist = macd_data.get("macd_hist", "N/A")
    
    bbands = fetch_indicator("bbands", symbol)
    bb_upper = bbands.get("upper_band", "N/A")
    bb_lower = bbands.get("lower_band", "N/A")
    
    sma50 = fetch_indicator("sma?time_period=50", symbol).get("sma", "N/A")
    sma200 = fetch_indicator("sma?time_period=200", symbol).get("sma", "N/A")
    ema20 = fetch_indicator("ema?time_period=20", symbol).get("ema", "N/A")
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
        
        # تحليل الشمعة اليابانية والسيولة
        body = abs(close - open_p)
        candle_trend = "🟢 شمعة صاعدة قوية تعكس هيمنة المشترين والسيولة الإيجابية" if close > open_p else "🔴 شمعة هابطة وضغط بيعي مسيطر"
        
        # تقييمات المؤشرات (إيجابي / سلبي)
        try:
            r_val = float(rsi)
            rsi_eval = "إيجابي وزخم صاعد" if r_val > 50 else "سلبي وتحت خط المنتصف"
        except:
            rsi_eval = "حيادي"
            
        try:
            m_val = float(macd_hist)
            macd_eval = "إيجابي (عزم صعودي متنامٍ)" if m_val > 0 else "سلبي (زخم بيعي متراجع)"
        except:
            macd_eval = "حيادي"

        # حساب مستويات فيبوناتشي
        highs = [float(c["high"]) for c in candles if "high" in c]
        lows = [float(c["low"]) for c in candles if "low" in c]
        max_h = max(highs) if highs else high
        min_l = min(lows) if lows else low
        diff = max_h - min_l if max_h != min_l else 1
        
        fib_382 = round(max_h - (diff * 0.382), 2)
        fib_500 = round(max_h - (diff * 0.500), 2)
        fib_618 = round(max_h - (diff * 0.618), 2) # المنطقة الذهبية
        
        # القرار المضاربي المستهدف
        stop_loss = round(low * 0.94, 2)
        target_1 = round(close * 1.07, 2)
        target_2 = round(close * 1.12, 2)

        # صياغة التقرير الفني الاحترافي الشامل
        report = f"""🚀 *التقرير الفني الاحترافي للأسهم المضاربية* 🚀
• السهم المختصر: *{symbol}* (أقل من 5$)
• سعر الإغلاق الحالي: `{close} USD`
• حجم التداول (Volume): `{volume:,}`

═════════════════
🕯️ *1. تحليل الشمعة اليابانية وحركة السيولة:*
• الحالة الفنية: *{candle_trend}*
• النطاق السعري للشمعة: بين قمة `{high}` وقاع `{low}` (حجم الجسم: `{round(body, 3)}`)

═════════════════
📊 *2. تحليل المؤشرات الفنية المتقدمة:*
• **مؤشر RSI (14):** `{rsi}` ⟵ *{rsi_eval}*
• **مؤشر MACD Histogram:** `{macd_hist}` ⟵ *{macd_eval}*
• **مؤشر CCI (قناة السلع):** `{cci}` ⟵ {'تشبع شراء / قوة زخم' if cci != 'N/A' and float(cci) > 100 else 'منطقة تداول طبيعية'}
• **مؤشر ADX (قوة الاتجاه):** `{adx}` ⟵ {'اتجاه قوي ومستمر' if adx != 'N/A' and float(adx) > 25 else 'حركة عرضية تجميعية'}
• **مؤشر Stochastic (%K):** `{stoch_k}`
• **المتوسط المتحرك SMA 50:** `{sma50}` ⟵ {'السعر يتداول أعلى المتوسط (إيجابي)' if sma50 != 'N/A' and close > float(sma50) else 'السعر أدنى المتوسط'}
• **المتوسط المتحرك SMA 200:** `{sma200}`
• **البولنجر باند (العلوي / السفلي):** `{bb_upper}` / `{bb_lower}`

═════════════════
📐 *3. مستويات فيبوناتشي الكاملة:*
• قمة المدى التاريخي: `{max_h}`
• قاع المدى التاريخي: `{min_l}`
• تصحيح 38.2%: `{fib_382}`
• تصحيح 50.0% (نصف المدى): `{fib_500}`
• ⭐ *المنطقة الذهبية للتصحيح 61.8%*: `{fib_618}` (أقوى مستويات الارتداد المرتقبة)

═════════════════
🎯 *4. التوصية ومستويات المخاطرة المضاربية:*
• 🛑 وقف الخسارة الآمن: `{stop_loss}`
• 🎯 الهدف المضاربي الأول: `{target_1}`
• 🎯 الهدف المضاربي الثاني: `{target_2}`
═════════════════"""
        
        send_telegram_message(report)
