import os
import time
import random
from datetime import datetime
import requests
import logging
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# إعدادات البوت
BOT_TOKEN = "7882447585:AAFRX4Q6eqhN5uoJvv45O3ACrY7fvFFF2nI"
ADMIN_ID = 6212199357

# قوائم الأذكار
MORNING_ADHKAR = ["أصبحنا وأصبح الملك لله...", "اللهم بك أصبحنا..."]
EVENING_ADHKAR = ["أمسينا وأمسى الملك لله...", "اللهم بك أمسينا..."]
NIGHT_ADHKAR = ["باسم الله الذي لا يضر...", "آية الكرسي..."]
QURAN_VERSES = ["إِنَّ مَعَ الْعُسْرِ يُسْرًا...", "وَمَن يَتَّقِ اللَّهَ..."]

# متغيرات البوت
active_users = set()
verse_sent_today = set()

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_algeria_time():
    return (datetime.utcnow().hour + 1) % 24

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    if user_id not in active_users:
        active_users.add(user_id)
        welcome_msg = (
            "✨ *مرحباً بك في بوت الأذكار والقرآن* ✨\n\n"
            "تم تطوير هذا البوت بواسطة *خليل*\n"
            "سوف تصلك الأذكار اليومية تلقائياً حسب التوقيت:\n"
            "- أذكار الصباح (6-9 ص)\n"
            "- أذكار المساء (6-9 م)\n"
            "- أذكار النوم (9-11 م)\n\n"
            "📜 *الأوامر المتاحة:*\n"
            "/start - عرض هذه الرسالة\n"
            "/quran - استماع إلى تلاوة قرآنية\n"
            "/sura 36 - سورة محددة\n"
            "/adhkar - عرض أذكار متنوعة\n"
            "/verse - آية قرآنية عشوائية"
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_msg, parse_mode="Markdown")
        current_hour = get_algeria_time()
        if 6 <= current_hour < 9:
            send_morning_adhkar(context, user_id)
        elif 18 <= current_hour < 21:
            send_evening_adhkar(context, user_id)
        elif 21 <= current_hour < 23:
            send_night_adhkar(context, user_id)

def send_morning_adhkar(context: CallbackContext, chat_id):
    zikr = random.choice(MORNING_ADHKAR)
    context.bot.send_message(chat_id=chat_id, text=f"🌞 *ذكر الصباح*\n\n{zikr}", parse_mode="Markdown")

def send_evening_adhkar(context: CallbackContext, chat_id):
    zikr = random.choice(EVENING_ADHKAR)
    context.bot.send_message(chat_id=chat_id, text=f"🌙 *ذكر المساء*\n\n{zikr}", parse_mode="Markdown")

def send_night_adhkar(context: CallbackContext, chat_id):
    zikr = random.choice(NIGHT_ADHKAR)
    context.bot.send_message(chat_id=chat_id, text=f"🌌 *ذكر النوم*\n\n{zikr}", parse_mode="Markdown")

def send_random_verse(context: CallbackContext):
    for user_id in active_users:
        verse = random.choice(QURAN_VERSES)
        while verse in verse_sent_today:
            verse = random.choice(QURAN_VERSES)
        verse_sent_today.add(verse)
        context.bot.send_message(chat_id=user_id, text=f"📖 *آية قرآنية*\n\n{verse}", parse_mode="Markdown")

def send_random_verse_command(update: Update, context: CallbackContext):
    verse = random.choice(QURAN_VERSES)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"📖 *آية قرآنية*\n\n{verse}", parse_mode="Markdown")

def send_random_adhkar(update: Update, context: CallbackContext):
    all_adhkar = MORNING_ADHKAR + EVENING_ADHKAR + NIGHT_ADHKAR
    zikr = random.choice(all_adhkar)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"📿 *ذكر متنوع*\n\n{zikr}", parse_mode="Markdown")

def send_quran_audio(update: Update, context: CallbackContext):
    try:
        surah_number = random.randint(1, 114)
        edition = "ar.alafasy"
        api_url = f"http://api.alquran.cloud/v1/quran/{edition}"
        resp = requests.get(api_url)
        resp.raise_for_status()
        data = resp.json()
        surah = data["data"]["surahs"][surah_number - 1]
        audio_url = surah["audio"]
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio_url, caption=f"🎧 تلاوة سورة {surah['englishName']}")
    except Exception as e:
        logger.error(f"خطأ في جلب التلاوة: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="❌ حدث خطأ أثناء تحميل التلاوة.")

def send_specific_surah_audio(update: Update, context: CallbackContext):
    try:
        if not context.args:
            update.message.reply_text("❗️ من فضلك أرسل رقم السورة مثل: /sura 55")
            return
        surah_number = int(context.args[0])
        if not 1 <= surah_number <= 114:
            update.message.reply_text("❗️ رقم السورة يجب أن يكون بين 1 و 114.")
            return
        edition = "ar.alafasy"
        api_url = f"http://api.alquran.cloud/v1/quran/{edition}"
        resp = requests.get(api_url)
        resp.raise_for_status()
        data = resp.json()
        surah = data["data"]["surahs"][surah_number - 1]
        audio_url = surah["audio"]
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio_url, caption=f"🎧 تلاوة سورة {surah['englishName']}")
    except Exception as e:
        logger.error(f"خطأ في أمر /sura: {e}")
        update.message.reply_text("⚠️ حدث خطأ أثناء جلب التلاوة.")

def scheduled_jobs(context: CallbackContext):
    current_hour = get_algeria_time()
    if 6 <= current_hour < 9:
        for user_id in active_users:
            send_morning_adhkar(context, user_id)
    elif 18 <= current_hour < 21:
        for user_id in active_users:
            send_evening_adhkar(context, user_id)
    elif 21 <= current_hour < 23:
        for user_id in active_users:
            send_night_adhkar(context, user_id)
    send_random_verse(context)

def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="حدث خطأ في البوت:", exc_info=context.error)

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("quran", send_quran_audio))
    dispatcher.add_handler(CommandHandler("sura", send_specific_surah_audio))
    dispatcher.add_handler(CommandHandler("adhkar", send_random_adhkar))
    dispatcher.add_handler(CommandHandler("verse", send_random_verse_command))
    dispatcher.add_error_handler(error_handler)
    job_queue = updater.job_queue
    job_queue.run_repeating(scheduled_jobs, interval=3600, first=0)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
