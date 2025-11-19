import re
import time
from datetime import datetime, timedelta
from telegram import ChatPermissions, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from langdetect import detect
import os

# ===== BOT TOKEN =====
TOKEN = os.getenv("BOT_TOKEN")

# ===== ADMIN LOG CHANNEL =====
ADMIN_LOG_CHAT = -1003383035433

# ===== CONTACT LIST =====
CONTACT_LIST = """
📞 *Tabu II Kontaktliste | Tabu II Contact List*

👤 *Senior*
📧 senioren.tabu2@web.de

👤 *Hausmeister / Caretaker*
📧 wh.hirschbergerstr@studierendenwerk-bonn.de

👮 *Sicherheitsdienst / Security*
📞 0157 331 3590
🕒 Fr–So, 17:00–01:00

🚑 112
👮♂️ 110
"""

# Warn memory
user_warnings = {}

# Spam detection
spam_tracker = {}


# ========== GREETING NEW MEMBERS ==========
def greet(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        update.message.reply_text(
            f"Willkommen {member.first_name}! 👋\nBitte halte dich an die Gruppenregeln."
        )


# ========== COMMAND: /hilfe ==========
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(CONTACT_LIST, parse_mode="Markdown")


# ========== RULE CHECK ==========
def is_spam(user_id):
    now = time.time()
    spam_tracker.setdefault(user_id, [])
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if now - t < 10]
    spam_tracker[user_id].append(now)
    return len(spam_tracker[user_id]) > 5


def warn_user(update, context, rule_text):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
    warn_count = user_warnings[user_id]

    update.message.reply_text(f"⚠️ Regelverstoß: {rule_text}\nWarnung {warn_count}/3")

    # Log to admin channel
    try:
        context.bot.send_message(
            ADMIN_LOG_CHAT,
            f"⚠️ User {user_id} violated: {rule_text}\nWarnings: {warn_count}/3"
        )
    except:
        pass

    # Mute after 3 warnings
    if warn_count >= 3:
        until_time = datetime.now() + timedelta(days=1)
        permissions = ChatPermissions(can_send_messages=False)

        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=permissions,
            until_date=until_time
        )

        update.message.reply_text("🚫 1 Tag Stummschaltung wegen wiederholter Regelverstöße.")
        user_warnings[user_id] = 0


def check_rules(update: Update, context: CallbackContext):
    message = update.message
    text = message.text.lower()
    user_id = message.from_user.id

    # SPAM
    if is_spam(user_id):
        message.delete()
        warn_user(update, context, "Spam ist nicht erlaubt")
        return

    # LANGUAGE
    try:
        lang = detect(text)
        if lang not in ["de", "en"]:
            message.delete()
            warn_user(update, context, "Nur Deutsch oder Englisch erlaubt")
            return
    except:
        pass

    # SUBLETTING
    sublet_words = ["zimmer", "room", "rent", "miete", "untervermietung", "sublet", "wg"]
    if any(w in text for w in sublet_words):
        message.delete()
        warn_user(update, context, "Untervermietung ist verboten")
        return

    # LINKS
    if "http://" in text or "https://" in text or "t.me/" in text:
        message.delete()
        warn_user(update, context, "Links und Werbung sind nicht erlaubt")
        return

    # POLITICS
    political_terms = ["afd", "cdu", "spd", "trump", "biden", "lgbtq"]
    if any(w in text for w in political_terms):
        message.delete()
        warn_user(update, context, "Politik/Ideologie ist verboten")
        return


# ========== BOT STARTUP ==========
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("hilfe", help_command))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_rules))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
