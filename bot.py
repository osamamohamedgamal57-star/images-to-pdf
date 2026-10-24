"""Telegram bot: send it photos, type /pdf, choose a name, and get them back as one PDF file.
Includes user statistics and an admin panel (type /admin).
Runs on your own computer: double-click run_bot.bat to start it."""
import logging
import os
import shutil
import tempfile

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    TypeHandler,
    filters,
)

import admin
import db
from pdf_utils import DEFAULT_NAME, clean_pdf_name, images_to_pdf

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def get_folder(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Each user gets their own temporary folder for their images."""
    if "folder" not in context.user_data:
        context.user_data["folder"] = tempfile.mkdtemp(prefix="pdfbot_")
    return context.user_data["folder"]


def cleanup(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete the user's temporary files and forget their images."""
    folder = context.user_data.pop("folder", None)
    if folder:
        shutil.rmtree(folder, ignore_errors=True)
    context.user_data.pop("images", None)
    context.user_data.pop("awaiting_pdf_name", None)


async def track_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs before every other handler: saves the user and marks them active today."""
    user = update.effective_user
    if user and not user.is_bot:
        db.track_user(user.id, user.username, user.first_name)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(db.get_setting("welcome_text"))


async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    images = context.user_data.setdefault("images", [])
    max_images = int(db.get_setting("max_images"))

    if len(images) >= max_images:
        await message.reply_text(f"The limit is {max_images} images. Type /pdf to get your file.")
        return

    if message.photo:  # a normal photo: the last item is the biggest size
        tg_file = await message.photo[-1].get_file()
        extension = ".jpg"
    else:  # an image sent "as a file"
        document = message.document
        tg_file = await document.get_file()
        extension = os.path.splitext(document.file_name or "")[1] or ".jpg"

    path = os.path.join(get_folder(context), f"{len(images) + 1:03d}{extension}")
    await tg_file.download_to_drive(path)
    images.append(path)
    await message.reply_text(f"Image {len(images)} saved. Send more, or type /pdf.")


async def ask_pdf_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/pdf: do not create the file yet, first ask the user what it should be called."""
    if not context.user_data.get("images"):
        await update.message.reply_text("You have not sent any images yet. Send me some photos first.")
        return

    context.user_data.pop("awaiting", None)  # in case an admin was in the middle of an edit
    context.user_data["awaiting_pdf_name"] = True
    await update.message.reply_text(
        "What should the PDF be called?\n\n"
        "Send me the name now (no need to type .pdf).\n"
        f"Or type /skip to use the default name ({DEFAULT_NAME}.pdf), or /cancel to go back."
    )


async def skip_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/skip: create the PDF with the default name."""
    if not context.user_data.get("awaiting_pdf_name"):
        await update.message.reply_text("Nothing to skip. Send me photos, then type /pdf.")
        return
    await create_pdf(update, context, clean_pdf_name(""))


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The only handler for plain text. Telegram runs just one handler per message,
    so this decides who the text belongs to: the PDF name, or an admin edit."""
    if context.user_data.get("awaiting_pdf_name"):
        await create_pdf(update, context, clean_pdf_name(update.message.text))
    else:
        await admin.admin_text_input(update, context)


async def create_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE, pdf_name: str) -> None:
    images = context.user_data.get("images", [])
    context.user_data.pop("awaiting_pdf_name", None)
    if not images:
        await update.message.reply_text("You have not sent any images yet. Send me some photos first.")
        return

    await update.message.reply_text(f"Creating {pdf_name} ...")
    # The file on disk has a fixed safe name; the name the user chose is used when sending it
    output_path = os.path.join(get_folder(context), "output.pdf")
    try:
        images_to_pdf(images, output_path)
        with open(output_path, "rb") as pdf_file:
            await update.message.reply_document(document=pdf_file, filename=pdf_name)
        db.record_pdf(update.effective_user.id, len(images))
    except Exception:
        logger.exception("Could not create the PDF")
        await update.message.reply_text("Sorry, something went wrong. One of the files may not be a valid image.")
    finally:
        cleanup(context)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cleanup(context)
    await update.message.reply_text("Done. Your images were deleted. Send new photos to start again.")


def main() -> None:
    load_dotenv()  # reads BOT_TOKEN and ADMIN_ID from the .env file
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token.startswith("put-your"):
        raise SystemExit("BOT_TOKEN is missing. Open the .env file and paste your token (see README).")

    db.init_db()
    owner = admin.owner_id()
    if owner:
        db.add_admin(owner)
    else:
        logger.warning("ADMIN_ID was not found in .env, so nobody can use the admin panel.")

    app = Application.builder().token(token).build()

    # group -1 runs first, for every update, so every user is counted
    app.add_handler(TypeHandler(Update, track_update), group=-1)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pdf", ask_pdf_name))
    app.add_handler(CommandHandler("skip", skip_name))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("cancel", admin.cancel))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_image))

    app.add_handler(CommandHandler("admin", admin.admin_command))
    app.add_handler(CommandHandler("addadmin", admin.add_admin_command))
    app.add_handler(CommandHandler("removeadmin", admin.remove_admin_command))
    app.add_handler(CallbackQueryHandler(admin.admin_buttons, pattern=r"^admin:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    logger.info("Bot is running. Keep this window open. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
