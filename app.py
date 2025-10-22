import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)


# Main keyboard
def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("Fun quiz 🎉"),
        telebot.types.KeyboardButton("Information ℹ️"),
        telebot.types.KeyboardButton("Leave feedback❓"),
    )
    return markup


# Start message
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Hello! I'm your Fun AI Bot.\nChoose an option below:",
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda msg: True)
def reply(message):
    if message.text.startswith("Information"):
        bot.send_message(message.chat.id, "ℹ️ This bot sends you every day fun quiz and fact,"
                                          " you can also get some fun quiz or fact anywhen.")

    elif message.text.startswith("Leave feedback"):
        bot.send_message(message.chat.id, "Have you already completed a course with us? If yes, we would be glad to"
                                          " receive your feedback on our website EXAMPLE-WEB! "
                                          "https://github.com/jevhen123zavirukha/telegram-bot-AI.git")
    elif message.text.startswith("Fun quiz"):
        fun_quiz(message.chat.id)


def fun_quiz(message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a Fun AI Bot."
                "You can tell user some fun fact about biology, chemistry, geography, Earth, animals and other category"
                "Max length of fact is 6 sentences."
            )},
            {"role": "user", "content": "User wants a fun fact"}
        ]
    )

    bot.send_message(message.chat.id, response.choices[0].message.content)


if __name__ == '__main__':
    print("bot is running...")
    bot.polling()
