import logging
import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# In-memory store: user_id -> file_id of saved thumbnail
user_thumbnails: dict[int, str] = {}


def bold_caption(text: str) -> str:
    """Strip any existing markdown formatting and return plain bold text."""
    if not text:
        return text
    # Remove existing markdown: bold (**), italic (*/_), mono (`)
    cleaned = re.sub(r"[*_`]", "", text)
    return f"**{cleaned.strip()}**"


# ── /start ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✅ Bot is online!\n\n"
        "Send me a *photo* first and I'll save it as your thumbnail.\n"
        "Then send a *video file* and I'll attach the thumbnail to it.",
        parse_mode="Markdown",
    )


# ── Photo handler ────────────────────────────────────────────────────────────
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    # Pick the highest-resolution version
    photo = update.message.photo[-1]
    user_thumbnails[user_id] = photo.file_id
    await update.message.reply_text("✅ New Thumbnail Saved.\nNow send the video file.")


# ── Document (video file) handler ────────────────────────────────────────────
async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message = update.message
    doc = message.document

    # Only handle video-like documents
    video_mime_prefixes = ("video/",)
    video_extensions = (".mkv", ".mp4", ".avi", ".mov", ".ts", ".m2ts", ".webm", ".flv")

    is_video_doc = False
    if doc.mime_type and any(doc.mime_type.startswith(p) for p in video_mime_prefixes):
        is_video_doc = True
    elif doc.file_name and any(doc.file_name.lower().endswith(ext) for ext in video_extensions):
        is_video_doc = True

    if not is_video_doc:
        return  # Ignore non-video documents silently

    if user_id not in user_thumbnails:
        await message.reply_text(
            "⚠️ No thumbnail saved yet.\nPlease send a *photo* first.",
            parse_mode="Markdown",
        )
        return

    thumbnail_file_id = user_thumbnails[user_id]

    # Build bold caption (use filename if no caption provided)
    raw_caption = message.caption or doc.file_name or ""
    caption = bold_caption(raw_caption)

    await message.reply_document(
        document=doc.file_id,
        thumbnail=thumbnail_file_id,
        caption=caption,
        parse_mode="Markdown",
    )


# ── Video handler (for .mp4 sent as video, not document) ────────────────────
async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message = update.message
    video = message.video

    if user_id not in user_thumbnails:
        await message.reply_text(
            "⚠️ No thumbnail saved yet.\nPlease send a *photo* first.",
            parse_mode="Markdown",
        )
        return

    thumbnail_file_id = user_thumbnails[user_id]
    raw_caption = message.caption or video.file_name or ""
    caption = bold_caption(raw_caption)

    await message.reply_video(
        video=video.file_id,
        thumbnail=thumbnail_file_id,
        caption=caption,
        parse_mode="Markdown",
        supports_streaming=True,
    )


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    logger.info("Bot started — polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
