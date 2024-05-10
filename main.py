import time
from telebot import types, TeleBot
import os
from sqlalchemy.orm import Session
from sqlalchemy import exists, func
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread, Lock

load_dotenv()

from database.conn import db_session

from command_handlers.start import start_bot

from hard_callback_handlers.authorize_bot import authorize_bot
from hard_callback_handlers.register_account import register_account

from inline_callback_handlers.start_acc_select import start_acc_select


bot = TeleBot(os.getenv("BOT_TOKEN"))

active_dict = dict()


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    start_bot(bot, message, db_session, active_dict)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: types.CallbackQuery):
    button_data = call.data
    chat_id = call.from_user.id
    msg_id = call.message.id

    if button_data.startswith("acc "):
        start_acc_select(bot, chat_id, msg_id, db_session, button_data, active_dict)


@bot.message_handler(func=lambda message: message.text == "Authorize Bot 🤖")
def handle_authorize_bot(message: types.Message):
    authorize_bot(bot, message.from_user.id, db_session, active_dict)


@bot.message_handler(func=lambda message: message.text == "Register New Account")
def handle_register_acc(message: types.Message):
    register_account(bot, message.from_user.id, db_session, active_dict)


bot.infinity_polling()
