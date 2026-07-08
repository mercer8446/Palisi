import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8506329567:AAEoiyOGiKWWu5tf1aWXdVcA2cFp1Sc3eXQ"
REQUIRED_CHANNEL = "@mercervpn"
SUPPORT_ID = "devil0night" 

bot = telebot.TeleBot(TOKEN)

CARD_NUMBER = "5054161703553101"
CARD_NAME = "پویا بیک محمدی"

PLANS = {
    "1": {"name": "🔹 90 گیگ + 10 گیگ هدیه (30 روزه)", "price": "390,000T"},
    "2": {"name": "🔹 180 گیگ + 20 گیگ هدیه (60 روزه)", "price": "520,000T"},
    "3": {"name": "🔹 270 گیگ + 30 گیگ هدیه (90 روزه)", "price": "620,000T"},
    "4": {"name": "🔹 360 گیگ + 40 گیگ هدیه (120 روزه)", "price": "840,000T"},
    "5": {"name": "🔹 ماهانه نامحدود", "price": "1,200,000T"},
}

def check_membership(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🛒 خرید اشتراک فیلترشکن"))
    markup.row(KeyboardButton("👤 حساب کاربری"), KeyboardButton("👨‍💻 پشتیبانی فروش"))
    return markup

def plans_keyboard():
    markup = InlineKeyboardMarkup()
    for key, plan in PLANS.items():
        markup.add(InlineKeyboardButton(f"{plan['name']} | {plan['price']}", callback_data=f"buy_{key}"))
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    if not check_membership(message.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 عضویت در کانال", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}"))
        bot.reply_to(message, "👋 ابتدا باید در کانال ما عضو شوید:", reply_markup=markup)
        return
    bot.send_message(message.chat.id, "🔥 به فروشگاه MERCER VPN خوش آمدید.\nجهت خرید یا پشتیبانی از منو استفاده کنید:", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if not check_membership(message.from_user.id): return
    
    if message.text == "🛒 خرید اشتراک فیلترشکن":
        bot.send_message(message.chat.id, "👇 یکی از پلن‌ها را انتخاب کنید:", reply_markup=plans_keyboard())
    elif message.text == "👤 حساب کاربری":
        bot.send_message(message.chat.id, f"👤 آیدی شما: `{message.from_user.id}`\nنام: {message.from_user.first_name}")
    elif message.text == "👨‍💻 پشتیبانی فروش":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🚀 ارتباط مستقیم با پشتیبانی", url=f"https://t.me/{SUPPORT_ID}"))
        bot.send_message(message.chat.id, "👨‍💻 جهت هرگونه سوال یا ارسال فیش به آیدی زیر پیام دهید:\n\n🎯 @{SUPPORT_ID}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    plan = PLANS[call.data.split("_")[1]]
    text = f"💳 **فاکتور خرید:**\n\n📦 پلن: {plan['name']}\n💰 مبلغ: {plan['price']}\n\n💳 شماره کارت:\n`{CARD_NUMBER}`\n👤 نام: {CARD_NAME}\n\n👇 پس از واریز، فیش را به آیدی زیر بفرستید:\n🎯 @{SUPPORT_ID}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📸 ارسال فیش به پشتیبانی", url=f"https://t.me/{SUPPORT_ID}"))
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

print("MERCER Bot Started...")
bot.infinity_polling()

