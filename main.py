import os
import time
import random
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
import requests
import logging

# إعدادات البوت
ADMIN_USERNAME = "messaoudi__khalil"
BOT_USERNAME = "adhkar122025"
BOT_PASSWORD = "kham2007"

# قوائم الأذكار
MORNING_ADHKAR = [
    "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "اللهم بك أصبحنا، وبك أمسينا، وبك نحيا، وبك نموت، وإليك النشور.",
    "سبحان الله وبحمده عدد خلقه ورضا نفسه وزنة عرشه ومداد كلماته."
]

EVENING_ADHKAR = [
    "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "اللهم بك أمسينا، وبك أصبحنا، وبك نحيا، وبك نموت، وإليك المصير.",
    "أعوذ بكلمات الله التامات من شر ما خلق."
]

NIGHT_ADHKAR = [
    "باسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم.",
    "آية الكرسي: الله لا إله إلا هو الحي القيوم...",
    "أعوذ برب الفلق، من شر ما خلق."
]

# متغيرات التتبع
follow_requests = []
active_users = []
followed_back = []
processed_messages = set()  # لتجنب معالجة الرسائل القديمة
last_message_times = {}  # لتجنب التكرار

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_logs.log'),
        logging.StreamHandler()
    ]
)

def get_algeria_time():
    """الحصول على توقيت الجزائر (UTC+1)"""
    try:
        return (datetime.utcnow().hour + 1) % 24
    except Exception as e:
        logging.error(f"خطأ في الحصول على الوقت: {e}")
        return datetime.now().hour

def send_direct_message(client, user_id, message):
    """إرسال رسالة مباشرة مع التحكم في التكرار"""
    try:
        if not user_id or not message:
            return False
            
        # التحقق من عدم تكرار الرسالة مؤخراً
        now = time.time()
        last_sent = last_message_times.get(user_id, 0)
        if now - last_sent < 30:  # 30 ثانية بين الرسائل
            return False
            
        client.direct_send(text=message, user_ids=[user_id])
        last_message_times[user_id] = now
        logging.info(f"تم إرسال رسالة إلى {user_id}")
        return True
    except Exception as e:
        logging.error(f"خطأ في إرسال الرسالة: {e}")
        return False

def handle_new_follower(client, user_id, username):
    """إدارة المتابعين الجدد"""
    if not user_id or not username:
        return False
        
    try:
        # التحقق من عدم إرسال الطلب مسبقاً
        for req in follow_requests:
            if req['user_id'] == user_id:
                return True
                
        message = f"📬 طلب متابعة جديد من: @{username}\n\n"
        message += "📌 للموافقة على المتابعة، اردد:\n"
        message += f"قبول {username}"
        
        admin_id = client.user_id_from_username(ADMIN_USERNAME)
        if send_direct_message(client, admin_id, message):
            follow_requests.append({
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return True
    except Exception as e:
        logging.error(f"خطأ في معالجة المتابع الجديد: {e}")
    return False

def follow_user(client, username):
    """متابعة مستخدم مع التحقق من المتابعة السابقة"""
    try:
        if not username:
            return False
            
        # التحقق من المتابعة السابقة
        if username in followed_back:
            return True
            
        user_id = client.user_id_from_username(username)
        if not user_id:
            return False
            
        client.user_follow(user_id)
        followed_back.append(username)
        logging.info(f"تم متابعة المستخدم: @{username}")
        return True
    except Exception as e:
        logging.error(f"خطأ في متابعة المستخدم: {e}")
        return False

def get_short_quran_audio():
    """الحصول على مقطع قرآن قصير"""
    try:
        # مصدر بديل إذا لم يعمل الأول
        return "https://server.mp3quran.net/s_gmd/001.mp3"  # سورة الفاتحة
    except Exception as e:
        logging.error(f"خطأ في جلب التلاوة: {e}")
        return None

def process_new_messages(client):
    """معالجة الرسائل الجديدة فقط"""
    try:
        threads = client.direct_threads(amount=10)  # الحد من عدد المحادثات
        if not threads:
            return
            
        for thread in threads:
            if not hasattr(thread, 'messages') or not thread.messages:
                continue
                
            for item in thread.messages:
                # التحقق من الرسائل الجديدة فقط
                if not hasattr(item, 'id') or item.id in processed_messages:
                    continue
                    
                if not hasattr(item, 'text') or not item.text:
                    processed_messages.add(item.id)
                    continue
                    
                message = item.text.strip()
                user_id = item.user_id
                thread_id = thread.id
                processed_messages.add(item.id)
                
                if not message:
                    continue
                    
                try:
                    if message.startswith("/start"):
                        if user_id not in active_users:
                            active_users.append(user_id)
                            send_direct_message(client, user_id,
                                "✨ تم تفعيل البوت بنجاح!\n\n"
                                "سوف تصلك الأذكار اليومية تلقائياً:\n"
                                "- أذكار الصباح (6-9 ص)\n"
                                "- أذكار المساء (6-9 م)\n"
                                "- أذكار النوم (9-11 م)\n\n"
                                "الأوامر المتاحة:\n"
                                "/quran - تلاوة قرآنية قصيرة\n"
                                "/حذف - إخفاء هذه المحادثة\n"
                                "/request - عرض طلبات المتابعة (للأدمن)")
                    
                    elif message.startswith("/quran"):
                        audio_url = get_short_quran_audio()
                        if audio_url:
                            send_direct_message(client, user_id,
                                "🎧 تلاوة قرآنية قصيرة (سورة الفاتحة):\n\n"
                                f"{audio_url}\n\n"
                                "اضغط على الرابط للاستماع")
                    
                    elif message.startswith("/request"):
                        if str(user_id) == str(client.user_id_from_username(ADMIN_USERNAME)):
                            if follow_requests:
                                requests_list = "\n".join(
                                    [f"{idx+1}. @{req['username']} ({req['timestamp']})"
                                     for idx, req in enumerate(follow_requests)])
                                send_direct_message(client, user_id,
                                    "📋 طلبات المتابعة:\n\n" + requests_list)
                            else:
                                send_direct_message(client, user_id,
                                    "لا توجد طلبات متابعة جديدة")
                    
                    elif message.startswith("قبول ") and str(user_id) == str(client.user_id_from_username(ADMIN_USERNAME)):
                        parts = message.split()
                        if len(parts) >= 2:
                            username = parts[1].replace("@", "")
                            if follow_user(client, username):
                                send_direct_message(client, user_id,
                                    f"تم قبول متابعة @{username}")
                    
                    elif message.startswith("/حذف"):
                        try:
                            client.direct_thread_hide(thread_id)
                            send_direct_message(client, user_id,
                                "✅ تم إخفاء المحادثة بنجاح\n"
                                "لإعادة التشغيل، اكتب /start في رسالة جديدة")
                        except Exception as e:
                            send_direct_message(client, user_id,
                                "❌ تعذر إخفاء المحادثة")
                
                except Exception as e:
                    logging.error(f"خطأ في معالجة رسالة: {e}")
    except Exception as e:
        logging.error(f"خطأ في معالجة الرسائل: {e}")

def send_scheduled_adhkar(client):
    """إرسال الأذكار حسب التوقيت"""
    current_hour = get_algeria_time()
    adhkar = None
    time_type = ""
    
    if 6 <= current_hour < 9:
        adhkar = MORNING_ADHKAR
        time_type = "الصباح 🌄"
    elif 18 <= current_hour < 21:
        adhkar = EVENING_ADHKAR
        time_type = "المساء 🌆"
    elif 21 <= current_hour < 23:
        adhkar = NIGHT_ADHKAR
        time_type = "النوم 🌙"
    
    if adhkar and active_users:
        for user_id in active_users:
            zikr = random.choice(adhkar)
            send_direct_message(client, user_id,
                f"📖 ذكر {time_type}:\n\n{zikr}\n\n"
                f"الوقت: {datetime.now().strftime('%H:%M')} (توقيت الجزائر)")
            time.sleep(10)  # تأخير بين الإرسال

def main():
    """الدالة الرئيسية"""
    client = Client()
    client.delay_range = [2, 5]  # تقليل سرعة الإجراءات
    
    # تسجيل الدخول
    try:
        client.login(BOT_USERNAME, BOT_PASSWORD)
        logging.info("✅ تم تسجيل الدخول بنجاح")
    except Exception as e:
        logging.error(f"❌ فشل تسجيل الدخول: {e}")
        return
    
    # معلومات الحساب
    try:
        bot_user_id = client.user_id
        logging.info(f"🔹 البوت يعمل باسم: @{client.username}")
    except Exception as e:
        logging.error(f"خطأ في جلب معلومات البوت: {e}")
        return
    
    # الدورة الرئيسية
    while True:
        try:
            logging.info("🔁 جاري فحص الأنشطة...")
            
            # 1. المتابعون الجدد
            try:
                followers = client.user_followers(bot_user_id, amount=15)
                for user_id, user_info in followers.items():
                    if user_id not in [u["user_id"] for u in follow_requests]:
                        handle_new_follower(client, user_id, user_info.username)
            except Exception as e:
                logging.error(f"خطأ في فحص المتابعين: {e}")
            
            # 2. معالجة الرسائل
            process_new_messages(client)
            
            # 3. إرسال الأذكار
            send_scheduled_adhkar(client)
            
            time.sleep(180)  # كل 3 دقائق
            
        except KeyboardInterrupt:
            logging.info("⏹️ إيقاف البوت...")
            break
        except Exception as e:
            logging.error(f"🔥 خطأ غير متوقع: {e}")
            time.sleep(60)

if __name__ == "__main__":
    logging.info("🚀 بدء تشغيل بوت الأذكار...")
    main()
