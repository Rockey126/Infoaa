import telebot
import requests

# Replace with your actual Bot Token from BotFather
BOT_TOKEN = '8578324022:AAE26QzOw1Z6ITLcyR8buf_JgqflBU0WCok'
bot = telebot.TeleBot(BOT_TOKEN)

# Command: /start or sending 'start'
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text.lower() == 'start')
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Please send me a 10-digit phone number to get the details.")

# Handling phone number inputs
@bot.message_handler(func=lambda message: True)
def get_info(message):
    user_input = message.text.strip()
    
    # Basic check if input is a number
    if user_input.isdigit() and len(user_input) >= 10:
        bot.send_message(message.chat.id, "🔍 Fetching details... Please wait.")
        
        # API URL
        api_url = f"https://username-brzb.vercel.app/get-info?phone={user_input}"
        
        try:
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Format the response (modify keys based on your actual API output)
                # Assuming API returns keys like 'name', 'location', etc.
                details = f"✅ **Details Found:**\n\n"
                for key, value in data.items():
                    details += f"🔹 {key.capitalize()}: {value}\n"
                
                bot.reply_to(message, details, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Error: Could not find details for this number.")
                
        except Exception as e:
            bot.reply_to(message, "⚠️ API is currently down or there's a connection issue.")
    else:
        bot.reply_to(message, "🚫 Please enter a valid 10-digit phone number.")

print("Bot is running...")
bot.infinity_polling()