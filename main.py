import random
import requests
import logging
import time
import filetype   
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# إعدادات البوت
BOT_TOKEN = "7882447585:AAFRX4Q6eqhN5uoJvv45O3ACrY7fvFFF2nI"
ADMIN_ID = 6212199357

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قوائم الأذكار
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

# تخزين بيانات المستخدمين
active_users = set()
user_data = {}

def get_algeria_time():
    now = datetime.utcnow() + timedelta(hours=1)  # UTC+1
    return now, now.strftime("%H:%M")

def get_next_adhkar_time():
    now, _ = get_algeria_time()
    hour = now.hour
    if hour < 6:
        next_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        adhkar_type = "أذكار الصباح"
    elif 6 <= hour < 18:
        next_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
        adhkar_type = "أذكار المساء"
    elif 18 <= hour < 21:
        next_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        adhkar_type = "أذكار الليل"
    else:
        next_time = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
        adhkar_type = "أذكار الصباح"
    time_left = next_time - now
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    return adhkar_type, hours, minutes, next_time.strftime("%H:%M")

async def send_quran_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now, time_str = get_algeria_time()
    verse = random.choice(QURAN_VERSES)
    await update.message.reply_text(f"📖 آية عشوائية | {time_str}\n\n{verse}")

async def send_random_adhkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now, time_str = get_algeria_time()
    all_adhkar = MORNING_ADHKAR + EVENING_ADHKAR + NIGHT_ADHKAR
    await update.message.reply_text(
        f"📿 ذكر عشوائي | {time_str}\n\n{random.choice(all_adhkar)}"
    )

async def send_random_verse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now, time_str = get_algeria_time()
    verse = random.choice(QURAN_VERSES)
    response = f"📖 آية قرآنية | {time_str}\n\n{verse}"
    await update.message.reply_text(response)

async def time_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    adhkar_type, hours, minutes, next_time = get_next_adhkar_time()
    message = (
        f"⏳ الأذكار القادمة: {adhkar_type}\n"
        f"⏱ الوقت المتبقي: {hours} ساعة و {minutes} دقيقة\n"
        f"🕒 الموعد: {next_time}"
    )
    await update.message.reply_text(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now, time_str = get_algeria_time()
    user = update.effective_user
    uid = user.id
    active_users.add(uid)
    user_data[uid] = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'join_date': now.strftime("%Y-%m-%d %H:%M:%S")
    }
    start_msg = f"""
✨ *مرحباً بك في بوت الأذكار والقرآن* ✨

👋 أهلًا وسهلاً بك {user.first_name}!
🕒 توقيت الجزائر: {time_str}

⚡️ *الأوامر المتاحة:*
/start - عرض هذه الرسالة
/quran - تلاوة قرآنية عشوائية
/adhkar - ذكر عشوائي
/verse - آية قرآنية مكتوبة
/timeleft - الوقت المتبقي للأذكار القادمة

📖 سيتم إرسال آية قرآنية تلقائياً كل 35 دقيقة

تم تطوير البوت بواسطة خليل
"""
    await update.message.reply_text(start_msg, parse_mode="Markdown")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quran", send_quran_audio))
    application.add_handler(CommandHandler("adhkar", send_random_adhkar))
    application.add_handler(CommandHandler("verse", send_random_verse))
    application.add_handler(CommandHandler("timeleft", time_left))
    application.run_polling()
    logger.info("تم تشغيل البوت بنجاح...")

if __name__ == "__main__":
    main()
