import os
import random
import time
import threading
import schedule
from dotenv import load_dotenv
from openai import OpenAI
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Store subscribers for daily facts
subscribers = set()


# ---------------- MAIN KEYBOARD ----------------
def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("Fun quiz 🎉"),
        telebot.types.KeyboardButton("Information ℹ️"),
        telebot.types.KeyboardButton("Leave feedback❓"),
        telebot.types.KeyboardButton("Subscribe for daily fact 📅")
    )
    return markup


# ---------------- START MESSAGE ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Hello! I'm your *Fun AI Bot*.\n\n"
        "You can get fun facts, info, or even subscribe for daily ones!",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ---------------- MAIN HANDLER ----------------
@bot.message_handler(func=lambda msg: True)
def reply(message):
    if message.text.startswith("Information"):
        bot.send_message(
            message.chat.id,
            "ℹ️ This bot sends you daily fun quizzes and facts!\n"
            "You can also request one anytime."
        )

    elif message.text.startswith("Leave feedback"):
        bot.send_message(
            message.chat.id,
            "We’d love your feedback! 💬\n"
            "Visit: https://github.com/jevhen123zavirukha/telegram-bot-AI.git"
        )

    elif message.text.startswith("Fun quiz"):
        fun_quiz(message.chat.id)

    elif message.text.startswith("Subscribe for daily fact"):
        if message.chat.id not in subscribers:
            subscribers.add(message.chat.id)
            bot.send_message(message.chat.id, "✅ You’re subscribed! You’ll get a fun fact every day 📅")
        else:
            bot.send_message(message.chat.id, "🔔 You’re already subscribed!")


# ---------------- FUN QUIZ FUNCTION ----------------
def fun_quiz(chat_id):
    try:
        topics = ["biology", "chemistry", "geography", "space", "animals", "Earth", "history", "technology"]
        topic = random.choice(topics)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are a Fun AI Bot. "
                    "Give short, interesting, and surprising fun facts about science, nature, or the world. "
                    "Keep it under 6 sentences."
                )},
                {"role": "user", "content": f"Give me one fun fact about {topic}."}
            ]
        )

        text = f"🌍 *Category:* {topic.capitalize()}\n\n{response.choices[0].message.content}"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔁 Another fact", callback_data="new_fact"))

        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

    except Exception as e:
        bot.send_message(chat_id, "⚠️ Oops! Something went wrong. Try again later.")
        print("Error in fun_quiz:", e)


# ---------------- INLINE BUTTON HANDLER ----------------
@bot.callback_query_handler(func=lambda call: call.data == "new_fact")
def new_fact(call):
    fun_quiz(call.message.chat.id)


# ---------------- DAILY FACT FUNCTION ----------------
def send_daily_facts():
    print("Sending daily facts...")
    for chat_id in subscribers:
        fun_quiz(chat_id)


# ---------------- SCHEDULER ----------------
def schedule_thread():
    schedule.every().day.at("09:00").do(send_daily_facts)  # send at 9:00 AM every day
    while True:
        schedule.run_pending()
        time.sleep(60)


# ---------------- START EVERYTHING ----------------
if __name__ == '__main__':
    print("🤖 Bot is running...")
    # Run scheduler in background
    threading.Thread(target=schedule_thread, daemon=True).start()
    bot.polling(none_stop=True)
