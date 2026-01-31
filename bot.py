import telebot
import requests

# Aapka fixed token yahan hai
BOT_TOKEN = '8578324022:AAE26QzOw1Z6ITLcyR8buf_JgqflBU0WCok'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot Active Ho Gaya Hai!\n\nDetails nikalne ke liye 10-digit phone number bhejein.")

@bot.message_handler(func=lambda message: True)
def get_info(message):
    user_input = message.text.strip()
    
    # Check if input is a valid number
    if user_input.isdigit() and len(user_input) >= 10:
        bot.send_message(message.chat.id, "🔍 Database mein search kar raha hoon... Please wait.")
        
        # Sahi API URL formatting
        api_url = f"https://username-brzb.vercel.app/get-info?phone={user_input}"
        
        try:
            response = requests.get(api_url, timeout=15)
            data = response.json()
            
            # Aapki API results list bhejti hai, isliye indexing [0] use ki hai
            if data.get("status") == True and data.get("results"):
                res = data["results"][0]
                
                details = (
                    f"✅ **Details Found**\n\n"
                    f"👤 Name: {res.get('name', 'N/A')}\n"
                    f"👨‍👦 Father: {res.get('father_name', 'N/A')}\n"
                    f"📍 Address: {res.get('address', 'N/A')}\n"
                    f"📱 Mobile: {res.get('mobile', 'N/A')}\n"
                    f"🌐 Circle: {res.get('circle', 'N/A')}"
                )
                bot.reply_to(message, details, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Is number ka koi record nahi mila.")
                
        except Exception as e:
            bot.reply_to(message, "⚠️ API Error! Shayad server down hai ya connection issue hai.")
    else:
        bot.reply_to(message, "🚫 Galti! Kripya sahi 10-digit mobile number bhejein.")

print("Bot is running...")
bot.infinity_polling()
