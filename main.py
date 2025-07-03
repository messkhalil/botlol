import random
import requests
import logging
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = "7882447585:AAFRX4Q6eqhN5uoJvv45O3ACrY7fvFFF2nI"
ADMIN_ID = 6212199357

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قوائم الأذكار (يجب استكمالها)
MORNING_ADHKAR = [
    "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "اللهم بك أصبحنا، وبك أمسينا، وبك نحيا، وبك نموت، وإليك النشور.",
    "سبحان الله وبحمده عدد خلقه ورضا نفسه وزنة عرشه ومداد كلماته.",
    "اللهم إني أصبحت منك في نعمة وعافية وستر، فأتم نعمتك علي وعافيتك وسترك في الدنيا والآخرة.",
    "أصبحنا على فطرة الإسلام، وكلمة الإخلاص، ودين نبينا محمد صلى الله عليه وسلم، وملة أبينا إبراهيم حنيفاً مسلماً وما كان من المشركين.",
    "اللهم ما أصبح بي من نعمة أو بأحد من خلقك فمنك وحدك لا شريك لك، فلك الحمد ولك الشكر.",
    "حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم.",
    "اللهم إني أسألك علماً نافعاً، ورزقاً طيباً، وعملاً متقبلاً.",
    "سبحان الله العظيم وبحمده، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "أعوذ بكلمات الله التامات من شر ما خلق."
]

EVENING_ADHKAR = [
    "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "اللهم بك أمسينا، وبك أصبحنا، وبك نحيا، وبك نموت، وإليك المصير.",
    "أعوذ بكلمات الله التامات من شر ما خلق.",
    "اللهم إني أمسيت منك في نعمة وعافية وستر، فأتم نعمتك علي وعافيتك وسترك في الدنيا والآخرة.",
    "أمسينا على فطرة الإسلام، وكلمة الإخلاص، ودين نبينا محمد صلى الله عليه وسلم، وملة أبينا إبراهيم حنيفاً مسلماً وما كان من المشركين.",
    "اللهم ما أمسى بي من نعمة أو بأحد من خلقك فمنك وحدك لا شريك لك، فلك الحمد ولك الشكر.",
    "حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم.",
    "اللهم إني أسألك العفو والعافية في الدنيا والآخرة، اللهم إني أسألك العفو والعافية في ديني ودنياي وأهلي ومالي.",
    "سبحان الله العظيم وبحمده، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "أعوذ بالله من الشيطان الرجيم: {آية الكرسي}"
]

NIGHT_ADHKAR = [
    "باسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم.",
    "آية الكرسي: الله لا إله إلا هو الحي القيوم لا تأخذه سنة ولا نوم له ما في السماوات وما في الأرض...",
    "أعوذ برب الفلق، من شر ما خلق، ومن شر غاسق إذا وقب، ومن شر النفاثات في العقد، ومن شر حاسد إذا حسد.",
    "أعوذ برب الناس، ملك الناس، إله الناس، من شر الوسواس الخناس، الذي يوسوس في صدور الناس، من الجنة والناس.",
    "اللهم رب السماوات ورب الأرض ورب العرش العظيم، ربنا ورب كل شيء، فالق الحب والنوى، ومنزل التوراة والإنجيل والفرقان، أعوذ بك من شر كل شيء أنت آخذ بناصيته، اللهم أنت الأول فليس قبلك شيء، وأنت الآخر فليس بعدك شيء، وأنت الظاهر فليس فوقك شيء، وأنت الباطن فليس دونك شيء، اقض عنا الدين وأغننا من الفقر.",
    "بسم الله وضعت جنبي، اللهم اغفر لي ذنبي، وأخسئ شيطاني، وفك رهاني، واجعلني في الندي الأعلى.",
    "اللهم أسلمت نفسي إليك، ووجهت وجهي إليك، وفوضت أمري إليك، وألجأت ظهري إليك، رغبة ورهبة إليك، لا ملجأ ولا منجا منك إلا إليك، آمنت بكتابك الذي أنزلت، وبنبيك الذي أرسلت.",
    "سبحان الله (33 مرة)، الحمد لله (33 مرة)، الله أكبر (34 مرة).",
    "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "اللهم عالم الغيب والشهادة، فاطر السماوات والأرض، رب كل شيء ومليكه، أشهد أن لا إله إلا أنت، أعوذ بك من شر نفسي ومن شر الشيطان وشركه."
]

QURAN_VERSES = [
    "إِنَّ مَعَ الْعُسْرِ يُسْرًا ﴿٥﴾ فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ﴿٦﴾ (الشرح:5-6)",
    "وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا ﴿٢﴾ وَيَرْزُقْهُ مِنْ حَيْثُ لَا يَحْتَسِبُ (الطلاق:2-3)",
    "رَّبِّ أَدْخِلْنِي مُدْخَلَ صِدْقٍ وَأَخْرِجْنِي مُخْرَجَ صِدْقٍ وَاجْعَل لِّي مِن لَّدُنكَ سُلْطَانًا نَّصِيرًا (الإسراء:80)",
    "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ (آية الكرسي)",
    "وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ (الطلاق:3)",
    "فَإِنَّ اللَّهَ هُوَ الْغَفُورُ الرَّحِيمُ (الحشر:22)",
    "وَقُل رَّبِّ أَنزِلْنِي مُنزَلًا مُّبَارَكًا وَأَنتَ خَيْرُ الْمُنزِلِينَ (المؤمنون:29)",
    "وَذَكِّرْ فَإِنَّ الذِّكْرَىٰ تَنفَعُ الْمُؤْمِنِينَ (الذاريات:55)",
    "وَإِذَا سَأَلَكَ عِبَادِي عَنِّي فَإِنِّي قَرِيبٌ أُجِيبُ دَعْوَةَ الدَّاعِ إِذَا دَعَانِ (البقرة:186)",
    "وَمَا تَوْفِيقِي إِلَّا بِاللَّهِ عَلَيْهِ تَوَكَّلْتُ وَإِلَيْهِ أُنِيبُ (هود:88)"
]

active_users = set()

def get_algeria_time():
    """الحصول على وقت الجزائر مع التنسيق"""
    now = datetime.utcnow() + timedelta(hours=1)  # UTC+1
    return now, now.strftime("%H:%M")

def get_surah_audio(surah_number):
    """الحصول على سورة كاملة بصوت"""
    try:
        response = requests.get(f"https://cdn.islamic.network/quran/audio-surah/128k/ar.abdulbasitmurattal/{number}.mp3")
        data = response.json()
        
        if data['code'] == 200:
            return {
                'name': data['data']['name'],
                'english_name': data['data']['englishName'],
                'ayahs': data['data']['ayahs']
            }
    except Exception as e:
        logger.error(f"خطأ في جلب السورة: {e}")
    return None

def get_random_verse_with_audio():
    """الحصول على آية عشوائية مع صوت"""
    try:
        surah = random.randint(1, 114)
        response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/ar.alafasy")
        data = response.json()
        
        if data['code'] == 200:
            verses = data['data']['ayahs']
            verse = random.choice(verses)
            return {
                'text': verse['text'],
                'audio': verse['audio'],
                'surah_name': data['data']['name'],
                'ayah_number': verse['numberInSurah']
            }
    except Exception as e:
        logger.error(f"خطأ في جلب الآية: {e}")
    return None

def send_quran_audio(update: Update, context: CallbackContext):
    """إرسال تلاوة عشوائية"""
    now, time_str = get_algeria_time()
    verse = get_random_verse_with_audio()
    
    if verse:
        try:
            update.message.reply_text(
                f"📖 تم اختيار آية من سورة {verse['surah_name']} - الآية {verse['ayah_number']}"
            )
            context.bot.send_audio(
                update.effective_chat.id,
                audio=verse['audio'],
                caption=f"🎧 تلاوة قرآنية | {time_str}"
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال التلاوة: {e}")
            update.message.reply_text("⚠️ حدث خطأ أثناء إرسال التلاوة")
    else:
        update.message.reply_text("⚠️ تعذر جلب التلاوة، حاول لاحقاً")

def send_surah(update: Update, context: CallbackContext):
    """إرسال سورة كاملة"""
    now, time_str = get_algeria_time()
    
    if not context.args:
        update.message.reply_text("⚠️ يرجى تحديد رقم السورة (1-114)\nمثال: /sura 1")
        return
    
    try:
        surah_num = int(context.args[0])
        if not 1 <= surah_num <= 114:
            raise ValueError
    except:
        update.message.reply_text("⚠️ رقم السورة يجب أن يكون بين 1 و114")
        return
    
    surah = get_surah_audio(surah_num)
    if not surah:
        update.message.reply_text("⚠️ تعذر جلب السورة، حاول لاحقاً")
        return
    
    update.message.reply_text(f"📖 جاري إرسال سورة {surah['name']}...")
    
    for ayah in surah['ayahs']:
        try:
            context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=ayah['audio'],
                caption=f"{surah['name']} - الآية {ayah['numberInSurah']}",
                timeout=30
            )
            time.sleep(1)
        except Exception as e:
            logger.error(f"خطأ في إرسال الآية: {e}")
            continue

def send_morning_adhkar(context: CallbackContext):
    now, time_str = get_algeria_time()
    for uid in active_users:
        context.bot.send_message(
            uid,
            f"🌞 ذكر الصباح | {time_str}\n\n{random.choice(MORNING_ADHKAR)}"
        )

def send_evening_adhkar(context: CallbackContext):
    now, time_str = get_algeria_time()
    for uid in active_users:
        context.bot.send_message(
            uid,
            f"🌙 ذكر المساء | {time_str}\n\n{random.choice(EVENING_ADHKAR)}"
        )

def send_night_adhkar(context: CallbackContext):
    now, time_str = get_algeria_time()
    for uid in active_users:
        context.bot.send_message(
            uid,
            f"🌌 ذكر النوم | {time_str}\n\n{random.choice(NIGHT_ADHKAR)}"
        )

def send_random_adhkar(update: Update, context: CallbackContext):
    """إرسال ذكر عشوائي"""
    now, time_str = get_algeria_time()
    all_adhkar = MORNING_ADHKAR + EVENING_ADHKAR + NIGHT_ADHKAR
    update.message.reply_text(
        f"📿 ذكر عشوائي | {time_str}\n\n{random.choice(all_adhkar)}"
    )

def start(update: Update, context: CallbackContext):
    now, time_str = get_algeria_time()
    uid = update.effective_user.id
    active_users.add(uid)
    
    start_msg = f"""
✨ *مرحباً بك في بوت الأذكار والقرآن* ✨

🕒 توقيت الجزائر: {time_str}

⚡️ *الأوامر المتاحة:*
/start - عرض هذه الرسالة
/quran - تلاوة عشوائية
/sura [رقم] - سورة كاملة
/adhkar - ذكر عشوائي

تم تطوير البوت بواسطة خليل
"""
    update.message.reply_text(start_msg, parse_mode="Markdown")

def scheduled_jobs(context: CallbackContext):
    """المهام المجدولة"""
    now, time_str = get_algeria_time()
    hour = now.hour
    
    if 6 <= hour < 9:
        send_morning_adhkar(context)
    elif 18 <= hour < 21:
        send_evening_adhkar(context)
    elif 21 <= hour < 23:
        send_night_adhkar(context)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # تعريف الأوامر
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("quran", send_quran_audio))
    dp.add_handler(CommandHandler("sura", send_surah))
    dp.add_handler(CommandHandler("adhkar", send_random_adhkar))
    
    # الجدولة
    job_queue = updater.job_queue
    job_queue.run_repeating(scheduled_jobs, interval=3600, first=0)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
