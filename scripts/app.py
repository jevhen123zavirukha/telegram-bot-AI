import os
import random
import time
import threading
import schedule
from dotenv import load_dotenv
from openai import OpenAI
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- ENVIRONMENT ----------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------- SUBSCRIBERS ----------------
def load_subscribers():
    if os.path.exists("subscribers.txt"):
        with open("subscribers.txt", "r") as f:
            return set(int(line.strip()) for line in f)
    return set()


def save_subscribers():
    with open("subscribers.txt", "w") as f:
        for s in subscribers:
            f.write(f"{s}\n")


subscribers = load_subscribers()


# ---------------- MAIN KEYBOARD ----------------
def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("Fun Fact or Quiz 🎉"),
        telebot.types.KeyboardButton("Information ℹ️"),
        telebot.types.KeyboardButton("Leave feedback❓"),
        telebot.types.KeyboardButton("Subscribe for daily fact 📅")
    )
    return markup


# ---------------- QUIZ/FACT KEYBOARD ----------------
def quiz_fact_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("Fun Fact 🎉🤓"),
        telebot.types.KeyboardButton("Fun Quiz 🎉❓"),
        telebot.types.KeyboardButton("Return to main keyboard ℹ️"),
    )
    return markup


# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Hello! I'm your *Fun AI Bot*.\n\n"
        "You can get fun facts or take quizzes for fun learning!",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ---------------- MAIN HANDLER ----------------
@bot.message_handler(func=lambda msg: True)
def reply(message):
    text = message.text

    if text.startswith("Information"):
        bot.send_message(
            message.chat.id,
            "ℹ️ This bot sends you fun quizzes and facts!\nYou can also subscribe for daily ones."
        )

    elif text.startswith("Leave feedback"):
        bot.send_message(
            message.chat.id,
            "💬 We’d love your feedback!\nVisit: https://github.com/jevhen123zavirukha/telegram-bot-AI.git"
        )

    elif text.startswith("Fun Fact or Quiz"):
        bot.send_message(
            message.chat.id,
            "Now choose if you want a *fun fact* or *quiz*! 🎉",
            parse_mode="Markdown",
            reply_markup=quiz_fact_keyboard()
        )

    elif text.startswith("Fun Fact"):
        fun_fact(message.chat.id)

    elif text.startswith("Fun Quiz"):
        fun_quiz(message.chat.id)

    elif text.startswith("Subscribe for daily fact"):
        if message.chat.id not in subscribers:
            subscribers.add(message.chat.id)
            save_subscribers()
            bot.send_message(message.chat.id, "✅ You’re subscribed! You’ll get a fun fact every day 📅")
        else:
            bot.send_message(message.chat.id, "🔔 You’re already subscribed!")

    elif text.startswith("Return"):
        bot.send_message(message.chat.id, "↩️ Back to main menu.", reply_markup=main_keyboard())


# ---------------- FUN FACT FUNCTION ----------------
def fun_fact(chat_id):
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
        print("Error in fun_fact:", e)


# ---------------- FUN QUIZ FUNCTION ----------------
def fun_quiz(chat_id):
    try:
        topics = ["science", "history", "geography", "animals", "space"]
        topic = random.choice(topics)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are a quiz generator bot. "
                    "Create a short multiple-choice question (quiz) with 4 options (A, B, C, D). "
                    "Mark the correct one with a star (*) but don't say which one it is explicitly. "
                    "Make it educational and fun, 1–2 sentences max."
                )},
                {"role": "user", "content": f"Create a quiz about {topic}."}
            ]
        )

        quiz_text = response.choices[0].message.content

        # Extract question and options
        lines = quiz_text.split("\n")
        question = lines[0]
        options = [line for line in lines[1:] if line.strip()]

        # Build buttons
        markup = InlineKeyboardMarkup()
        for opt in options:
            clean_text = opt.replace("*", "").strip()
            callback = "correct" if "*" in opt else "wrong"
            markup.add(InlineKeyboardButton(clean_text, callback_data=callback))

        bot.send_message(chat_id, f"🧩 *Quiz time!*\n\n{question}", parse_mode="Markdown", reply_markup=markup)

    except Exception as e:
        bot.send_message(chat_id, "⚠️ Couldn't load quiz, try again!")
        print("Error in fun_quiz:", e)


# ---------------- INLINE CALLBACKS ----------------
@bot.callback_query_handler(func=lambda call: call.data in ["new_fact", "correct", "wrong"])
def handle_callback(call):
    if call.data == "new_fact":
        fun_fact(call.message.chat.id)
    elif call.data == "correct":
        bot.answer_callback_query(call.id, "✅ Correct! You're awesome!")
    elif call.data == "wrong":
        bot.answer_callback_query(call.id, "❌ Oops! Try again next time.")


# ---------------- DAILY FACT SENDER ----------------
def send_daily_facts():
    print("Sending daily facts...")
    for chat_id in subscribers:
        fun_fact(chat_id)


# ---------------- SCHEDULER THREAD ----------------
def schedule_thread():
    schedule.every().day.at("19:06").do(send_daily_facts)
    while True:
        schedule.run_pending()
        time.sleep(60)


# ---------------- START EVERYTHING ----------------
if __name__ == '__main__':
    print("🤖 Bot is running...")
    threading.Thread(target=schedule_thread, daemon=True).start()
    bot.polling(none_stop=True)
