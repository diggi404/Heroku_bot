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
from hard_callback_handlers.apps import apps
from hard_callback_handlers.move_back_apps import move_back_apps
from hard_callback_handlers.move_fwd_apps import move_fwd_apps

from inline_callback_handlers.start_acc_select import start_acc_select
from inline_callback_handlers.apps.view_app import view_app
from inline_callback_handlers.apps.back_to_app_list import back_to_app_list
from inline_callback_handlers.apps.move_back_releases import move_back_releases
from inline_callback_handlers.apps.move_fwd_releases import move_fwd_releases
from inline_callback_handlers.apps.show_releases import show_releases


bot = TeleBot(os.getenv("BOT_TOKEN"))

active_dict = dict()
apps_page_dict = dict()
releases_page_dict = dict()


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    start_bot(bot, message, db_session, active_dict)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: types.CallbackQuery):
    button_data = call.data
    chat_id = call.from_user.id
    msg_id = call.message.id

    if button_data == "cancel menu":
        bot.delete_message(chat_id, msg_id)

    elif button_data.startswith("acc "):
        start_acc_select(bot, chat_id, msg_id, db_session, button_data, active_dict)

    elif button_data.startswith("move back apps:"):
        move_back_apps(bot, chat_id, msg_id, apps_page_dict, active_dict, button_data)

    elif button_data.startswith("move fwd apps:"):
        move_fwd_apps(bot, chat_id, msg_id, apps_page_dict, active_dict, button_data)

    elif button_data == "go back to app list":
        back_to_app_list(bot, chat_id, msg_id, active_dict, apps_page_dict, db_session)

    elif button_data.startswith("app_"):
        view_app(bot, chat_id, msg_id, button_data, active_dict)

    elif button_data.startswith("app releases_"):
        show_releases(
            bot, chat_id, msg_id, button_data, active_dict, releases_page_dict
        )

    elif button_data.startswith("move back r_"):
        move_back_releases(
            bot, chat_id, msg_id, button_data, active_dict, releases_page_dict
        )

    elif button_data.startswith("move fwd r_"):
        move_fwd_releases(
            bot, chat_id, msg_id, button_data, active_dict, releases_page_dict
        )

    elif button_data.startswith("go back to app_"):
        view_app(bot, chat_id, msg_id, button_data, active_dict)


@bot.message_handler(func=lambda message: message.text == "Authorize Bot 🤖")
def handle_authorize_bot(message: types.Message):
    authorize_bot(bot, message.from_user.id, db_session, active_dict)


@bot.message_handler(func=lambda message: message.text == "Register Account")
def handle_register_acc(message: types.Message):
    register_account(bot, message.from_user.id, db_session, active_dict)


@bot.message_handler(func=lambda message: message.text == "Apps")
def handle_apps(message: types.Message):
    apps(bot, message.from_user.id, db_session, active_dict, apps_page_dict)


bot.infinity_polling()
