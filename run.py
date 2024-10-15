import logging
from logging.handlers import RotatingFileHandler
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from sdnotify import SystemdNotifier
import argparse
import re 

# Start command to initialize the bot
async def start(update: Update, context):
    global user_id
    user_id = update.message.chat_id
    await update.message.reply_text(
        "Hi! Thank you for your message, we'll get back ASAP. Can you please send you phone number if it is urgent."
    )

# Forward messages from the user to the group
async def forward_to_group(update: Update, context):
    global group_id
    logger.debug(f'{update.to_json()}')
    if group_id:
        try: 
            message_text = update.message.text
            if await is_spam(message_text) or update.message.from_user.id in blocked_users:
                await update.message.reply_text("You have been blocked.")
                return None
        except Exception as e:
            print(f'Exception: {Exception(e)}')

        logger.debug(f'{update.message.from_user.to_json()}')
        
        await context.bot.send_message(
            chat_id=group_id,
            text=f"User: {update.message.from_user.first_name, update.message.from_user.id}\nMessage: {message_text}"
        )
        await update.message.reply_text(args.reply_msg)

async def is_spam(message: str)-> bool:
    # Normalize the message (convert to lowercase)
    message = message.lower()

    url_pattern = r"(https?://\S+)"
    exclamation_pattern = r"(!{3,})"
    
    # Check for spam keywords
    for keyword in spam_keywords:
        if keyword in message:
            return True
    
    # Check for suspicious patterns
    if re.search(url_pattern, message):
        return True
    if re.search(exclamation_pattern, message):
        return True

    return False


# Forward group messages back to the user
async def forward_to_user(update: Update, context):
    logger.debug(f'{update}/n{context}')
    logger.debug(f'{update.message.from_user.to_json()}')

    message_text = update.message.text
    try:         
        user_id=int(message_text.split('%')[1].strip()) 
        print(message_text)  
        if message_text.find('block_user')>-1: # block_user%user_id%message
            with open('blocked_users.txt', 'a') as f:
                f.write(f'{user_id}\n')
                blocked_users.append(user_id)
                return None 
            
        message_text=message_text[message_text.rfind('%')+1:] # %user_id%message
        await context.bot.send_message(chat_id=user_id, text=message_text)
    except Exception as e:
        print(f'Exception: {Exception(e)}')
        if message_text.count('%')>=2:
            context.bot.send_message(
                chat_id=group_id,
                text=f"Exception: {Exception(e)}"
            )

        pass 

if __name__ == "__main__":
    args=argparse.ArgumentParser()
    args.add_argument('--TOKEN', type=str, required=True, help='Telegram Bot Token; Open BotFather and create a new bot to get the token')
    args.add_argument('--GROUP_ID', type=int, required=True, help='Group ID; to obtain group_id, run the bot, open the group chat and add @your_bot, add admin permissions,message him and check log files for the group ID; Number should be negative. Eg: -100123456789')
    args.add_argument('--reply_msg', type=str, default='Hi! Thank you for your message, we will get back to you ASAP. Can you please send your phone number if it is urgent.', help='Reply message to the user')
    args=args.parse_args()

    group_id = args.GROUP_ID   
    TOKEN = args.TOKEN 

    notifier = SystemdNotifier()
    notifier.notify("READY=1")

    log_file = "./bot.log"

    with open('spam_keywords.txt', 'r') as f:
        spam_keywords = [spam_keyword.strip() for spam_keyword in f.readlines()]

    with open('./blocked_users.txt', 'r') as f:
        blocked_users=[int(blocked_userid.strip()) for blocked_userid in  f.readlines()]

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=10),  # 10MB max, 5 backups
        ]
    )
    logger = logging.getLogger(__name__)

    # Create the Application and pass the bot token
    application = Application.builder().token(TOKEN).build()

    # Command handler to start the bot
    application.add_handler(CommandHandler("start", start))

    # Message handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.Chat(group_id), forward_to_group)
    )

    # Forward group's messages to the user
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Chat(group_id), forward_to_user)
    )
    application.run_polling()
