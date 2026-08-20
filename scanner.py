import requests
import json

# مفتاح سحب بيانات الأسهم الخاص بك
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"

# معلومات تيليجرام الخاصة بك
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

# قائمة الأسهم الصغيرة ومضاربية
watchlist = ["SNDL", "ZOM", "VERU", "MULN", "AGBA"]

def get_stock_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    return response.json()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    print("جاري سحب بيانات الأسهم...")
    
    report_lines = ["📊 *تقرير فحص الأسهم الآلي* 📊\n"]
    
    for symbol in watchlist:
        data = get_stock_data(symbol)
        if "values" in data:
            latest = data["values"][0]
            close_price = latest["close"]
            high_price = latest["high"]
            low_price = latest["low"]
            volume = latest["volume"]
            
            report_lines.append(f"🔹 السهم: *{symbol}*")
            report_lines.append(f"سعر الإغلاق: {close_price} USD")
            report_lines.append(f"الاعلى: {high_price} | الأدنى: {low_price}")
            report_lines.append(f"السيولة/الحجم: {volume}\n")
        else:
            report_lines.append(f"🔹 السهم: *{symbol}* - تعذر جلب البيانات حالياً.\n")

    final_report = "\n".join(report_lines)
    
    # إرسال التقرير لجوالك
    tg_response = send_telegram_message(final_report)
    
    if tg_response.get("ok"):
        print("تم إرسال التقرير بنجاح إلى جوالك عبر تيليجرام!")
    else:
        print("خطأ في التيليجرام:", tg_response)
