import requests
import json

# المفاتيح الأساسية
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

def get_cheap_active_stocks():
    try:
        url = f"https://api.twelvedata.com/market_movers/stocks?direction=gainers&outputsize=20&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        selected_symbols = []
        if "values" in data:
            for item in data["values"]:
                symbol = item.get("symbol")
                if not symbol:
                    continue
                price_res = requests.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}").json()
                if "price" in price_res:
                    try:
                        price = float(price_res["price"])
                        if price <= 5.0:
                            selected_symbols.append(symbol)
                    except:
                        pass
                if len(selected_symbols) >= 2:
                    break
                    
        if not selected_symbols:
            selected_symbols = ["SNDL", "ZOM"]
        return selected_symbols
    except Exception as e:
        return ["SNDL", "ZOM"]

def safe_get(url):
    try:
        res = requests.get(url).json()
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
        requests.post(url, json=payload)
    except:
        pass

if __name__ == "__main__":
    print("جاري فحص السوق والأسهم الرخيصة...")
    stocks = get_cheap_active_stocks()
    
    for symbol in stocks:
        base_url = f"https://api.twelvedata.com"
        
        # سحب المؤشرات بأمان
        rsi_val = safe_get(f"{base_url}/rsi?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").get("rsi", "N/A")
        cci_val = safe_get(f"{base_url}/cci?symbol={symbol}&interval=1day&time_period=20&apikey={TWELVE_DATA_API_KEY}").get("cci", "N/A")
        adx_val = safe_get(f"{base_url}/adx?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").get("adx", "N/A")
        
        # جلب البيانات التاريخية
        ts_res = requests.get(f"{base_url}/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}").json()
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
                
            candle_type = "صاعدة قوية (Bullish)" if close > open_p else "هابطة وضغط بيعي (Bearish)"
            
            # فيبوناتشي
            try:
                highs = [float(c["high"]) for c in candles if "high" in c]
                lows = [float(c["low"]) for c in candles if "low" in c]
                max_h = max(highs) if highs else high
                min_l = min(lows) if lows else low
                diff = max_h - min_l if max_h != min_l else 1
                f_618 = round(max_h - (diff * 0.618), 2)
            except:
                max_h, min_l, f_618 = high, low, low
            
            report = f"""🔬 *التقرير الفني الآلي الشامل* 🔬
السهم: *{symbol}* (أقل من 5$)
السعر الحالي: `{close} USD`
السيولة: `{volume:,}`

📌 *1. دراسة الشمعة اليابانية:*
• الحالة: *{candle_type}* بين قمة `{high}` وقاع `{low}`

📌 *2. المؤشرات الفنية المتقدمة:*
• RSI (14): `{rsi_val}`
• CCI (20): `{cci_val}`
• ADX (الاتجاه): `{adx_val}`

📌 *3. مستويات فيبوناتشي:*
• قمة: `{max_h}` | قاع: `{min_l}`
• المنطقة الذهبية (61.8%): `{f_618}`

📌 *4. القرار التداولي:*
• 🛑 وقف الخسارة: `{round(low * 0.95, 2)}`
• 🎯 الهدف المضاربي: `{round(close * 1.07, 2)}`
═════════════════"""
            
            send_telegram_message(report)
            
    print("تم إتمام الفحص وإرسال التقارير بنجاح.")
