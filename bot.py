import telebot
from telebot import types
import json
import os
from datetime import datetime

# ================= CONFIG =================
TOKEN = "8346099917:AAFlIuH9OEbPQKrJRhzVT5AvTof3frv5ThE"
ADMIN_ID = 7517279474

USERS_FILE = "users.json"
WORK_FILE = "work_submissions.json"
PRICE_REQUEST_FILE = "price_requests.json"
BANK_FILE = "bank_submissions.json"

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
user_state = {}
processed_messages = set()  # Store approved/rejected messages to prevent duplicates

# ================= FILE HELPERS =================
def init_file(file):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    items = load_json(file)
    items.append(data)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)

def save_user(uid):
    users = load_json(USERS_FILE)
    if uid not in users:
        users.append(uid)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)

def reset(uid):
    user_state.pop(uid, None)

# ================= INIT FILES =================
for f in [USERS_FILE, WORK_FILE, PRICE_REQUEST_FILE, BANK_FILE]:
    init_file(f)

# ================= MENUS =================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📤 Submit Work", "🔥 Today Price")
    kb.row("📚 Learning", "🌐 Join Groups")
    kb.row("🧑‍💼 Customer Care", "🏦 Add Your Bank")
    kb.row("🔁 Cancel & Back")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📢 Broadcast to All Users")
    kb.row("📋 View All Users")
    kb.row("🔁 Cancel & Back")
    return kb

# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    reset(m.chat.id)
    save_user(m.chat.id)
    if m.chat.id == ADMIN_ID:
        bot.send_message(m.chat.id, "👋 *WELCOME ADMIN*", reply_markup=admin_menu())
    else:
        bot.send_message(m.chat.id, "👋 *WELCOME*\nFollow the steps to use the bot.", reply_markup=main_menu())
        bot.send_message(ADMIN_ID,
                         f"👤 *NEW USER*\nName: {m.from_user.first_name}\nUsername: @{m.from_user.username or 'N/A'}\nID: `{m.chat.id}`")

# ================= SUBMIT WORK =================
@bot.message_handler(func=lambda m: m.text == "📤 Submit Work")
def submit_work(m):
    uid = m.chat.id
    reset(uid)
    user_state[uid] = {"step": "choose_category"}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row("1️⃣ Facebook Account", "2️⃣ Telegram Account")
    kb.row("3️⃣ WhatsApp Account", "4️⃣ Gmail Account")
    kb.row("5️⃣ Other (Specify)")
    kb.row("🔁 Cancel & Back")
    bot.send_message(uid, "📤 *SUBMIT WORK*\nChoose the type of account or work:", reply_markup=kb)

@bot.message_handler(content_types=["text", "photo", "document"])
def submit_flow(m):
    uid = m.chat.id
    if uid not in user_state:
        return
    step = user_state[uid].get("step")
    text = m.text.strip() if m.content_type == "text" else ""

    # Step 1: Choose Category
    if step == "choose_category" and m.content_type == "text":
        if text.startswith("1"):
            user_state[uid]["category"] = "Facebook Account"
            user_state[uid]["step"] = "facebook_type"
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            kb.row("a. Webmail 00frnd 2FA", "b. Hotmail 30frnd 2FA")
            kb.row("c. Webmail 30frnd 2FA", "d. Any Mail 00frnd 2FA")
            kb.row("e. Facebook Switch", "f. Old Facebook 2017-2020")
            kb.row("🔁 Cancel & Back")
            bot.send_message(uid, "📘 *Facebook Account*\nChoose the type of account:", reply_markup=kb)
        elif text.startswith("2"):
            user_state[uid]["category"] = "Telegram Account"
            user_state[uid]["step"] = "enter_telegram_number"
            bot.send_message(uid, "📲 Enter your Telegram Number:", reply_markup=types.ReplyKeyboardRemove())
        elif text.startswith("3"):
            user_state[uid]["category"] = "WhatsApp Account"
            user_state[uid]["step"] = "enter_whatsapp_number"
            bot.send_message(uid, "📱 Enter your WhatsApp Number:", reply_markup=types.ReplyKeyboardRemove())
        elif text.startswith("4"):
            user_state[uid]["category"] = "Gmail Account"
            user_state[uid]["step"] = "gmail_details"
            bot.send_message(uid, "📧 Enter full Gmail info:", reply_markup=types.ReplyKeyboardRemove())
        elif text.startswith("5"):
            user_state[uid]["category"] = "Other"
            user_state[uid]["step"] = "other_details"
            bot.send_message(uid, "✍️ Describe the type of work/account you want to sell:", reply_markup=types.ReplyKeyboardRemove())
        elif text == "🔁 Cancel & Back":
            reset(uid)
            bot.send_message(uid, "↩️ Returned to menu.", reply_markup=main_menu())
        else:
            bot.send_message(uid, "⚠️ Please choose from the provided options.")
        return

    # Step 2: Facebook specific
    if step == "facebook_type" and m.content_type == "text":
        fb_choice = text
        if fb_choice in ["a. Webmail 00frnd 2FA","b. Hotmail 30frnd 2FA","c. Webmail 30frnd 2FA","d. Any Mail 00frnd 2FA"]:
            user_state[uid]["details_step"] = "upload_file"
            user_state[uid]["facebook_type"] = fb_choice
            bot.send_message(uid, "📎 Upload a screenshot or file of the account:", reply_markup=types.ReplyKeyboardRemove())
        elif fb_choice in ["e. Facebook Switch", "f. Old Facebook 2017-2020"]:
            user_state[uid]["details_step"] = "credentials"
            bot.send_message(uid, "🔑 Enter Phone/Email and Password:", reply_markup=types.ReplyKeyboardRemove())
        elif fb_choice == "🔁 Cancel & Back":
            reset(uid)
            bot.send_message(uid, "↩️ Returned to menu.", reply_markup=main_menu())
        else:
            bot.send_message(uid, "⚠️ Please choose from the provided options.")
        return

    # Step 3: Other accounts (Telegram/WhatsApp/Gmail/Other)
    if step in ["enter_telegram_number","enter_whatsapp_number","other_details","gmail_details"] and m.content_type == "text":
        user_state[uid]["details_step"] = "upload_file"
        user_state[uid]["account_info"] = text
        bot.send_message(uid, "📎 Upload a file/screenshot/text for admin review:", reply_markup=types.ReplyKeyboardRemove())
        return

    # Step 4: Upload / Credentials
    if user_state[uid].get("details_step") in ["upload_file","credentials"]:
        category = user_state[uid]["category"]
        fb_type = user_state[uid].get("facebook_type","")
        extra = user_state[uid].get("account_info","")
        creds = text if user_state[uid].get("details_step")=="credentials" else ""
        username = m.from_user.username or "NoUsername"

        data = {
            "user_id": uid,
            "username": username,
            "category": category,
            "fb_type": fb_type,
            "details": extra,
            "credentials": creds,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
                   types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}"))
        caption = f"📤 *NEW WORK SUBMISSION*\n\n👤 User: @{username}\n💼 Type: {category}\n📝 Details: {extra or fb_type}\n🔑 Credentials: {creds}\n🕒 {data['date']}"

        if m.content_type == "photo":
            sent = bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption, reply_markup=markup)
        elif m.content_type == "document":
            sent = bot.send_document(ADMIN_ID, m.document.file_id, caption=caption, reply_markup=markup)
        else:
            sent = bot.send_message(ADMIN_ID, caption, reply_markup=markup)

        # Save message_id to prevent double approve/reject
        processed_messages.add(sent.message_id)

        save_json(WORK_FILE, data)
        bot.send_message(uid, "✅ *YOUR WORK HAS BEEN SUBMITTED*\nAdmin will review shortly.", reply_markup=main_menu())
        reset(uid)

# ================= APPROVAL =================
@bot.callback_query_handler(func=lambda c: c.data.startswith(("approve_","reject_")))
def approve(c):
    if c.from_user.id != ADMIN_ID:
        return
    if c.message.message_id in processed_messages:
        # Prevent double approve/reject
        processed_messages.remove(c.message.message_id)
        action, uid = c.data.split("_")
        uid = int(uid)
        status = "✅ APPROVED" if action=="approve" else "❌ REJECTED"
        bot.send_message(uid, f"🎉 YOUR WORK HAS BEEN {status}" if action=="approve" else f"❌ YOUR WORK WAS NOT ACCEPTED")
        try:
            bot.edit_message_caption(c.message.chat.id, c.message.message_id, caption=c.message.caption+f"\n\n{status}", reply_markup=None)
        except:
            pass
    else:
        bot.answer_callback_query(c.id, "⚠️ This message has already been processed", show_alert=True)

# ================= TODAY PRICE =================
# ... (rest of your Today Price, Admin, Learning, Customer Care, Join Groups, Cancel code stays the same)

# ================= RUN =================
bot.infinity_polling(skip_pending=True)