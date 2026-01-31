import telebot
import requests
import time

# --- CONFIGURATION ---
BOT_TOKEN = '8578324022:AAE26QzOw1Z6ITLcyR8buf_JgqflBU0WCok'
ADMIN_ID = 5768665344
CHANNEL_ID = -1003896003068
CHANNEL_USER = '@osintbyrockey'
UPI_ID = "paytm.s20gdag@pty"

bot = telebot.TeleBot(BOT_TOKEN)

# Temporary Database
user_credits = {}
referred_users = [] 
used_txns = [] 

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# --- KEYBOARDS ---
def main_keyboard(uid):
    markup = telebot.types.InlineKeyboardMarkup()
    pay_url = f"upi://pay?pa={UPI_ID}&pn=RockeyBot&am=10&cu=INR"
    btn_pay = telebot.types.InlineKeyboardButton("💰 Add Funds (UPI)", url=pay_url)
    markup.add(btn_pay)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    
    # New User Setup (1 Credit Only)
    if uid not in user_credits:
        user_credits[uid] = 1 
        if len(args) > 1 and args[1].isdigit():
            referrer_id = int(args[1])
            if referrer_id != uid and uid not in referred_users:
                user_credits[referrer_id] = user_credits.get(referrer_id, 0) + 1
                referred_users.append(uid)
                try: bot.send_message(referrer_id, "🎁 Referral Credit added!")
                except: pass

    ref_link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
    msg = (
        f"👋 **Rockey Info Bot**\n\n"
        f"💰 Balance: `{user_credits[uid]}`\n"
        f"➖ Per Search: **2 Credits**\n\n"
        f"📝 Number bhejein details ke liye.\n"
        f"🔗 **Refer Link:** `{ref_link}`"
    )
    bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(uid))

# --- COMBINED ADMIN MANUAL CREDIT COMMAND ---
@bot.message_handler(commands=['add'])
def add_credits_manual(message):
    if message.from_user.id == ADMIN_ID:
        try:
            # Format: /add [User_ID] [Amount]
            args = message.text.split()
            target_id, amount = int(args[1]), int(args[2])
            user_credits[target_id] = user_credits.get(target_id, 0) + amount
            bot.reply_to(message, f"✅ Admin: Added {amount} credits to {target_id}.")
            bot.send_message(target_id, f"🎉 Admin ne aapke account mein **{amount} credits** add kiye hain!")
        except:
            bot.reply_to(message, "❌ Use: `/add UserID Amount`", parse_mode="Markdown")

# --- TRANSACTION ID APPROVAL SYSTEM ---
@bot.message_handler(func=lambda message: len(message.text) > 8 and not message.text.isdigit())
def verify_payment_id(message):
    txn_id = message.text.strip()
    uid = message.from_user.id
    if txn_id in used_txns:
        bot.reply_to(message, "❌ TXN ID used already.")
        return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{uid}_{txn_id}"))
    bot.send_message(ADMIN_ID, f"🔔 **New Payment!**\nUser: `{uid}`\nTXN: `{txn_id}`", reply_markup=markup)
    bot.reply_to(message, "⏳ Admin verification ke liye bhej diya gaya hai.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def admin_approve(call):
    data = call.data.split("_")
    target_id, txn_id = int(data[1]), data[2]
    user_credits[target_id] = user_credits.get(target_id, 0) + 10 
    used_txns.append(txn_id)
    bot.send_message(target_id, "🎉 Payment Approved! 10 Credits added.")
    bot.edit_message_text(f"✅ Approved {target_id}", call.message.chat.id, call.message.message_id)

# --- SEARCH LOGIC ---
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) >= 10)
def handle_search(message):
    uid = message.from_user.id
    num = message.text.strip()
    if not is_user_joined(uid):
        bot.reply_to(message, f"⚠️ Join {CHANNEL_USER}")
        return
    if user_credits.get(uid, 0) < 2:
        bot.reply_to(message, "❌ Credits Low!", reply_markup=main_keyboard(uid))
        return
    bot.send_message(message.chat.id, "🔍 Searching...")
    api_url = f"https://username-brzb.vercel.app/get-info?phone={num}"
    try:
        response = requests.get(api_url, timeout=15).json()
        if response.get("status") == True:
            user_credits[uid] -= 2
            res = response["results"][0]
            bot.reply_to(message, f"👤 Name: `{res.get('name')}`\n📍 Address: `{res.get('address')}`\n💰 Balance: {user_credits[uid]}", parse_mode="Markdown")
        else: bot.reply_to(message, "❌ No data.")
    except: bot.reply_to(message, "⚠️ Error!")

bot.infinity_polling()
