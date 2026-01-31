import os
import telebot
import requests

# Render Environment Variables se token lein
BOT_TOKEN ='8578324022:AAE26QzOw1Z6ITLcyR8buf_JgqflBU0WCok' os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Welcome! Phone number bhejein details ke liye.")

@bot.message_handler(func=lambda message: True)
def get_info(message):
    number = message.text.strip()
    
    if number.isdigit() and len(number) >= 10:
        bot.send_message(message.chat.id, "🔍 Searching in Database...")
        
        # Sahi API URL string formatting ke saath
        api_url = f"https://username-brzb.vercel.app/get-info?phone={number}"
        
        try:
            response = requests.get(api_url, timeout=10)
            data = response.json()
            
            # Aapki API ke "results" list se data nikalna
            if data.get("status") == True and data.get("results"):
                res = data["results"][0] # Pehla result uthaya
                
                details = (
                    f"✅ Details Found\n\n"
                    f"👤 Name: {res.get('name', 'N/A')}\n"
                    f"👨‍👦 Father: {res.get('father_name', 'N/A')}\n"
                    f"📍 Address: {res.get('address', 'N/A')}\n"
                    f"📱 Mobile: {res.get('mobile', 'N/A')}\n"
                    f"🌐 Circle: {res.get('circle', 'N/A')}"
                )
                bot.reply_to(message, details, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ No records found for this number.")
                
        except Exception as e:
            bot.reply_to(message, "⚠️ Server Error: API response read nahi kar paa raha.")
    else:
        bot.reply_to(message, "🚫 Invalid number! Please enter 10 digits.")

bot.infinity_polling()
