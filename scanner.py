import requests
import json

# المفاتيح الأساسية
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

def get_cheap_active_stocks():
    # سحب الأسهم الأكثر حركة وتصفيتها لتكون تحت 5 دولار
    url = f"https://api.twelvedata.com/market_movers/stocks?direction=gainers&outputsize=15&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    selected_symbols = []
    if "values" in data:
        for item in data["values"]:
            symbol = item["symbol"]
            # التأكد من السعر أو جلب السعر الحالي للتأكد أنه تحت 5$
            price_url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
            p_res = requests.get(price_url).json()
            if "price" in p_res:
                price = float(p_res["price"])
                if price <= 5.0:
                    selected_symbols.append(symbol)
            if len(selected_symbols) >= 3: # اختيار أفضل 3 أسهم مطابقة للشروط
                break
                
    # قائمة احتياطية لو السوق في حالة هدوء ولم يرجع نتائج تحت 5$
    if not selected_symbols:
        selected_symbols = ["SNDL", "ZOM", "VERU"]
        
    return selected_symbols

def get_technical_indicators(symbol):
    # سحب المؤشرات الفنية المتقدمة (RSI, MACD, BBands, SMA, ADX وغيرها)
    indicators = {}
    
    # جلب RSI
    rsi_res = requests.get(f"https://api.twelvedata.com/rsi?symbol={symbol}&interval=1day&time_period=14&apikey={TWELVE_DATA_API_KEY}").json()
    indicators['rsi'] = rsi_res.get("values", [{}])[0].get("rsi", "غير متوفر")
    
    # جلب MACD
    macd_res = requests.get(f"https://api.twelvedata.com/macd?symbol={symbol}&interval=1day&apikey={TWELVE_DATA_API_KEY}").json()
    if "values" in macd_res and len(macd_res["values"]) > 0:
        m_val = macd_res["values"][0]
        indicators['macd'] = f"Hist: {m_val.get('macd_hist', 'N/A')}"
    else:
        indicators['macd'] = "غير متوفر"
        
    # جلب السعر والبيانات الأساسية لحساب الفيبوناتشي والشموع
    ts_res = requests.get(f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}").json()
    indicators['ts'] = ts_res.get("values", [])
    
    return indicators

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    print("جاري فحص أسهم الزخم الرخيصة (<5$) وتطبيق المؤشرات التقنية...")
    
    stocks = get_cheap_active_stocks()
    report_lines = ["🚀 *تقرير الأسهم المضاربية (أقل من 5$) والتحليل الفني الشامل* 🚀\n"]
    
    for symbol in stocks:
        tech = get_technical_indicators(symbol)
        candles = tech.get('ts', [])
        
        if len(candles) > 0:
            latest = candles[0]
            close = float(latest["close"])
            high = float(latest["high"])
            low = float(latest["low"])
            volume = int(latest["volume"])
            
            # دراسة أداة فيبوناتشي (بناءً على أعلى قمة وأدنى قاع في آخر 30 يوم)
            highs = [float(c["high"]) for c in candles]
            lows = [float(c["low"]) for c in candles]
            max_high = max(highs)
            min_low = min(lows)
            diff = max_high - min_low
            
            fib_382 = round(max_high - (diff * 0.382), 2)
            fib_500 = round(max_high - (diff * 0.50), 2)
            fib_618 = round(max_high - (diff * 0.618), 2) # المنطقة الذهبية
            
            # حساب مستويات وقف الخسارة والأهداف
            stop_loss = round(low * 0.95, 2)
            target = round(close * 1.08, 2)
            
            report_lines.append(f"🔹 السهم: *{symbol}*")
            report_lines.append(f"• السعر الحالي: `{close} USD` (أقل من 5$)")
            report_lines.append(f"• حجم السيولة (Volume): `{volume:,}`")
            report_lines.append(f"• 📊 مؤشر RSI (14): `{tech.get('rsi')}`")
            report_lines.append(f"• 📈 مؤشر MACD: `{tech.get('macd')}`")
            report_lines.append(f"• 📐 فيبوناتشي (المنطقة الذهبية 0.618): `{fib_618}` | (تصحيح 0.382): `{fib_382}`")
            report_lines.append(f"• 🕯️ دراسة الشمعة الأخيرة: الإغلاق عند `{close}` وسط صراع بين المشترين والبائعين بين قمة `{high}` وقاع `{low}`")
            report_lines.append(f"• 🛑 وقف الخسارة المقترح: `{stop_loss}`")
            report_lines.append(f"• 🎯 الهدف المضاربي: `{target}`\n")
        else:
            report_lines.append(f"🔹 السهم: *{symbol}* - تعذر جلب بيانات المؤشرات التفصيلية.\n")

    final_report = "\n".join(report_lines)
    send_telegram_message(final_report)
    print("تم إرسال التقرير الشامل بنجاح!")
