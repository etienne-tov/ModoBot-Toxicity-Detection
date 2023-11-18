import logging
from typing import Final
from telegram import Update
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import random


TELEGRAM_TOKEN: Final = "***********************************"
BOT_USERNAME = '@ToxiGuard_bot'

API_URL = 'http://localhost:8000/predict_toxicity'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update:Update, context: ContextTypes)->None:
    message_text: str = update.message.text

    response = requests.post(API_URL, json={"text": message_text})
    
    toxic_labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hat"]

    if response.status_code == 200:
        predictions = response.json()["predictions"]
        
        if any(predictions[label] for label in toxic_labels):
             user_id = update.message.from_user.id
             #context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
             warnings = context.user_data.get(user_id, 0)

             warnings += 1

             context.user_data[user_id] = warnings
             
             emojis_toxic = ["😡", "🤬", "😤"]
             emojis_severe_toxic = ["👿", "💣", "🔥"]
             emojis_obscene = ["😳", "🙈", "🤢"]
             emojis_threat = ["🚫", "⚠️", "🔪"]
             emojis_insult = ["😒", "🙄", "😠"]
             emojis_identity_hat = ["🎭", "👤", "🕵️‍♂️"]
             
             emojis_mapping = {
                "toxic": emojis_toxic,
                "severe_toxic": emojis_severe_toxic,
                "obscene": emojis_obscene,
                "threat": emojis_threat,
                "insult": emojis_insult,
                "identity_hat": emojis_identity_hat,
            }
             
             messages = {
                "toxic": "Your message is toxic. Be nice!",
                "severe_toxic": "Your message is severely toxic. Calm down!",
                "obscene": "Your message is obscene. Keep it clean!",
                "threat": "Your message contains threats. Not cool!",
                "insult": "Your message is insulting. Spread love!",
                "identity_hat": "Your message may contain identity-hat. Be respectful!",
            }
             
             for label in toxic_labels:
                if predictions[label]:
                    emoji = random.choice(emojis_mapping[label])
                    text = f"{emoji} {messages.get(label, 'Your message is toxic. Be nice!')} This is your warning #{warnings}."
                    
                    print('Bot:', text)
                    await update.message.reply_text(text)
                    break
             

             if warnings >= 3:
                await context.bot.ban_chat_member(update.effective_chat.id, user_id)
                
                del context.user_data[user_id]
                


def main():
    print("Start ......")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print('Pooling..........')
    app.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()
