import telebot
import requests

# --- CONFIGURATION ---
BOT_TOKEN = '8578324022:AAE26QzOw1Z6ITLcyR8buf_JgqflBU0WCok'
CHANNEL_ID = -1003896003068  
CHANNEL_USER = '@osintbyrockey' 
ADMIN_ID = 5768665344        

bot = telebot.TeleBot(BOT_TOKEN)

# Temporary Database
user_credits = {}
referred_users = [] 

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    
    if uid not in user_credits:
        user_credits[uid] = 10 
        
        if len(args) > 1 and args[1].isdigit():
            referrer_id = int(args[1])
            if referrer_id != uid and uid not in referred_users:
                user_credits[referrer_id] = user_credits.get(referrer_id, 0) + 1
                referred_users.append(uid)
                try:
                    bot.send_message(referrer_id, f"🎁 Aapko 1 Referral Credit mila!")
                except: pass

    ref_link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
    msg = (
        f"👋 **Welcome!**\n\n"
        f"💰 Credits: `{user_credits[uid]}`\n"
        f"📢 Join: {CHANNEL_USER}\n"
        f"➖ Per Search: **2 Credits**\n\n"
        f"🔗 **Referral Link:**\n`{ref_link}`"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['add'])
def add_credits(message):
    if message.from_user.id == ADMIN_ID:
        try:
            args = message.text.split()
            target_id, amount = int(args[1]), int(args[2])
            user_credits[target_id] = user_credits.get(target_id, 0) + amount
            bot.reply_to(message, f"✅ User {target_id} ko {amount} credits de diye.")
        except:
            bot.reply_to(message, "❌ Format: `/add ID Amount`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_search(message):
    uid = message.from_user.id
    num = message.text.strip()

    if not is_user_joined(uid):
        bot.reply_to(message, f"⚠️ Join First: {CHANNEL_USER}")
        return

    if num.isdigit() and len(num) >= 10:
        if user_credits.get(uid, 0) < 2:
            bot.reply_to(message, "❌ Low Balance! Refer karke credits kamayein.")
            return

        bot.send_message(message.chat.id, "🔍 **Fetching all details...**")
        api_url = f"https://username-brzb.vercel.app/get-info?phone={num}"
        
        try:
            response = requests.get(api_url, timeout=15)
            data = response.json()
            
            if data.get("status") == True and data.get("results"):
                user_credits[uid] -= 2 
                res = data["results"][0]
                
                # Saari details fetch karna
                details = (
                    f"✅ **Details Found**\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 Name: `{res.get('name', 'N/A')}`\n"
                    f"👨‍👦 Father: `{res.get('father_name', 'N/A')}`\n"
                    f"📱 Primary: `{res.get('mobile', 'N/A')}`\n"
                    f"📲 Alt Mobile: `{res.get('alt_mobile', 'N/A')}`\n"
                    f"📍 Address: `{res.get('address', 'N/A')}`\n"
                    f"🌐 Circle: `{res.get('circle', 'N/A')}`\n"
                    f"🆔 ID Number: `{res.get('id_number', 'N/A')}`\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"💰 Balance: {user_credits[uid]} credits"
                )
                bot.reply_to(message, details, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ No record found.")
        except:
            bot.reply_to(message, "⚠️ API Server error!")
    else:
        bot.reply_to(message, "🚫 Valid number bhejein.")

bot.infinity_polling()
