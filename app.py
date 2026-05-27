import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
from email_utils import send_email

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID "))

app = FastAPI()

telegram_app = Application.builder().token(BOT_TOKEN).build()
BOT_ACTIVE = True

def is_authorized(update: Update):
    return update.effective_user.id == ALLOWED_USER_ID

# START COMMAND
async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE
    BOT_ACTIVE = True
    await update.message.reply_text(
        "✅ Bot activated."
        "Send message in this format:\n\n"
        "AI/ML\n"
        "email1@gmail.com\n"
        "email2@gmail.com"
    )

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE
    BOT_ACTIVE = False
    await update.message.reply_text(
        "🛑 Bot stopped.\nEmails will not be sent."
    )

# HANDLE MESSAGE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not is_authorized(update):
        await update.message.reply_text(
            "❌ Unauthorized access."
        )
        return
    
    global BOT_ACTIVE
    if not BOT_ACTIVE:
        await update.message.reply_text(
            "⚠️ Bot is currently stopped."
        )
        return
    
    text = update.message.text
    lines = text.strip().split("\n")
    role = lines[0].strip().lower()
    emails = [email.strip() for email in lines[1:]]
    await update.message.reply_text("Sending emails... ⏳")

    result = send_email(role, emails)
    if result == "SUCCESS":
        await update.message.reply_text("✅ Emails sent successfully!")
    else:
        await update.message.reply_text(f"❌ {result}")


telegram_app.add_handler(CommandHandler("stop", stop_bot))
telegram_app.add_handler(CommandHandler("start", start_bot))
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)


# WEBHOOK ENDPOINT
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


# STARTUP EVENT
@app.on_event("startup")
async def startup():

    webhook_url = os.getenv("WEBHOOK_URL")

    await telegram_app.initialize()

    await telegram_app.bot.set_webhook(
        url=f"{webhook_url}/webhook"
    )

    print("Webhook set successfully")