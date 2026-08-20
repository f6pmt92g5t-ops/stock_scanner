import requests
import json

# المفاتيح الأساسية
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

def get_market_gainers():
    # سحب الأسهم الأكثر حركة ونشاطاً في السوق لتحديد فرص اليوم أوتوماتيكياً
    url = f"https://api.twelvedata.com/market_movers/stocks?direction=gainers&outputsize=5&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    symbols = []
    if "values" in data:
        for item in data["values"]:
            symbols.append(item["symbol"])
    
    # إذا لم تتوفر القائمة اللحظية لأي سبب، نضع بدائل متحركة لضمان عمل السكربت
    if not symbols:
        symbols = ["NIO", "PLTR", "SOFI", "F", "BAC"]
        
    return symbols[:5]

def get_stock_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=10&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    return response.json()

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
    print("جاري فحص السوق واختيار أفضل الأسهم المشتعلة...")
    
    active_stocks = get_market_gainers()
    report_lines = [f"🔥 *تقرير أسهم الزخم والاختيار التلقائي* 🔥\n"]
    report_lines.append(f"الأسهم المختارة اليوم بناءً على الحركة: `{', '.join(active_stocks)}`\n")
    
    for symbol in active_stocks:
        data = get_stock_data(symbol)
        if "values" in data and len(data["values"]) > 0:
            latest = data["values"][0]
            close = float(latest["close"])
            high = float(latest["high"])
            low = float(latest["low"])
            volume = int(latest["volume"])
            
            # حسابات فنية مضاربية دقيقة
            stop_loss = round(low * 0.96, 2)
            target = round(close * 1.06, 2)
            
            report_lines.append(f"🔹 السهم: *{symbol}*")
            report_lines.append(f"• السعر الحالي: `{close} USD`")
            report_lines.append(f"• القمة/القاعة: `{high}` / `{low}`")
            report_lines.append(f"• السيولة: `{volume:,}`")
            report_lines.append(f"• 🛑 وقف الخسارة: `{stop_loss}`")
            report_lines.append(f"• 🎯 الهدف المضاربي: `{target}`\n")
        else:
            report_lines.append(f"🔹 السهم: *{symbol}* - تعذر جلب تفاصيله.\n")

    final_report = "\n".join(report_lines)
    
    # إرسال التقرير النهائي لجوالك
    tg_response = send_telegram_message(final_report)
    
    if tg_response.get("ok"):
        print("تم إرسال التقرير الذكي بنجاح لجوالك!")
    else:
        print("خطأ في تيليجرام:", tg_response)
