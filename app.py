import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)


@bot.message_handler(func=lambda msg: True)
def chat_with_ai(message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a strict Calculator AI. "
                "Whenever the user sends a math expression (like '4 + 4' or '10 * 3'), "
                "you MUST calculate it and respond ONLY with the solved expression in this format: '4 + 4 = 8'. "
                "Do NOT write explanations, confirmations, or any text other than the answer. "
                "If the input is not a math expression, reply exactly: 'Please send a valid math expression.'"
            )},
            {"role": "user", "content": message.text}
        ]
    )

    bot.send_message(message.chat.id, response.choices[0].message.content)



bot.polling()
