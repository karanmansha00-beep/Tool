#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# ═══════════════════════════════════════════════
#   Arya - Telegram Group Manager Tool
# ═══════════════════════════════════════════════
"""

import asyncio
import os
import json
import random
import time
import logging
import sys
import io
from typing import Set, Dict, List
from datetime import datetime, timedelta, timezone

# ================= WINDOWS ASYNCIO FIX =================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ================= TELEGRAM IMPORTS =================
from telegram import Update
from telegram.ext import Application, ContextTypes, PrefixHandler
from telegram.error import RetryAfter

# ================= MULTI BOT TOKENS =================
BOT_TOKENS = [
    "8672545028:AAHAg_9N4bHDmwtNL0Gyixygp-g4fDIWklM",
"8705166409:AAF7kMKcMBT5t6V7UV7ot8xyMRM0wjI8Wcg",
"8661068456:AAGHyK5UmOak5fMBYsyu99k7Il6ULHhZpWY",
"7792506919:AAFDPRTAu4TuzETDmh5Vfu_0C7r3q9FMBxs",
"8272449193:AAHpiURkVrJsJpqNojiE2PSYp0F0CYWrkAE",
"8888295645:AAE9VlrKkUdCbNJUKanbgWJ4Gh5i_XrQDYY",
"8685098913:AAHFC7vwbEbDV6yrs2TBjMZWmFnOpGSyrhk",
"8940927157:AAE3H73nAYAYWjvWeG1fEPfW3skJu_9LAE8",
"8845755595:AAE63gK0_zvSOs4wZLFKjBtj8lxLay1bLOA",
"8650596065:AAFBgvNCexVOqisUQj0l4oois02628Y_SCo",
"8734256687:AAH7UAM7BlUMYzOitUIX79faDXH-OpZptT0",
"8684815584:AAGgsuBcfXK8teBAz_gFO5vX37METTA1lhA",
"8886032597:AAE3Vsyw6jk8HW-RPsGgGYUzgruSi2ixUvg",
"8960691268:AAFZQFXkqQpX66e9i8lQoZUxynIDKE8dheM",
]

OWNER_ID = 8783901855
GLOBAL_DELAY = 0.0
CURRENT_PREFIX = "."

# ================= LOGGING =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= GLOBALS =================
start_time = time.time()
nc_tasks: Dict[int, List[asyncio.Task]] = {}
spam_tasks: Dict[int, List[asyncio.Task]] = {}
nc_counters: Dict[int, int] = {}
spam_counters: Dict[int, int] = {}
SUDO_USERS: Set[int] = set()
ACTIVE_TASKS: Dict[int, str] = {}
AUTHORIZATION_MSG = "𝐒TAY 𝐀WAY 𝐊IDZ"
ALL_BOTS = []

# ================= LOAD SUDO USERS =================
SUDO_FILE = "sudo_users.json"

def load_sudo():
    global SUDO_USERS
    try:
        if os.path.exists(SUDO_FILE):
            with open(SUDO_FILE, "r") as f:
                data = json.load(f)
                SUDO_USERS = set(data.get("users", []))
    except:
        SUDO_USERS = set()

def save_sudo():
    try:
        with open(SUDO_FILE, "w") as f:
            json.dump({"users": list(SUDO_USERS)}, f)
    except:
        pass

load_sudo()

# ================= AUTHORIZATION DECORATORS =================
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID and uid not in SUDO_USERS:
            try:
                await update.message.reply_text(AUTHORIZATION_MSG)
            except:
                pass
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID:
            try:
                await update.message.reply_text("Only owner can use this command!")
            except:
                pass
            return
        return await func(update, context)
    return wrapper

# ================= SET PREFIX COMMAND =================
@only_owner
async def setprefix_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_PREFIX
    if not context.args:
        await update.message.reply_text(f"Current prefix: {CURRENT_PREFIX}\nUsage: .setprefix <new_prefix>")
        return
    new_prefix = context.args[0].strip()
    if len(new_prefix) > 3:
        await update.message.reply_text("Prefix too long! Max 3 characters.")
        return
    CURRENT_PREFIX = new_prefix
    await update.message.reply_text(f"Prefix changed to: {CURRENT_PREFIX}")

# ================= GAME OVER COMMAND =================
@only_owner
async def gameover_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    current_time = now_ist.strftime("%I:%M:%S %p")
    current_date = now_ist.strftime("%d %B %Y")

    user = update.effective_user
    message = update.effective_message
    name = (
        f"@{user.username}"
        if user and user.username
        else (user.first_name if user else "UNKNOWN USER")
    )
    chat = update.effective_chat
    group_name = chat.title if chat and chat.title else "UNKNOWN GROUP"
    text = (
        f"=========================\n"
        f"Game over Time - {current_time}\n"
        f"Date - {current_date} (IST)\n\n"
        f"Abb baap ke agge\n"
        f"Hawabazzi karne mat aana\n\n"
        f"Group - {group_name}\n\n"
        f"Teri maa chud ke dfn by - {name}\n"
        f"========================="
    )

    if message:
        await message.reply_video(
            video="https://files.catbox.moe/2pltx5.mp4",
            caption=text,
        )

# ================= TARGET STYLE =================
TARGET_SOURCE = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
TARGET_STYLE = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
TARGET_TRANSLATION = str.maketrans(TARGET_SOURCE, TARGET_STYLE)

def transform_nc_target(text: str) -> str:
    return text.translate(TARGET_TRANSLATION)

# ================= NC1 - FLOWERS EMOJIS WITH ABUSE WORDS =================
NC1_EMOJIS = ["🥱","😱","🤨","😒","😡","🤬","😤","😮‍💨","🥵","🥶","🤢","🤮","🫩","😈","👿","👽","🧃","🧋","🗻","🃏","💠","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇧🇦","🇧🇶","🇧🇱","🇧🇫","🇨🇮","🇨🇩","🇨🇦","🇨🇿","🇩🇯","🇨🇭","🇪🇬","🇨🇨","🇧🇯","🇧🇶","🇰🇿","🇰🇼","🇰🇳","🇲🇭","🇲🇪","🇲🇬","🇰🇳","🇮🇴","🇯🇵","🇷🇺","🇳🇺","🇵🇬","🇸🇩","🇵🇷","🇵🇳","🇵🇭","🇳🇫","🇳🇪","🇺🇾","🇺🇸","🇻🇪","🌊","🌬️","❄️","🌀","🌪️","⚡","☔","🌈","💧","☁️","🌨️","🌧️","🌩️","⛈️","🌦️","🌥️","⛅","🌤️","☀️","🌞","🌝","🌚","🌜","🌛","🌙","⭐","🌟","✨","🪐","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]

NC1_WORDS = [
   "<🐶> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🐺> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🐻‍❄️> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🦁> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🐯> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🦄> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🐲> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🦎> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🦖> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫",
    "<🦕> ᴛᴍᴋᴄ 🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫👾𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🧃𒐫𒐫𒐫🍌𒐫𒐫 𒐫𒐫𒐫🍌𒐫"
    "ARYA PAPA KI JAY HO",
]

NC1_PATTERN = "𓏲 ๋࣭ ࣪ ˖ {emoji} 𓂃 ࣪˖ {target} {word} 𓏲 ๋࣭   ࣪ ˖ {emoji} 𓂃 ࣪˖"

# ================= NC2 - HEART EMOJIS WITH ABUSE WORDS =================
NC2_EMOJIS = ["🥱","😱","🤨","😒","😡","🤬","😤","😮‍💨","🥵","🥶","🤢","🤮","🫩","😈","👿","👽","🧃","🧋","🗻","🃏","💠","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇧🇦","🇧🇶","🇧🇱","🇧🇫","🇨🇮","🇨🇩","🇨🇦","🇨🇿","🇩🇯","🇨🇭","🇪🇬","🇨🇨","🇧🇯","🇧🇶","🇰🇿","🇰🇼","🇰🇳","🇲🇭","🇲🇪","🇲🇬","🇰🇳","🇮🇴","🇯🇵","🇷🇺","🇳🇺","🇵🇬","🇸🇩","🇵🇷","🇵🇳","🇵🇭","🇳🇫","🇳🇪","🇺🇾","🇺🇸","🇻🇪","🌊","🌬️","❄️","🌀","🌪️","⚡","☔","🌈","💧","☁️","🌨️","🌧️","🌩️","⛈️","🌦️","🌥️","⛅","🌤️","☀️","🌞","🌝","🌚","🌜","🌛","🌙","⭐","🌟","✨","🪐","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]

NC2_WORDS = [
    "TMKB",
    "TMKC",
    "RAND",
    "BKL",
    "TMR",
    "LUNKHA",
    "MADERCHOD",
    "BSDK",
    "GANDU",
    "TMKC MACCHAR",
    "PLAYGIRL",
    "ASSHOLE",
    "NIGGA",
    "FUCKYOU",
    "PERVERT",
    "STEPSIS",
    "MOTHERFUCKER",
    "BOBBIE",
    "BASTARD",
    "PIECEOFSHIT",
]

NC2_PATTERN = "『{emoji}』 {target} {word} 『{emoji}』"

# ================= SPAM TEXTS - 2 SLOTS (UPDATED) =================
SPAM1_TEXTS = [
"""༒🩷༒{target} ᴛᴇʀɪ  माँ चुद ɢʏɪ ༒🩷༒






















༒🩷༒{target} ᴛᴇʀɪ  माँ चुद ɢʏɪ ༒🩷༒

























༒🩷༒{target} ᴛᴇʀɪ  माँ चुद ɢʏɪ ༒🩷༒""",
"""╔════════    ════════╗
        ✞ {target} 𝐓𝐌𝐊𝐂 ✞
 ╚════════    ════════╝

















╔════════    ════════╗
        ✞ {target} 𝐓𝐌𝐊𝐂 ✞
╚════════    ════════╝



















╔════════    ════════╗
        ✞ {target} 𝐓𝐌𝐊𝐂 ✞
╚════════    ════════╝""",
"""{target}  की चुदाई   𝐁ʏ ~/ 𝐀rya Pᴀᴘᴀ  🌙🩶✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆ ㅤㅤ{target}  की  चुदाई   𝐁ʏ ~/ 𝐀𝐫𝐲𝐀 Pᴀᴘᴀ   🌙🩶 ✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆ㅤ{target}  की  चुदाई   𝐁ʏ ~/ 𝐀𝐫𝐲𝐀 Pᴀᴘᴀ  🌙🩶✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆✧･ﾟ: ✧･ﾟ:⋆｡ﾟ｡⋆｡ ﾟ☾ ﾟ｡⋆ ㅤㅤ{target} की  चुदाई   𝐁ʏ ~/ 𝐀𝐫𝐲𝐚 Pᴀᴘᴀ   🌙🩶""",
]

SPAM2_TEXTS = [
"""━━〔 {target} की चुदाई 🧐〕━━ 𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤
𒈙𒐫𒈙🖤𒐫𒈙𒐫🖤𒈙𒐫𒈙🖤━━〔 {target} की चुदाई 🧐〕━━""",
]

SPAM_TEXTS_MAP: Dict[int, list] = {
    1: SPAM1_TEXTS,
    2: SPAM2_TEXTS,
}

# ================= SLIDE MESSAGES =================
SLIDE_MESSAGES = [
    "{target}Kya Re Randike Cool Banega Tu Chal Ab Chud Apne Baap AryA Se",
    "{target}Ki Maa Marr Gayi Yaar - Jai AryA !",
    "{target}acha beta ? coi na me toh HATER codunga",
    "{target}chudke bhaga kaise",
    "{target}ne toh AryA ka lun muh me lelia",
    "{target}try maa surya nikalte hi pel du",
    "{target}{target}mkl lun te vaj",
    "{target}TmkB pe AryA ka hamla",
    "{target}Chl Haramzadi Ke ladke",
    "{target}oi Teri Maa gulam",
    "{target}chl rndyce chud ke dikha",
    "{target}Ki Maa Marr Gayi naacho",
    "{target}tera baap bass AryA hai",
    "{target}try maa hagte hue paad mari",
    "{target}Teri Mummy Chod Di AryA Ne Bwahahaha",
    "{target}Cyu Re madarchod AryA baap ke samne Fyter Banega",
    "{target}nahi nahi teri maa ko Sirf AryA baap chod sakta hai samjha randike",
    "{target}teri maa ka Stylish bhosda",
    "{target}Tery maa randAL h bas baat khatam",
    "{target}soch teri behan ko AryA baap ka gulam chod raha",
    "{target}Hello hello?? Oxygen aarahi hai? Randi putra",
    "{target}Shut up randike warna duniya yahi bolegi teri behan AryA baap se sahi chudi",
    "{target}tu or teri maa dono AryA baap ke lnd se kabhi uth nahi paye",
    "{target}BHARAT HAMARA DESH H AUR US DESH ME teri maa ghar ghar jakar MOAN karti hai"
]

# ================= SPAM WORKER =================
async def spam_worker_with_counter(bot, chat_id, base_text, spam_type, counter_dict):
    texts = SPAM_TEXTS_MAP.get(spam_type, SPAM1_TEXTS)
    idx = 0
    while True:
        try:
            text = texts[idx % len(texts)].format(target=base_text)
            await bot.send_message(chat_id, text)
            counter_dict[chat_id] = counter_dict.get(chat_id, 0) + 1
            idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(0)

# ================= SPAM COMMAND HANDLERS =================
@only_sudo
async def spam1_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Use: .spam1 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    
    spam_counters[chat_id] = 0
    tasks = [asyncio.create_task(spam_worker_with_counter(bot, chat_id, text, 1, spam_counters)) for bot in ALL_BOTS]
    spam_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = "spam1"
    await update.message.reply_text(f"Spam1 started with {len(ALL_BOTS)} bots!\nTarget: {text}")

@only_sudo
async def spam2_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Use: .spam2 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    
    spam_counters[chat_id] = 0
    tasks = [asyncio.create_task(spam_worker_with_counter(bot, chat_id, text, 2, spam_counters)) for bot in ALL_BOTS]
    spam_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = "spam2"
    await update.message.reply_text(f"Spam2 started with {len(ALL_BOTS)} bots!\nTarget: {text}")

# ================= SLIDE COMMAND HANDLERS =================
@only_sudo
async def slide_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a message to start slide!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    target_name = update.message.reply_to_message.from_user.first_name
    
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    
    tasks = [asyncio.create_task(slide_worker(bot, chat_id, target_msg_id, target_name)) for bot in ALL_BOTS]
    nc_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = "slide"
    await update.message.reply_text(f"Slide started on {target_name} with {len(ALL_BOTS)} bots!")

async def slide_worker(bot, chat_id, target_msg_id, target_name):
    idx = 0
    while True:
        try:
            msg = SLIDE_MESSAGES[idx % len(SLIDE_MESSAGES)].format(target=target_name)
            await bot.send_message(chat_id, msg, reply_to_message_id=target_msg_id)
            idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)

# ================= NC COMMAND HANDLERS =================
@only_sudo
async def nc1_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Use: .nc1 <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    
    tasks = []
    for idx, bot in enumerate(ALL_BOTS):
        task = asyncio.create_task(nc1_worker(bot, chat_id, base, nc_counters, idx))
        tasks.append(task)
    
    nc_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = "nc1"
    await update.message.reply_text(f"{base} - NC1 started with {len(ALL_BOTS)} bots!")

@only_sudo
async def nc2_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Use: .nc2 <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    
    tasks = []
    for idx, bot in enumerate(ALL_BOTS):
        task = asyncio.create_task(nc2_worker(bot, chat_id, base, nc_counters, idx))
        tasks.append(task)
    
    nc_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = "nc2"
    await update.message.reply_text(f"{base} - NC2 started with {len(ALL_BOTS)} bots!")

# ================= NC WORKER FUNCTIONS =================
async def nc1_worker(bot, chat_id, base_text, counter_dict, bot_index):
    emoji_len = len(NC1_EMOJIS)
    word_len = len(NC1_WORDS)
    e_idx = random.randint(0, 1000) + bot_index * 100
    w_idx = random.randint(0, 1000) + bot_index * 100
    
    while True:
        try:
            emoji = NC1_EMOJIS[e_idx % emoji_len]
            word = NC1_WORDS[w_idx % word_len]
            text = NC1_PATTERN.format(target=transform_nc_target(base_text), word=word, emoji=emoji)
            await bot.set_chat_title(chat_id, text)
            counter_dict[chat_id] = counter_dict.get(chat_id, 0) + 1
            e_idx += 1
            w_idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)

async def nc2_worker(bot, chat_id, base_text, counter_dict, bot_index):
    emoji_len = len(NC2_EMOJIS)
    word_len = len(NC2_WORDS)
    e_idx = random.randint(0, 1000) + bot_index * 100
    w_idx = random.randint(0, 1000) + bot_index * 100
    
    while True:
        try:
            emoji = NC2_EMOJIS[e_idx % emoji_len]
            word = NC2_WORDS[w_idx % word_len]
            text = NC2_PATTERN.format(target=transform_nc_target(base_text), word=word, emoji=emoji)
            await bot.set_chat_title(chat_id, text)
            counter_dict[chat_id] = counter_dict.get(chat_id, 0) + 1
            e_idx += 1
            w_idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)

# ================= STOP COMMANDS =================
@only_sudo
async def stopnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    if chat_id in ACTIVE_TASKS:
        del ACTIVE_TASKS[chat_id]
    await update.message.reply_text("NC stopped!")

@only_sudo
async def stopspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    if chat_id in ACTIVE_TASKS:
        del ACTIVE_TASKS[chat_id]
    await update.message.reply_text("Spam stopped!")

@only_sudo
async def stopall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for d in (nc_tasks, spam_tasks):
        if chat_id in d:
            for task in d[chat_id]:
                task.cancel()
            del d[chat_id]
    if chat_id in ACTIVE_TASKS:
        del ACTIVE_TASKS[chat_id]
    await update.message.reply_text("All tasks stopped!")

# ================= SUDO MANAGEMENT COMMANDS =================
@only_owner
async def addsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a user to make them sudo!")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"Sudo added: {uid}")

@only_owner
async def delsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a user to remove from sudo!")
    uid = update.message.reply_to_message.from_user.id
    if uid == OWNER_ID:
        return await update.message.reply_text("Cannot remove owner!")
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"Sudo removed: {uid}")
    else:
        await update.message.reply_text("This user is not sudo!")

@only_sudo
async def listsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["SUDO USERS LIST:"]
    for uid in SUDO_USERS:
        if uid == OWNER_ID:
            lines.append(f"{uid} (Owner)")
        else:
            lines.append(f"{uid}")
    lines.append(f"\nTotal: {len(SUDO_USERS)}")
    await update.message.reply_text("\n".join(lines))

# ================= STATUS & INFO COMMANDS =================
@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int(time.time() - start_time)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    seconds = uptime % 60
    
    status_text = f"""
Arya Bot Activity
Uptime: {hours}h {minutes}m {seconds}s
Speed: 0.0s (ULTRA FAST)
Bots Online: {len(ALL_BOTS)}
NC Tasks: {len(nc_tasks)}
Spam Tasks: {len(spam_tasks)}
Sudo Users: {len(SUDO_USERS)}
Floodless: ACTIVE
Powered By: Arya
"""
    await update.message.reply_text(status_text)

@only_sudo
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("Pinging...")
    end = time.time()
    await msg.edit_text(f"Pong! {round((end - start) * 1000)}ms")

# ================= PROMOTE ALL BOTS =================
@only_sudo
async def promoteallbots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    try:
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            return await update.message.reply_text("I need to be admin first!")
    except:
        return await update.message.reply_text("Failed to check admin status!")
    
    status_msg = await update.message.reply_text("Promoting bots...")
    promoted = 0
    failed = 0
    
    for bot in ALL_BOTS:
        try:
            me = await bot.get_me()
            await context.bot.promote_chat_member(
                chat_id=chat_id,
                user_id=me.id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                can_manage_chat=True,
                can_manage_video_chats=True
            )
            promoted += 1
            await status_msg.edit_text(f"Promoted {promoted} bots...")
        except:
            failed += 1
            continue
    
    await status_msg.edit_text(
        f"Promotion Complete!\n"
        f"Promoted: {promoted} bots\n"
        f"Failed: {failed} bots"
    )

# ================= LEAVE COMMAND =================
@only_sudo
async def leave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    chat_title = update.effective_chat.title or "this chat"
    await update.message.reply_text(f"Leaving {chat_title}...")
    for bot in ALL_BOTS:
        try:
            await bot.leave_chat(chat_id)
        except:
            pass

# ================= DELAY COMMAND =================
@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_DELAY
    if not context.args:
        await update.message.reply_text(f"Current delay: {GLOBAL_DELAY}s\nUsage: .delay <seconds>")
        return
    try:
        new_delay = float(context.args[0])
        if new_delay < 0.0:
            new_delay = 0.0
        if new_delay > 5.0:
            new_delay = 5.0
        GLOBAL_DELAY = new_delay
        await update.message.reply_text(f"Delay set to {GLOBAL_DELAY}s")
    except:
        await update.message.reply_text("Invalid number!")

# ================= HELP / MENU COMMAND (with VIDEO) =================
@only_sudo
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
🔥 ARYA BOT MENU 🔥 
━━━━━━━━━━━━━━━━━━━━━
💉 NC SECTION
✦ .nc1 <text> — NC Mode 1
✦ .nc2 <text> — NC Mode 2
━━━━━━━━━━━━━━━━━━━━━
🌊 SPAM SECTION
✦ .spam1 <text> — Spam Mode 1
✦ .spam2 <text> — Spam Mode 2
━━━━━━━━━━━━━━━━━━━━━
⚔️ SLIDE SECTION
✦ .slide — Reply to user to abuse
━━━━━━━━━━━━━━━━━━━━━
🛑 STOP COMMANDS
✦ .stopnc — Stop NC
✦ .stopspam — Stop Spam
✦ .stopall — Stop Everything
👑 SUDO COMMANDS
━━━━━━━━━━━━━━━━━━━━━
✦ .addsudo — Add Sudo (Reply)
✦ .delsudo — Remove Sudo (Reply)
✦ .listsudo — List Sudo Users
━━━━━━━━━━━━━━━━━━━━━
🛠️ ADMIN COMMANDS
✦ .promoteallbots — Promote All Bots
✦ .leave — Leave Group
━━━━━━━━━━━━━━━━━━━━━
⚙️ SETTINGS
✦ .delay <seconds> — Set Speed Delay
✦ .setprefix <prefix> — Change Prefix
━━━━━━━━━━━━━━━━━━━━━
📊 BOT INFO
✦ .status — Bot Status
✦ .ping — Check Latency
✦ .help — Show This Menu
━━━━━━━━━━━━━━━━━━━━━
⚡ Speed: 0.0s (Ultra Fast!)
🤖 Bots: {len(ALL_BOTS)} Online
"""
    try:
        await update.message.reply_video(
            video="https://files.catbox.moe/dai6bb.mp4",
            caption=help_text,
            parse_mode=None
        )
    except Exception:
        try:
            await update.message.reply_photo(
                photo="https://files.catbox.moe/uhmfbl.jpg",
                caption=help_text,
                parse_mode=None
            )
        except Exception:
            await update.message.reply_text(help_text)

# ================= MAIN WITH MULTI BOT SUPPORT =================
async def run_bots():
    global ALL_BOTS
    
    apps = []
    print("Starting all bots...")
    print("Ultra speed mode: 0.0s delay")
    print("All bots will work together\n")
    
    for i, token in enumerate(BOT_TOKENS):
        try:
            app = Application.builder().token(token).build()
            
            # NC commands
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "nc1", nc1_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "nc2", nc2_cmd))
            # Spam commands
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "spam1", spam1_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "spam2", spam2_cmd))
            # Slide
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "slide", slide_cmd))
            # Stop commands
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "stopnc", stopnc_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "stopspam", stopspam_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "stopall", stopall_cmd))
            # Sudo commands
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "addsudo", addsudo_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "delsudo", delsudo_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "listsudo", listsudo_cmd))
            # Admin commands
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "promoteallbots", promoteallbots_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "leave", leave_cmd))
            # Settings
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "setprefix", setprefix_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "gameover", gameover_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "delay", delay_cmd))
            # Info
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "status", status_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "ping", ping_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "help", help_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "menu", help_cmd))
            app.add_handler(PrefixHandler(CURRENT_PREFIX, "panel", help_cmd))
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            
            apps.append(app)
            ALL_BOTS.append(app.bot)
            
            print(f"Bot {i+1} online: {token[:15]}...")
        except Exception as e:
            print(f"Failed to start bot{i+1}: {e}")
    
    print(f"\nTotal bots online: {len(ALL_BOTS)}")
    print(f"Owner ID: {OWNER_ID}")
    print(f"Speed: 0.0s (ULTRA FAST)")
    print(f"Prefix: {CURRENT_PREFIX}")
    print("Arya bot is running!\n")
    
    await asyncio.Event().wait()

def main():
    try:
        asyncio.run(run_bots())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()