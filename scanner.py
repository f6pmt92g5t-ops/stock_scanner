import requests
import json

# المفاتيح الأساسية
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

# قائمة الأسهم
watchlist = ["SNDL", "ZOM", "VERU", "MULN", "AGBA"]

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
    print("جاري الفحص المالي للأسهم...")
    
    report_lines = ["🤖 *التقرير الفني الآلي للأسهم المضاربية* 🤖\n"]
    
    for symbol in watchlist:
        data = get_stock_data(symbol)
        if "values" in data and len(data["values"]) > 0:
            latest = data["values"][0]
            close = float(latest["close"])
            high = float(latest["high"])
            low = float(latest["low"])
            volume = int(latest["volume"])
            
            # حسابات فنية ذكية ومستويات مقترحة للمضاربة
            stop_loss = round(low * 0.96, 2)
            target = round(close * 1.07, 2)
            decision = "إيجابية ملحوظة (فرصة متابعة)" if close > low * 1.01 else "حيادي / ترقب"
            
            report_lines.append(f"🔹 السهم: *{symbol}*")
            report_lines.append(f"• السعر الحالي: `{close} USD`")
            report_lines.append(f"• القمة / القاع: `{high}` / `{low}`")
            report_lines.append(f"• حجم السيولة: `{volume:,}`")
            report_lines.append(f"• 🛑 وقف الخسارة: `{stop_loss}`")
            report_lines.append(f"• 🎯 الهدف المضاربي: `{target}`")
            report_lines.append(f"• 💡 التقييم الفني: *{decision}*\n")
        else:
            report_lines.append(f"🔹 السهم: *{symbol}* - تعذر جلب البيانات حالياً.\n")

    final_report = "\n".join(report_lines)
    
    # إرسال التقرير لجوالك
    tg_response = send_telegram_message(final_report)
    
    if tg_response.get("ok"):
        print("تم إرسال التقرير بنجاح لجوالك!")
    else:
        print("خطأ في التيليجرام:", tg_response)
