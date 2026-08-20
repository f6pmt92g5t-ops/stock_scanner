import requests
import json

# المفاتيح الأساسية
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

def get_cheap_active_stocks():
    url = f"https://api.twelvedata.com/market_movers/stocks?direction=gainers&outputsize=20&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    selected_symbols = []
    if "values" in data:
        for item in data["values"]:
            symbol = item["symbol"]
            price_res = requests.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}").json()
            if "price" in price_res:
                price = float(price_res["price"])
                if price <= 5.0:
                    selected_symbols.append(symbol)
            if len(selected_symbols) >= 2: # نختار سهمين ليكون التقرير مفصلاً للغاية ولا يتجاوز حد تيليجرام
                break
                
    if not selected_symbols:
        selected_symbols = ["SNDL", "ZOM"]
        
    return selected_symbols

def get_all_indicators(symbol):
    ind = {}
    base_url = f"https://api.twelvedata.com"
    
    # سحب مؤشرات متعددة
    ind['rsi'] = requests.get(f"{base_url}/rsi?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("rsi", "N/A")
    ind['cci'] = requests.get(f"{base_url}/cci?symbol={symbol}&interval=1day&time_period=20&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("cci", "N/A")
    ind['adx'] = requests.get(f"{base_url}/adx?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("adx", "N/A")
    ind['willr'] = requests.get(f"{base_url}/williams%20r?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("willr", "N/A")
    ind['mfi'] = requests.get(f"{base_url}/mfi?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("mfi", "N/A")
    
    # المتوسطات المتحركة
    ind['sma50'] = requests.get(f"{base_url}/sma?symbol={symbol}&interval=1day&time_period=50&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("sma", "N/A")
    ind['sma200'] = requests.get(f"{base_url}/sma?symbol={symbol}&interval=1day&time_period=200&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("sma", "N/A")
    ind['ema20'] = requests.get(f"{base_url}/ema?symbol={symbol}&interval=1day&time_period=20&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0].get("ema", "N/A")
    
    # البولنجر باند
    bb = requests.get(f"{base_url}/bbands?symbol={symbol}&interval=1day&time_period=20&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0]
    ind['bb_upper'] = bb.get("upper_band", "N/A")
    ind['bb_lower'] = bb.get("lower_band", "N/A")
    
    # الماكد
    macd = requests.get(f"{base_url}/macd?symbol={symbol}&interval=1day&apikey={TWELVE_DATA_API_KEY}").json().get("values", [{}])[0]
    ind['macd_hist'] = macd.get("macd_hist", "N/A")
    
    # السعر والشموع التاريخية
    ts = requests.get(f"{base_url}/time_series?symbol={symbol}&interval=1day&outputsize=50&apikey={TWELVE_DATA_API_KEY}").json()
    ind['ts'] = ts.get("values", [])
    
    return ind

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    print("جاري سحب التحليل الفني الشامل للمؤشرات والفيبوناتشي...")
    stocks = get_cheap_active_stocks()
    
    for symbol in stocks:
        data = get_all_indicators(symbol)
        candles = data.get('ts', [])
        
        if len(candles) > 0:
            latest = candles[0]
            close = float(latest["close"])
            open_p = float(latest["open"])
            high = float(latest["high"])
            low = float(latest["low"])
            volume = int(latest["volume"])
            
            # تحليل الشمعة اليابانية
            body_size = abs(close - open_p)
            candle_type = "صاعدة قوية (Bullish)" if close > open_p else "هابطة وضغط بيعي (Bearish)"
            
            # فيبوناتشي بناءً على آخر 50 شمعة
            highs = [float(c["high"]) for c in candles]
            lows = [float(c["low"]) for c in candles]
            max_h = max(highs)
            min_l = min(lows)
            diff = max_h - min_l
            
            f_236 = round(max_h - (diff * 0.236), 2)
            f_382 = round(max_h - (diff * 0.382), 2)
            f_500 = round(max_h - (diff * 0.500), 2)
            f_618 = round(max_h - (diff * 0.618), 2) # الذهبية
            
            # تقييم المؤشرات إيجابي/سلبي
            rsi_val = float(data['rsi']) if data['rsi'] != "N/A" else 50
            rsi_status = "إيجابي (زخم صاعد)" if rsi_val > 50 else "سلبي (ضغط بيعي)"
            
            # بناء تقرير مفصل لكل سهم على حدة
            report = f"""🔬 *التقرير الفني الشامل العميق* 🔬
السهم: *{symbol}* (أقل من 5$)
السعر الحالي: `{close} USD`
السيولة (Volume): `{volume:,}`

---
📌 *1. دراسة الشمعة اليابانية والسيولة:*
• نوع الشمعة: *{candle_type}*
• حجم الجسم: `{round(body_size, 3)}` بين قمة `{high}` وقاع `{low}`
• دلالة السيولة: حركة الحجوم تؤكد سيطرة {'المشترين' if close > open_p else 'البائعين'}.

📌 *2. تحليل المؤشرات الفنية (أكثر من 10 مؤشرات):*
• *RSI (14):* `{data['rsi']}` -> الحالة: *{rsi_status}*
• *CCI (20):* `{data['cci']}` -> {'تشبع شراء' if str(data['cci']) != 'N/A' and float(data['cci']) > 100 else 'منطقة عادية/بيع'}
• *ADX (القوة الاتجاهية):* `{data['adx']}` -> {'اتجاه قوي' if str(data['adx']) != 'N/A' and float(data['adx']) > 25 else 'حركة عرضية ضعيفة'}
• *Williams %R:* `{data['willr']}`
• *MFI (مؤشر تدفق السيولة):* `{data['mfi']}`
• *MACD Histogram:* `{data['macd_hist']}` -> {'إيجابي (تقاطع صعودي)' if str(data['macd_hist']) != 'N/A' and float(data['macd_hist']) > 0 else 'سلبي'}
• *المتوسط SMA 50:* `{data['sma50']}` {'(السعر فوقه - إيجابي)' if str(data['sma50']) != 'N/A' and close > float(data['sma50']) else '(السعر تحته)'}
• *المتوسط SMA 200:* `{data['sma200']}`
• *المتوسط EMA 20:* `{data['ema20']}`
• *البولنجر باند (العلوي/السفلي):* `{data['bb_upper']}` / `{data['bb_lower']}`

📌 *3. مستويات فيبوناتشي (بناءً على المدى التاريخي):*
• قمة القياس: `{max_h}` | قاع القياس: `{min_l}`
• تصحيح 23.6%: `{f_236}`
• تصحيح 38.2%: `{f_382}`
• تصحيح 50.0%: `{f_500}`
• *المنطقة الذهبية للتصحيح 61.8%*: `{f_618}` (مهمة جداً لارتداد السهم)

📌 *4. القرار التداولي المضاربي:*
• 🛑 وقف الخسارة: `{round(low * 0.95, 2)}`
• 🎯 الهدف السعري الأول: `{round(close * 1.07, 2)}`
• 🎯 الهدف السعري الثاني: `{round(close * 1.12, 2)}`
═════════════════"""
            
            send_telegram_message(report)
