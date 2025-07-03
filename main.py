import random
import requests
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = "7882447585:AAFRX4Q6eqhN5uoJvv45O3ACrY7fvFFF2nI"
ADMIN_ID = 6212199357

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# أذكار
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
verse_sent_today = set()

def get_algeria_time():
    return datetime.utcnow() + timedelta(hours=1)

def send_morning_adhkar(context, chat_id):
    context.bot.send_message(chat_id, f"🌞 *ذكر الصباح*\n\n{random.choice(MORNING_ADHKAR)}", parse_mode="Markdown")

def send_evening_adhkar(context, chat_id):
    context.bot.send_message(chat_id, f"🌙 *ذكر المساء*\n\n{random.choice(EVENING_ADHKAR)}", parse_mode="Markdown")

def send_night_adhkar(context, chat_id):
    context.bot.send_message(chat_id, f"🌌 *ذكر النوم*\n\n{random.choice(NIGHT_ADHKAR)}", parse_mode="Markdown")

def send_random_verse(context):
    for uid in active_users:
        verse = random.choice(QURAN_VERSES)
        if verse not in verse_sent_today:
            context.bot.send_message(uid, f"📖 *آية قرآنية*\n\n{verse}", parse_mode="Markdown")
            verse_sent_today.add(verse)

def send_quran_audio(update: Update, context: CallbackContext):
    surah = random.randint(1, 114)
    surah_str = str(surah).zfill(3)
     url = f"https://server7.mp3quran.net/s_gmd/{surah_str}.mp3""
    try:
        context.bot.send_audio(update.effective_chat.id, audio=url, caption=f"🎧 تلاوة سورة رقم {surah}")
    except Exception as e:
        logger.error(f"خطأ في إرسال التلاوة: {e}")
        context.bot.send_message(update.effective_chat.id, "⚠️ حدث خطأ أثناء إرسال التلاوة الصوتية. حاول لاحقًا.")

def send_specific_surah_audio(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❗️ من فضلك أرسل رقم السورة مثال: /sura 55")
        return
    try:
        surah = int(context.args[0])
        if not 1 <= surah <= 114:
            raise ValueError
    except:
        update.message.reply_text("❗️ رقم السورة يجب أن يكون بين 1 و114.")
        return

    surah_str = str(surah).zfill(3)
    url = f"https://server.mp3quran.net/s_gmd/{surah_str}.mp3"
    try:
        context.bot.send_audio(update.effective_chat.id, audio=url, caption=f"🎧 تلاوة سورة رقم {surah}")
    except Exception as e:
        logger.error(f"خطأ في /sura: {e}")
        update.message.reply_text("⚠️ حدث خطأ أثناء إرسال التلاوة.")

def start(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    active_users.add(uid)
    update.message.reply_text(
         "✨ *مرحباً بك في بوت الأذكار والقرآن* ✨\n\n"
            "تم تطوير هذا البوت بواسطة *خليل*\n"
            "سوف تصلك الأذكار اليومية تلقائياً حسب التوقيت الجزائر:\n"
            "- أذكار الصباح (6-9 ص)\n"
            "- أذكار المساء (6-9 م)\n"
            "- أذكار النوم (9-11 م)\n\n"
            "📜 *الأوامر المتاحة:*\n"
            "/start - عرض هذه الرسالة\n"
            "/quran - استماع إلى تلاوة قرآنية\n"
            "/adhkar - عرض أذكار متنوعة\n"
            "/verse - آية قرآنية عشوائية\n\n"
            "سيتم إرسال آية قرآنية مكتوبة كل ساعة إن شاء الله",
        parse_mode="Markdown"
    )

def send_random_adhkar(update: Update, context: CallbackContext):
    all_adhkar = MORNING_ADHKAR + EVENING_ADHKAR + NIGHT_ADHKAR
    update.message.reply_text(f"📿 *ذكر*\n\n{random.choice(all_adhkar)}", parse_mode="Markdown")

def send_random_verse_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"📖 *آية قرآنية*\n\n{random.choice(QURAN_VERSES)}", parse_mode="Markdown")

def scheduled_jobs(context: CallbackContext):
    hour = get_algeria_time().hour
    for uid in active_users:
        if 6 <= hour < 9:
            send_morning_adhkar(context, uid)
        elif 18 <= hour < 21:
            send_evening_adhkar(context, uid)
        elif 21 <= hour < 23:
            send_night_adhkar(context, uid)
    send_random_verse(context)

def error_handler(update: Update, context: CallbackContext):
    logger.error("حدث خطأ في البوت:", exc_info=context.error)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("quran", send_quran_audio))
    dp.add_handler(CommandHandler("sura", send_specific_surah_audio))
    dp.add_handler(CommandHandler("adhkar", send_random_adhkar))
    dp.add_handler(CommandHandler("verse", send_random_verse_command))
    dp.add_error_handler(error_handler)

    job = updater.job_queue
    job.run_repeating(scheduled_jobs, interval=3600, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
