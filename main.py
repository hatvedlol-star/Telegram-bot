
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
import subprocess
from docx import Document
from docx.shared import Inches
import fitz  # PyMuPDF

TOKEN = "8207135505:AAH0eOZjnCzFVIKN5ilWSAxEIWfiu2wPBDM"
CHANNEL_USERNAME = "@News_SirMob"
CLOUDCONVERT_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYzkyZDlkNTE4YzY3ZmMxMTkyZGNiYjk5N2JhN2IxZmZhNWE1ZDdjODA0Y2RiZDRlMzdhNTlkYTI5MmQ3ZmViYThhODE3MTQ1NmUxMmNkYWYiLCJpYXQiOjE3NTYyNDI4NjkuODc5NDc0LCJuYmYiOjE3NTYyNDI4NjkuODc5NDc2LCJleHAiOjQ5MTE5MTY0NjkuODczNTE5LCJzdWIiOiI3Mjc1NTMzMCIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.fEXNM-nXsL2ROOnjICMf0UzAAye6DFivfLZT32Xg8Now-EdqjGGVRN5uy4S54A1aUnng6uYDVASlqxVcXIYcFuRjbnI7adrsEQuOfsUykvAUxbv4l5vG296dMQvx9ojwXW0QL4aq2RVrFGMoQVnps0jJDUM88xhewO1ifrA1vbSSAY-7z7WXnIfCbYx4gZQKn21wVC8YB9W3ZSWf5yEv7gX7n7H61cGzFlPs138O5M0K8TCCcBXdf8y1x3ptGaa1Un5pfP08eVe0ajdeCpaCqQUuYk1QKqcR-EuVsX2GZ7BcV18fQBtAkPL2W6-T4KkmVN3lsXh92ox1H6J427hBg8kmCgIf-igx4zhjyWyWC815ASV1wBGhOQ6bwggGe6c29LnSQPf0o-572yiUuijvFfzoef-u14fyPsTbAwFyJ7nMtCYOL7B0TJrMKZv901jYxPtDnhJTI3hLVC1Qq936AxuH0CxgehW547lH7byT00ROz5f9JNWMHNts5ALVC9sLnr8M0MyhtaOUsm7Ol-CEanDzBaJPG6T5pTHNZH5MWcPNJ8QM7N0nc2RexQw113F3TROtAcHJAOpDCGl9SD65aJ2TutiOOi2Kj5UIr9jn7iJaKrOmh95IMmaiWi0F3HnhtWJ7F7x9ftm3uaFxjOtahgBbv10"

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
