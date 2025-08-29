
import os
import time
import tempfile
import requests
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import speech_recognition as sr
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from dotenv import load_dotenv
import subprocess
from docx import Document
from docx.shared import Inches
import fitz  # PyMuPDF

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = "@News_SirMob"
CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

# Dictionary to track user operations
user_operations = {}

def is_subscribed(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def show_subscription_message(update):
    keyboard = [[InlineKeyboardButton("📢 اشترك في قناة المطور", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]]
    update.message.reply_text("اشترك في القناة أولاً.", reply_markup=InlineKeyboardMarkup(keyboard))

def build_main_keyboard():
    keyboard = [
        ["🎬 فيديو ⬅️ صوت", "🖼️ صور ⬅️ PDF"],
        ["📄 PDF ⬅️ Word", "📝 Word ⬅️ PDF"],
        ["🎤 صوت ⬅️ نص"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def build_cancel_keyboard():
    keyboard = [["🛑 إيقاف العملية"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def is_user_busy(user_id):
    return user_id in user_operations

def set_user_operation(user_id, operation):
    user_operations[user_id] = operation

def clear_user_operation(user_id):
    if user_id in user_operations:
        del user_operations[user_id]

def start(update, context):
    user_id = update.effective_user.id
    
    if not is_subscribed(context.bot, user_id):
        show_subscription_message(update)
        return
    
    clear_user_operation(user_id)
    update.message.reply_text(
        "مرحباً! اختر العملية التي تريد تنفيذها:",
        reply_markup=build_main_keyboard()
    )

def handle_message(update, context):
    user_id = update.effective_user.id
    text = update.message.text
    
    if not is_subscribed(context.bot, user_id):
        show_subscription_message(update)
        return
    
    if text == "🛑 إيقاف العملية":
        clear_user_operation(user_id)
        update.message.reply_text("تم إيقاف العملية.", reply_markup=build_main_keyboard())
        return
    
    # Handle main menu options
    if text == "🎬 فيديو ⬅️ صوت":
        set_user_operation(user_id, "video_to_audio")
        update.message.reply_text("أرسل الفيديو الذي تريد تحويله إلى صوت.", reply_markup=build_cancel_keyboard())
    elif text == "🖼️ صور ⬅️ PDF":
        set_user_operation(user_id, "images_to_pdf")
        update.message.reply_text("أرسل الصور التي تريد تحويلها إلى PDF.", reply_markup=build_cancel_keyboard())
    elif text == "📄 PDF ⬅️ Word":
        set_user_operation(user_id, "pdf_to_word")
        update.message.reply_text("أرسل ملف PDF الذي تريد تحويله إلى Word.", reply_markup=build_cancel_keyboard())
    elif text == "📝 Word ⬅️ PDF":
        set_user_operation(user_id, "word_to_pdf")
        update.message.reply_text("أرسل ملف Word الذي تريد تحويله إلى PDF.", reply_markup=build_cancel_keyboard())
    elif text == "🎤 صوت ⬅️ نص":
        set_user_operation(user_id, "audio_to_text")
        update.message.reply_text("أرسل الملف الصوتي الذي تريد تحويله إلى نص.", reply_markup=build_cancel_keyboard())

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
