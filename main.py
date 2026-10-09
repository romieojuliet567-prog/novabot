import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# Enable logging to diagnose issues
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your custom message text
JOIN_MESSAGE = (
    "Welcome! To verify you are human, please click the button below.\n\n"
    "After verification, your join request will be approved automatically."
)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles new join requests by sending a private message with verification."""
    request = update.chat_join_request
    
    # Create an inline keyboard with a verification button
    keyboard = [
        [InlineKeyboardButton("✅ I am human - Verify me", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Send the message to the user's private chat
        await context.bot.send_message(
            chat_id=request.user_chat_id, 
            text=JOIN_MESSAGE,
            reply_markup=reply_markup
        )
        logger.info(f"Verification message sent to {request.from_user.id}")
    except Exception as e:
        # If the user has not started the bot, we cannot send them a message
        logger.error(f"Failed to message {request.from_user.id}: {e}")
        # Auto-decline if we cannot verify them
        await context.bot.decline_chat_join_request(
            chat_id=request.chat.id,
            user_id=request.from_user.id
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standard /start command for ad moderation."""
    await update.message.reply_text(
        "Hello! This bot helps manage channel access. Use /help for more info."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standard /help command for ad moderation."""
    await update.message.reply_text(
        "This bot automatically processes join requests for a private channel."
    )

async def verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder for verification logic - handles the button click."""
    query = update.callback_query
    await query.answer("Verification logic not implemented yet.")
    # In a real bot, you would implement captcha logic here

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    """Start the bot using webhooks for Railway."""
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
    
    PORT = int(os.environ.get("PORT", 8080))
    
    # Build the application
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Error handler
    application.add_error_handler(error_handler)

    # Railway injects RAILWAY_PUBLIC_DOMAIN
    webhook_url = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}/{TOKEN}"
    
    logger.info(f"Starting webhook on port {PORT}")
    
    # Run the webhook server
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
