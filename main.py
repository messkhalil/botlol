import os
import time
import random
from datetime import datetime
import requests
import logging
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# إعدادات البوت
BOT_TOKEN = "توكن_بوتك_هنا"
ADMIN_ID = 123456789  # أضف آيدي حسابك هنا

# قوائم الأذكار الكبيرة والمتنوعة
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

QURAN_AUDIO = [
    "https://server.mp3quran.net/s_gmd/001.mp3",  # الفاتحة
    "https://server.mp3quran.net/s_gmd/112.mp3",  # الإخلاص
    "https://server.mp3quran.net/s_gmd/113.mp3",  # الفلق
    "https://server.mp3quran.net/s_gmd/114.mp3",  # الناس
    "https://server.mp3quran.net/s_gmd/002.mp3",  # البقرة (آية الكرسي)
    "https://server.mp3quran.net/s_gmd/036.mp3",  # يس
    "https://server.mp3quran.net/s_gmd/067.mp3",  # الملك
    "https://server.mp3quran.net/s_gmd/055.mp3",  # الرحمن
    "https://server.mp3quran.net/s_gmd/078.mp3",  # النبأ
    "https://server.mp3quran.net/s_gmd/093.mp3"   # الضحى
]

# متغيرات البوت
active_users = set()
verse_sent_today = set()

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_algeria_time():
    """الحصول على توقيت الجزائر (UTC+1)"""
    return (datetime.utcnow().hour + 1) % 24

def start(update: Update, context: CallbackContext):
    """معالجة أمر /start"""
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
            "/adhkar - عرض أذكار متنوعة\n"
            "/verse - آية قرآنية عشوائية\n\n"
            "سيتم إرسال آية قرآنية مكتوبة كل ساعة إن شاء الله"
        )
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_msg,
            parse_mode="Markdown"
        )
        
        # إرسال أول ذكر بعد التسجيل
        current_hour = get_algeria_time()
        if 6 <= current_hour < 9:
            send_morning_adhkar(context, user_id)
        elif 18 <= current_hour < 21:
            send_evening_adhkar(context, user_id)
        elif 21 <= current_hour < 23:
            send_night_adhkar(context, user_id)

def send_morning_adhkar(context: CallbackContext, chat_id):
    """إرسال أذكار الصباح"""
    zikr = random.choice(MORNING_ADHKAR)
    context.bot.send_message(
        chat_id=chat_id,
        text=f"🌞 *ذكر الصباح*\n\n{zikr}",
        parse_mode="Markdown"
    )

def send_evening_adhkar(context: CallbackContext, chat_id):
    """إرسال أذكار المساء"""
    zikr = random.choice(EVENING_ADHKAR)
    context.bot.send_message(
        chat_id=chat_id,
        text=f"🌙 *ذكر المساء*\n\n{zikr}",
        parse_mode="Markdown"
    )

def send_night_adhkar(context: CallbackContext, chat_id):
    """إرسال أذكار النوم"""
    zikr = random.choice(NIGHT_ADHKAR)
    context.bot.send_message(
        chat_id=chat_id,
        text=f"🌌 *ذكر النوم*\n\n{zikr}",
        parse_mode="Markdown"
    )

def send_random_verse(context: CallbackContext):
    """إرسال آية قرآنية عشوائية كل ساعة"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    for user_id in active_users:
        verse = random.choice(QURAN_VERSES)
        while verse in verse_sent_today:
            verse = random.choice(QURAN_VERSES)
            
        verse_sent_today.add(verse)
        
        context.bot.send_message(
            chat_id=user_id,
            text=f"📖 *آية قرآنية*\n\n{verse}",
            parse_mode="Markdown"
        )

def send_quran_audio(update: Update, context: CallbackContext):
    """إرسال تلاوة قرآنية"""
    audio = random.choice(QURAN_AUDIO)
    context.bot.send_audio(
        chat_id=update.effective_chat.id,
        audio=audio,
        caption="🎧 تلاوة قرآنية"
    )

def send_random_adhkar(update: Update, context: CallbackContext):
    """إرسال أذكار متنوعة"""
    all_adhkar = MORNING_ADHKAR + EVENING_ADHKAR + NIGHT_ADHKAR
    zikr = random.choice(all_adhkar)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📿 *ذكر متنوع*\n\n{zikr}",
        parse_mode="Markdown"
    )

def send_random_verse_command(update: Update, context: CallbackContext):
    """إرسال آية قرآنية عند الطلب"""
    verse = random.choice(QURAN_VERSES)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📖 *آية قرآنية*\n\n{verse}",
        parse_mode="Markdown"
    )

def scheduled_jobs(context: CallbackContext):
    """المهام المجدولة"""
    current_hour = get_algeria_time()
    
    # إرسال الأذكار حسب الوقت
    if 6 <= current_hour < 9:
        for user_id in active_users:
            send_morning_adhkar(context, user_id)
    elif 18 <= current_hour < 21:
        for user_id in active_users:
            send_evening_adhkar(context, user_id)
    elif 21 <= current_hour < 23:
        for user_id in active_users:
            send_night_adhkar(context, user_id)
    
    # إرسال آية قرآنية كل ساعة
    send_random_verse(context)

def error_handler(update: Update, context: CallbackContext):
    """معالجة الأخطاء"""
    logger.error(msg="حدث خطأ في البوت:", exc_info=context.error)

def main():
    """الدالة الرئيسية"""
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # تعريف الأوامر
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("quran", send_quran_audio))
    dispatcher.add_handler(CommandHandler("adhkar", send_random_adhkar))
    dispatcher.add_handler(CommandHandler("verse", send_random_verse_command))

    # معالجة الأخطاء
    dispatcher.add_error_handler(error_handler)

    # المهام المجدولة
    job_queue = updater.job_queue
    job_queue.run_repeating(scheduled_jobs, interval=3600, first=0)  # كل ساعة

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
