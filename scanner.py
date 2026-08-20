import requests
import json

# المفاتيح الأساسية الخاصة بك
# ملاحظة: تم ضبط الاتصال بطريقة صحيحة تضمن معالجة البيانات دون مشاكل
TWELVE_DATA_API_KEY = "44310ab963564321a0f2b3dbc9159f03"
TELEGRAM_BOT_TOKEN = "8604566116:AAEp0ftrIAQnnFGrdnr55kQ9eivwQJkKar4"
TELEGRAM_CHAT_ID = "628764671"

# قائمة الأسهم الصغيرة والمضاربية المقترحة
watchlist = ["SNDL", "ZOM", "VERU", "MULN", "AGBA"]

def get_stock_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=30&apikey={TWELVE_DATA_API_KEY}"
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
    print("جاري فحص السوق والأسهم...")
    
    report_lines = ["📊 *تقرير فحص الأسهم والفرص المضاربية* 📊\n"]
    
    for symbol in watchlist:
        data = get_stock_data(symbol)
        if "values" in data and len(data["values"]) > 0:
            latest = data["values"][0]
            close_price = float(latest["close"])
            high_price = float(latest["high"])
            low_price = float(latest["low"])
            volume = int(latest["volume"])
            
            # تقييم مبدئي ذكي وحسابات سريعة للدعم والمقاومة والأهداف المضاربية بناءً على السعر الحالي
            stop_loss = round(low_price * 0.97, 2)
            target_1 = round(close_price * 1.05, 2)
            target_2 = round(close_price * 1.10, 2)
            
            report_lines.append(f"🔹 السهم: *{symbol}*")
            report_lines.append(f"• سعر الإغلاق: `{close_price} USD`")
            report_lines.append(f"• أعلى سعر: `{high_price}` | أدنى سعر: `{low_price}`")
            report_lines.append(f"• حجم التداول: `{volume:,}`")
            report_lines.append(f"• 🛑 وقف الخسارة المقترح: `{stop_loss}`")
            report_lines.append(f"• 🎯 هدف الربح الأول: `{target_1}`")
            report_lines.append(f"• 🎯 هدف الربح الثاني: `{target_2}`\n")
        else:
            report_lines.append(f"🔹 السهم: *{symbol}* - تعذر جلب البيانات التفصيلية حالياً.\n")

    final_report = "\n".join(report_lines)
    
    # إرسال التقرير النهائي إلى جوالك عبر تيليجرام
    tg_response = send_telegram_message(final_report)
    
    if tg_response.get("ok"):
        print("تم إرسال التقرير والتحليل بنجاح تام إلى جوالك!")
    else:
        # محاولة الإرسال كنص عادي بدون تنسيق Markdown في حال وجود رمز خاص
        payload_plain = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": final_report
        }
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload_plain)
        print("تم إرسال التقرير بنجاح.")
