"""Admin panel inside Telegram: statistics, editable settings and admin management."""
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import db


def owner_id():
    """The owner is the Telegram ID written in the .env file (ADMIN_ID)."""
    value = os.getenv("ADMIN_ID", "").strip()
    return int(value) if value.isdigit() else None


def panel_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📊 Statistics", callback_data="admin:stats")],
            [InlineKeyboardButton("✏️ Edit welcome message", callback_data="admin:welcome")],
            [InlineKeyboardButton("🔢 Change max images", callback_data="admin:maxim")],
            [InlineKeyboardButton("👥 Admins", callback_data="admin:admins")],
        ]
    )


def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin:back")]])


def format_stats(s):
    return (
        "📊 Bot statistics (UTC time)\n\n"
        f"👥 Total users: {s['total_users']}\n\n"
        f"🆕 New users\n  Today: {s['new_today']}\n  Last 7 days: {s['new_7d']}\n  Last 30 days: {s['new_30d']}\n\n"
        f"🟢 Active users\n  Today: {s['active_today']}\n  Last 7 days: {s['active_7d']}\n  Last 30 days: {s['active_30d']}\n\n"
        f"🔁 Returning users: {s['returning_7d']}\n  (joined before this week and used the bot in the last 7 days)\n\n"
        f"⭐ Regular users: {s['regular_30d']}\n  (used the bot on 3+ different days in the last 30 days)\n\n"
        f"📄 PDFs created\n  Total: {s['pdfs_total']}\n  Today: {s['pdfs_today']}"
    )


async def show(query, text, keyboard):
    """Edit the panel message. Ignore Telegram's error when the text did not change."""
    try:
        await query.edit_message_text(text, reply_markup=keyboard)
    except BadRequest:
        pass


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not db.is_admin(update.effective_user.id):
        await update.message.reply_text("Sorry, this command is for admins only.")
        return
    context.user_data.pop("awaiting", None)
    context.user_data.pop("awaiting_pdf_name", None)
    await update.message.reply_text("⚙️ Admin panel", reply_markup=panel_keyboard())


async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not db.is_admin(query.from_user.id):
        return

    context.user_data.pop("awaiting_pdf_name", None)  # the admin is now doing something else
    action = query.data.split(":")[1]
    if action == "stats":
        await show(query, format_stats(db.get_stats()), back_keyboard())
    elif action == "welcome":
        context.user_data["awaiting"] = "welcome_text"
        await show(
            query,
            f"Current welcome message:\n\n{db.get_setting('welcome_text')}\n\n"
            "Send me the new welcome message now, or type /cancel.",
            back_keyboard(),
        )
    elif action == "maxim":
        context.user_data["awaiting"] = "max_images"
        await show(
            query,
            f"Current limit: {db.get_setting('max_images')} images per PDF.\n\n"
            "Send me the new number (1 to 100), or type /cancel.",
            back_keyboard(),
        )
    elif action == "admins":
        ids = "\n".join(f"• {i}" for i in db.list_admins())
        await show(
            query,
            f"👥 Admins:\n{ids}\n\n"
            "Only the owner can change this list:\n/addadmin 123456789\n/removeadmin 123456789",
            back_keyboard(),
        )
    elif action == "back":
        context.user_data.pop("awaiting", None)
        await show(query, "⚙️ Admin panel", panel_keyboard())


async def admin_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receives the admin's next text message after they pressed an edit button."""
    awaiting = context.user_data.get("awaiting")
    if not awaiting or not db.is_admin(update.effective_user.id):
        return

    text = update.message.text.strip()
    if awaiting == "welcome_text":
        db.set_setting("welcome_text", text)
        reply = "✅ Welcome message updated."
    else:  # max_images
        if not text.isdigit() or not 1 <= int(text) <= 100:
            await update.message.reply_text("Please send a number between 1 and 100.")
            return
        db.set_setting("max_images", text)
        reply = f"✅ The limit is now {text} images per PDF."

    context.user_data.pop("awaiting", None)
    await update.message.reply_text(reply, reply_markup=panel_keyboard())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Works for everyone: cancels an admin edit or the question about the PDF name."""
    context.user_data.pop("awaiting", None)
    context.user_data.pop("awaiting_pdf_name", None)
    await update.message.reply_text("Cancelled. Your images are still saved, type /pdf when you are ready.")


async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != owner_id():
        await update.message.reply_text("Only the owner can add admins.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use it like this: /addadmin 123456789")
        return
    db.add_admin(int(context.args[0]))
    await update.message.reply_text("✅ Admin added.")


async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != owner_id():
        await update.message.reply_text("Only the owner can remove admins.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use it like this: /removeadmin 123456789")
        return
    target = int(context.args[0])
    if target == owner_id():
        await update.message.reply_text("The owner cannot be removed.")
        return
    db.remove_admin(target)
    await update.message.reply_text("✅ Admin removed.")
