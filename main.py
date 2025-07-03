import os
import time
import random
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import requests
import logging

# إعدادات البوت
ADMIN_USERNAME = "messaoudi_khalil"
BOT_USERNAME = "your_bot_username"
BOT_PASSWORD = "your_bot_password"

# قوائم الأذكار
MORNING_ADHKAR = [
    "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له...",
    "اللهم بك أصبحنا، وبك أمسينا، وبك نحيا، وبك نموت، وإليك النشور.",
    "سبحان الله وبحمده عدد خلقه ورضا نفسه وزنة عرشه ومداد كلماته."
]

EVENING_ADHKAR = [
    "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له...",
    "اللهم بك أمسينا، وبك أصبحنا، وبك نحيا، وبك نموت، وإليك المصير.",
    "أعوذ بكلمات الله التامات من شر ما خلق."
]

NIGHT_ADHKAR = [
    "باسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم.",
    "آية الكرسي: الله لا إله إلا هو الحي القيوم...",
    "أعوذ برب الفلق، من شر ما خلق..."
]

# متغيرات التتبع
follow_requests = []  # لتخزين طلبات المتابعة
active_users = []     # المستخدمون الذين كتبوا /start
followed_back = []    # المستخدمون الذين تمت متابعتهم

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_algeria_time():
    # توقيت الجزائر (UTC+1)
    return datetime.utcnow().hour + 1

def send_direct_message(client, user_id, message):
    try:
        client.direct_send(message, user_ids=[user_id])
        logging.info(f"تم إرسال رسالة إلى {user_id}")
    except Exception as e:
        logging.error(f"خطأ في الإرسال: {e}")

def handle_new_follower(client, user_id, username):
    # إرسال طلب متابعة إلى الأدمن
    message = f"طلب متابعة جديد من: {username}\n\n"
    message += f"لموافقة على المتابعة، اضغط على الرابط التالي أو اكتب 'قبول {username}'"
    
    try:
        client.direct_send(message, user_ids=[client.user_id_from_username(ADMIN_USERNAME)])
        follow_requests.append({"user_id": user_id, "username": username, "status": "pending"})
        logging.info(f"تم إرسال طلب متابعة من {username}")
    except Exception as e:
        logging.error(f"خطأ في إرسال طلب المتابعة: {e}")

def follow_user(client, username):
    try:
        user_id = client.user_id_from_username(username)
        client.user_follow(user_id)
        followed_back.append(username)
        logging.info(f"تم متابعة المستخدم: {username}")
        return True
    except Exception as e:
        logging.error(f"خطأ في متابعة المستخدم: {e}")
        return False

def get_random_quran_audio():
    try:
        # استخدام API من موقع Quran.com أو غيره
        response = requests.get("https://api.quran.com/api/v4/chapters/1/audio_files")
        audio_files = response.json()["audio_files"]
        return random.choice(audio_files)["audio_url"]
    except Exception as e:
        logging.error(f"خطأ في جلب الآية القرآنية: {e}")
        return None

def process_messages(client):
    # معالجة الرسائل الواردة
    threads = client.direct_threads()
    for thread in threads:
        for item in thread.messages:
            message = item.text
            user_id = item.user_id
            
            if message.startswith("/start"):
                if user_id not in active_users:
                    active_users.append(user_id)
                    send_direct_message(client, user_id, "تم تفعيل البوت! ستصلك الأذكار يومياً.")
            
            elif message.startswith("/quran"):
                audio_url = get_random_quran_audio()
                if audio_url:
                    send_direct_message(client, user_id, f"تلاوة قرآنية: {audio_url}")
                else:
                    send_direct_message(client, user_id, "عذراً، حدث خطأ في جلب التلاوة.")
            
            elif message.startswith("قبول ") and item.user.username == ADMIN_USERNAME:
                username = message.split(" ")[1]
                if follow_user(client, username):
                    send_direct_message(client, user_id, f"تم قبول متابعة {username}")

def send_scheduled_adhkar(client):
    current_hour = get_algeria_time()
    
    # تحديد نوع الذكر حسب الوقت
    if 6 <= current_hour < 9:
        adhkar = MORNING_ADHKAR
        time_type = "صباحاً"
    elif 18 <= current_hour < 21:
        adhkar = EVENING_ADHKAR
        time_type = "مساءً"
    elif 21 <= current_hour < 23:
        adhkar = NIGHT_ADHKAR
        time_type = "وقت النوم"
    else:
        return
    
    # إرسال الأذكار للمستخدمين النشطين
    for user_id in active_users:
        zikr = random.choice(adhkar)
        message = f"ذكر {time_type}:\n\n{zikr}"
        send_direct_message(client, user_id, message)

def main():
    client = Client()
    
    try:
        client.login(BOT_USERNAME, BOT_PASSWORD)
        logging.info("تم تسجيل الدخول بنجاح!")
    except LoginRequired as e:
        logging.error("فشل تسجيل الدخول: تحقق من اسم المستخدم وكلمة المرور")
        return
    
    # الحصول على معلومات الحساب
    bot_user_id = client.user_id
    
    while True:
        try:
            # 1. التحقق من المتابعين الجدد
            followers = client.user_followers(bot_user_id)
            for user_id, user_info in followers.items():
                if user_id not in [u["user_id"] for u in follow_requests] and user_id not in followed_back:
                    handle_new_follower(client, user_id, user_info.username)
            
            # 2. معالجة الرسائل الواردة
            process_messages(client)
            
            # 3. إرسال الأذكار حسب الوقت
            send_scheduled_adhkar(client)
            
            # 4. الانتظار قبل التحقق مرة أخرى
            time.sleep(300)  # كل 5 دقائق
            
        except Exception as e:
            logging.error(f"خطأ في الدورة الرئيسية: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()