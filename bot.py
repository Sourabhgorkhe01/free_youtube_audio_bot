import os
import logging
import threading
import re
from telegram import Update
from telegram.error import Conflict
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, DOWNLOAD_DIR
from downloader import download_audio, download_video

# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename=os.path.join(log_dir, 'bot.log'))
logger = logging.getLogger(__name__)

# Dictionary to track active downloads cancellation flags per user id
active_downloads = {}

# Regex pattern to detect YouTube URLs
YOUTUBE_URL_PATTERN = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description_text = (
        "👋 *Welcome to YouTube Downloader Bot!*\n\n"
        "With this bot, you can download:\n"
        "🎧 *Audio* — /audio <YouTube URL>\n"
        "🎥 *Video* — /video <YouTube URL>\n\n"
        "Example:\n"
        "/audio https://youtube.com/watch?v=abcd1234\n"
        "/video https://youtube.com/watch?v=abcd1234\n\n"
        "ℹ️ *Supported formats:*\n"
        "- MP3 (audio)\n"
        "- MP4 (video)\n\n"
        "📬 [Contact Developer](https://t.me/Thewarrior2003)\n"
        "*your frind* "
    )
    await update.message.reply_text(description_text, parse_mode='Markdown')


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text.lower() in ["hi", "hello"]:
        await update.message.reply_text("👋 Hi! Send a YouTube link to get started.")
        return

    if YOUTUBE_URL_PATTERN.search(text):
        if "video" in text.lower():
            await process_video(update, context, text, user_id)
        else:
            await process_audio(update, context, text, user_id)
    else:
        await update.message.reply_text("❌ Please send a valid YouTube link.")


async def process_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, user_id: int):
    await update.message.reply_text("⏳ Downloading audio...")
    cancel_flag = threading.Event()
    active_downloads[user_id] = cancel_flag
    try:
        url = YOUTUBE_URL_PATTERN.search(text).group(0)
        audio_file, title, elapsed_time = download_audio(url, cancel_flag)

        if not os.path.exists(audio_file):
            await update.message.reply_text(f"❌ Audio file not found: {audio_file}")
        else:
            with open(audio_file, 'rb') as audio_f:
                await update.message.reply_audio(audio=audio_f, caption=f"🎧 {title}")
            os.remove(audio_file)
            await update.message.reply_text(f"⏱️ Done in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Audio download error: {e}")
        await update.message.reply_text("❌ Failed to download audio.")
    finally:
        active_downloads.pop(user_id, None)


async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, user_id: int):
    await update.message.reply_text("⏳ Downloading video...")
    cancel_flag = threading.Event()
    active_downloads[user_id] = cancel_flag
    try:
        url = YOUTUBE_URL_PATTERN.search(text).group(0)
        video_file, title, elapsed_time = download_video(url, cancel_flag)

        if not os.path.exists(video_file):
            await update.message.reply_text(f"❌ Video file not found: {video_file}")
        else:
            with open(video_file, 'rb') as video_f:
                await update.message.reply_video(video=video_f, caption=f"🎥 {title}")
            os.remove(video_file)
            await update.message.reply_text(f"⏱️ Done in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Video download error: {e}")
        await update.message.reply_text("❌ Failed to download video.")
    finally:
        active_downloads.pop(user_id, None)


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /audio <YouTube URL>")
        return
    await process_audio(update, context, context.args[0], update.effective_user.id)


async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /video <YouTube URL>")
        return
    await process_video(update, context, context.args[0], update.effective_user.id)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cancel_flag = active_downloads.get(user_id)
    if cancel_flag:
        cancel_flag.set()
        await update.message.reply_text("⏹️ Stopped your download.")
    else:
        await update.message.reply_text("ℹ️ No active download to stop.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📌 Commands:\n"
        "/start - Show welcome message\n"
        "/audio <link> - Download audio\n"
        "/video <link> - Download video\n"
        "/stop - Cancel current download"
    )
    await update.message.reply_text(help_text)


if __name__ == '__main__':
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Bot is running...")
    try:
        app.run_polling()
    except Conflict as e:
        print(f"❌ Conflict error: {e}")
        print("Please make sure only one bot instance is running")
        logger.error(f"Conflict error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception(f"Unexpected error: {e}")