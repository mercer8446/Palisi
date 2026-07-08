import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import uuid
import threading
import time

TOKEN = "8961252412:AAGuTxDAw1aoH6jw9ujmX0g4HQRUKgY0bjg"
ADMIN_ID = 1279226047
CHANNELS = ["@House_Mistress",]

bot = telebot.TeleBot(TOKEN)
DB_FILE = "videos.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

db = load_db()

def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def delete_after(chat_id, messages_to_delete):
    time.sleep(30)
    for msg_id in messages_to_delete:
        try:
            bot.delete_message(chat_id, msg_id)
        except:
            pass

def check_membership(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

def get_join_keyboard(key):
    markup = InlineKeyboardMarkup()
    for channel in CHANNELS:
        url = f"https://t.me/{channel.replace('@', '')}"
        markup.add(InlineKeyboardButton("🔗 عضویت", url=url))
    
    markup.add(InlineKeyboardButton("✅ عضو شدم | فعال سازی", callback_data=f"join_{key}"))
    return markup

def send_video_to_user(chat_id, key):
    warning_msg = bot.send_message(
        chat_id,
        "⚠️ توجه!\n\n"
        "🎥 ویدیوی شما آماده ارسال است.\n"
        "🗑 این ویدیو پس از ۳۰ ثانیه به‌صورت خودکار حذف خواهد شد.\n"
        "💾 اگر قصد نگهداری آن را دارید، قبل از پایان زمان آن را ذخیره کنید."
    )

    # تشخیص نوع فایل (ویدیو معمولی یا دایره‌ای) و ارسال آن
    file_data = db[key]
    if isinstance(file_data, dict) and file_data.get("type") == "video_note":
        video_msg = bot.send_video_note(chat_id, file_data["file_id"])
    else:
        file_id = file_data["file_id"] if isinstance(file_data, dict) else file_data
        video_msg = bot.send_video(chat_id, file_id)

    threading.Thread(
        target=delete_after,
        args=(chat_id, [warning_msg.message_id, video_msg.message_id])
    ).start()


@bot.message_handler(commands=["start"])
def start(message):
    parts = message.text.split()  
    key = parts[1] if len(parts) == 2 else "none"

    if not check_membership(message.from_user.id):
        bot.reply_to(
            message,
            "برای استفاده از ربات لطفا داخل کانالهای زیر عضو شوید:",
            reply_markup=get_join_keyboard(key)
        )
        return

    if key != "none" and key in db:
        send_video_to_user(message.chat.id, key)
    else:
        if key == "none":
            bot.reply_to(message, "توله الکی پیام نده")
        else:
            bot.reply_to(message, "❌ لینک نامعتبر است یا ویدیو از سرور حذف شده است.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("join_"))
def handle_join_callback(call):
    key = call.data.split("_")[1]
    
    if not check_membership(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ هنوز در همه کانال‌ها عضو نشده‌اید!", show_alert=True)
        return

    bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!")
    bot.delete_message(call.message.chat.id, call.message.message_id)

    if key != "none" and key in db:
        send_video_to_user(call.message.chat.id, key)
    elif key == "none":
        bot.send_message(call.message.chat.id, "توله الکی پیام نده")
    else:
        bot.send_message(call.message.chat.id, "❌ لینک نامعتبر است یا ویدیو از سرور حذف شده است.")

# تابع مشترک برای ذخیره ویدیوها و فیلم‌های دایره‌ای
def process_and_save_video(message, file_id, is_note=False):
    if message.from_user.id != ADMIN_ID:  
        return  

    key = uuid.uuid4().hex[:8]  
    db[key] = {
        "file_id": file_id,
        "type": "video_note" if is_note else "video"
    }
    save_db()  

    me = bot.get_me()  
    link = f"https://t.me/{me.username}?start={key}"  

    bot.reply_to(  
        message,  
        "✅ لینک اختصاصی ساخته شد:\n\n" + link  
    )

# هندلر ویدیوهای معمولی
@bot.message_handler(content_types=["video"])
def receive_video(message):
    process_and_save_video(message, message.video.file_id, is_note=False)

# هندلر ویدیوهای دایره‌ای (Video Note)
@bot.message_handler(content_types=["video_note"])
def receive_video_note(message):
    process_and_save_video(message, message.video_note.file_id, is_note=True)

print("Bot Started... Waiting for messages.")
bot.infinity_polling(skip_pending=True)

