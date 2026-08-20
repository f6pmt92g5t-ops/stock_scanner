import requests
import json
import random

# المفاتيح الأساسية
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

def get_random_cheap_stocks():
    # قائمة واسعة ومتنوعة من الأسهم المضاربية المحتملة تحت 5 دولار لمنع التكرار وضمان التنوع
    pool = ["AMC", "SNDL", "ZOM", "VERU", "MULN", "AGBA", "BBIG", "CEI", "PROG", "NILE", "GNUS", "TRKA", "IDEX", "SHIP", "OCGN"]
    random.shuffle(pool)
    
    selected = []
    for symbol in pool:
        try:
            price_res = requests.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}", timeout=5).json()
            if "price" in price_res:
                price = float(price_res["price"])
                if price <= 5.0:
                    selected.append(symbol)
            if len(selected) >= 2: # اختيار سهمين متنوعين في كل مرة ليكون التحليل عميقاً ومفصلاً بالكامل
                break
        except:
            continue
            
    if not selected:
        selected = ["AMC", "ZOM"]
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
    print("جاري سحب السوق وتحليل أكثر من 15 مؤشراً فنياً بالتفصيل...")
    stocks = get_random_cheap_stocks()
    
    for symbol in stocks:
        base_url = f"https://api.twelvedata.com"
        
        # سحب أكثر من 15 مؤشراً وبيانات متقدمة
        rsi = fetch_indicator("rsi", symbol).get("rsi", "N/A")
        macd = fetch_indicator("macd", symbol)
        macd_val = macd.get("macd", "N/A")
        macd_signal = macd.get("macd_signal", "N/A")
        macd_hist = macd.get("macd_hist", "N/A")
        
        bbands = fetch_indicator("bbands", symbol)
        bb_upper = bbands.get("upper_band", "N/A")
        bb_lower = bbands.get("lower_band", "N/A")
        bb_middle = bbands.get("middle_band", "N/A")
        
        sma50 = fetch_indicator("sma?time_period=50", symbol).get("sma", "N/A")
        sma200 = fetch_indicator("sma?time_period=200", symbol).get("sma", "N/A")
        ema20 = fetch_indicator("ema?time_period=20", symbol).get("ema", "N/A")
        
        stoch = fetch_indicator("stoch", symbol)
        stoch_k = stoch.get("slow_k", "N/A")
        stoch_d = stoch.get("slow_d", "N/A")
        
        willr = fetch_indicator("williams%20r", symbol).get("willr", "N/A")
        cci = fetch_indicator("cci", symbol).get("cci", "N/A")
        adx = fetch_indicator("adx", symbol).get("adx", "N/A")
        mfi = fetch_indicator("mfi", symbol).get("mfi", "N/A")
        atr = fetch_indicator("atr", symbol).get("atr", "N/A")
        obv = fetch_indicator("obv", symbol).get("obv", "N/A")
        
        # الشموع التاريخية لفيبوناتشي
        ts_res = requests.get(f"{base_url}/time_series?symbol={symbol}&interval=1day&outputsize=50&apikey={TWELVE_DATA_API_KEY}").json()
        candles = ts_res.get("values", [])
        
        if len(candles) > 0:
            latest = candles[0]
            try:
                close = float(latest.get("close", 1))
                open_p = float(latest.get("open", 1))
                high = float(latest.get("high", 1))
                low = float(latest.get("low", 1))
                volume = int(float(latest.get("volume", 0)))
            except:
                close, open_p, high, low, volume = 1.0, 1.0, 1.0, 1.0, 0
                
            # دراسة تفصيلية للشموع اليابانية
            body = abs(close - open_p)
            upper_shadow = high - max(close, open_p)
            lower_shadow = min(close, open_p) - low
            
            candle_desc = "شمعة صاعدة قوية تعكس سيطرة المشترين" if close > open_p else "شمعة هابطة وضغط بيعي واضح"
            if upper_shadow > body * 2:
                candle_desc += " مع وجود ذل علوي ينم عن رفض الأسعار المرتفعة (مقاومة)."
            if lower_shadow > body * 2:
                candle_desc += " مع وجود ذل سفلي يدل على وجود دعم قوي وامتصاص للبيع."

            # تحليل وتقييم المؤشرات (إيجابي / سلبي)
            try:
                r_val = float(rsi)
                rsi_eval = "🟢 إيجابي (زخم صاعد)" if r_val > 50 else "🔴 سلبي (ضغط بيعي)"
            except:
                rsi_eval = "حيادي"

            try:
                m_hist = float(macd_hist)
                macd_eval = "🟢 إيجابي (تقاطع صعودي وعزم إيجابي)" if m_hist > 0 else "🔴 سلبي (عزم سلبي وتراجع)"
            except:
                macd_eval = "حيادي"

            try:
                s50 = float(sma50)
                sma50_eval = "🟢 إيجابي (السعر يتداول أعلى المتوسط)" if close > s50 else "🔴 سلبي (السعر تحت المتوسط)"
            except:
                sma50_eval = "حيادي"

            # مستويات فيبوناتشي الكاملة
            highs = [float(c["high"]) for c in candles if "high" in c]
            lows = [float(c["low"]) for c in candles if "low" in c]
            max_h = max(highs) if highs else high
            min_l = min(lows) if lows else low
            diff = max_h - min_l if max_h != min_l else 1
            
            f_236 = round(max_h - (diff * 0.236), 2)
            f_382 = round(max_h - (diff * 0.382), 2)
            f_500 = round(max_h - (diff * 0.500), 2)
            f_618 = round(max_h - (diff * 0.618), 2) # المنطقة الذهبية
            f_786 = round(max_h - (diff * 0.786), 2)

            report = f"""📊 *التقرير الفني الشامل والمفصل للأسهم (أقل من 5$)* 📊
السهم المختصر: *{symbol}*
سعر الإغلاق الحالي: `{close} USD`
حجم السيولة (Volume): `{volume:,}`

═════════════════
🕯️ *1. تحليل الشمعة اليابانية وحركة السعر:*
• الحالة: *{candle_desc}*
• نطاق التركة: بين قمة `{high}` وقاع `{low}` (حجم الجسم: `{round(body, 3)}`)

═════════════════
📈 *2. تحليل أكثر من 15 مؤشراً فنياً بالتفصيل:*
1. **RSI (14):** `{rsi}` -> {rsi_eval}
2. **MACD Histogram:** `{macd_hist}` -> {macd_eval}
3. **MACD Line / Signal:** `{macd_val}` / `{macd_signal}`
4. **SMA 50 (متوسط 50):** `{sma50}` -> {sma50_eval}
5. **SMA 200 (متوسط 200):** `{sma200}`
6. **EMA 20 (الاسي 20):** `{ema20}` -> {'🟢 إيجابي فوقه' if ema20 != 'N/A' and close > float(ema20) else '🔴 تحته'}
7. **Bollinger Bands (العلوي):** `{bb_upper}`
8. **Bollinger Bands (السفلي):** `{bb_lower}`
9. **Bollinger Bands (المتوسط):** `{bb_middle}`
10. **Stochastic (%K / %D):** `{stoch_k}` / `{stoch_d}` -> {'🟢 تشبع بيعي (فرصة ارتداد)' if stoch_k != 'N/A' and float(stoch_k) < 20 else '⚪ حركة طبيعية'}
11. **Williams %R:** `{willr}`
12. **CCI (مؤشر قناة السلع):** `{cci}` -> {'🟢 إيجابي (زخم قوي)' if cci != 'N/A' and float(cci) > 0 else '🔴 سلبي'}
13. **ADX (قوة الاتجاه):** `{adx}` -> {'🟢 اتجاه قوي مسيطر' if adx != 'N/A' and float(adx) > 25 else '⚪ حركة عرضية ضعيفة'}
14. **MFI (تدفق السيولة):** `{mfi}`
15. **ATR (مقياس التذبذب):** `{atr}`
16. **OBV (حجم التوازن):** `{obv}`

═════════════════
📐 *3. مستويات فيبوناتشي الكاملة:*
• قمة القياس: `{max_h}` | قاع القياس: `{min_l}`
• تصحيح 23.6%: `{f_236}`
• تصحيح 38.2%: `{f_382}`
• تصحيح 50.0% (نصف المنتصف): `{f_500}`
• ⭐ *المنطقة الذهبية للتصحيح 61.8%*: `{f_618}` (أقوى مناطق الارتداد المتوقعة)
• تصحيح 78.6%: `{f_786}`

═════════════════
🎯 *4. التوصية ومستويات المخاطرة:*
• 🛑 وقف الخسارة الآمن: `{round(low * 0.94, 2)}`
• 🎯 الهدف المضاربي الأول: `{round(close * 1.07, 2)}`
• 🎯 الهدف المضاربي الثاني: `{round(close * 1.12, 2)}`
═════════════════"""
            
            send_telegram_message(report)
            
    print("تم فحص الأسهم وإرسال التحليل العميق بنجاح.")
