
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
