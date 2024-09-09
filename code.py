import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle the /start command or any message  
async def start(update: Update, context):
    user = update.effective_user
    
    # If the user hasn't clicked start yet, show the start button
    if not context.user_data.get('active', False):
        keyboard = [[InlineKeyboardButton("Start", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = f"Hello, {user.first_name}! Click 'Start' to begin using the bot."
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        # If the bot is already active, just ask for the image
        await update.message.reply_text("The bot is active. Send me an image to compress.")

# Function to handle button clicks
async def button_click(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        context.user_data['active'] = True  # Set bot to active state for this user
        await query.edit_message_text(text="Bot is now active. You can send me an image for compression.")

# Function to handle image compression
async def compress_image(update: Update, context):
    if context.user_data.get('active', False):  # Check if user clicked 'Start'
        logger.info("Received an image")

        # Get the image from the message
        photo = await update.message.photo[-1].get_file()
        image_data = await photo.download_as_bytearray()

        # Open the image using PIL
        img = Image.open(BytesIO(image_data))

        # Compress the image
        img_io = BytesIO()
        img.save(img_io, format='JPEG', optimize=True, quality=60)  # Adjust quality as needed
        img_io.seek(0)

        # Send the compressed image back to the user
        await update.message.reply_photo(photo=img_io)

        # Send a text message along with the compressed image
        await update.message.reply_text("Here is your compressed image!")
    else:
        # If the user hasn't clicked 'Start' yet
        await update.message.reply_text("Please click 'Start' to begin using the bot.")

# Error handler to log any issues
async def error(update: Update, context):
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    # Your bot's token
    TOKEN = '6868428003:AAG2AEiIBxTH-DqYo7Wb7CBAcHSc_xfPPsE'

    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Handle all messages, including text and non-image messages
    application.add_handler(MessageHandler(filters.ALL & (~filters.PHOTO), start))

    # Handle images separately
    application.add_handler(MessageHandler(filters.PHOTO, compress_image))

    # Log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
