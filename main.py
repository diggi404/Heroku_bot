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
from hard_callback_handlers.settings import settings
from hard_callback_handlers.login import login

from inline_callback_handlers.start_acc_select import start_acc_select
from inline_callback_handlers.apps.view_app import view_app
from inline_callback_handlers.apps.back_to_app_list import back_to_app_list
from inline_callback_handlers.apps.move_back_releases import move_back_releases
from inline_callback_handlers.apps.move_fwd_releases import move_fwd_releases
from inline_callback_handlers.apps.show_releases import show_releases
from inline_callback_handlers.apps.view_logs import view_logs
from inline_callback_handlers.apps.config_vars import config_vars
from inline_callback_handlers.apps.add_config_var import (
    add_config_var,
    yes_config_var,
    no_config_var,
)
from inline_callback_handlers.apps.delete_config_var import (
    delete_config_var,
    yes_del_config_var,
)
from inline_callback_handlers.apps.edit_config_var import (
    edidt_config_var,
    yes_edit_config_var,
)
from inline_callback_handlers.apps.app_addons import get_app_addons
from inline_callback_handlers.apps.move_back_app_addons import move_back_app_addons
from inline_callback_handlers.apps.move_fwd_app_addons import move_fwd_app_addons
from inline_callback_handlers.apps.specific_addon import specific_addon
from inline_callback_handlers.apps.delete_specific_addon import (
    delete_specific_addon,
    yes_delete_specific_addon,
)
from inline_callback_handlers.apps.delete_app import delete_app
from inline_callback_handlers.apps.delete_app import yes_delete_app
from inline_callback_handlers.apps.deploy_app import deploy_app
from inline_callback_handlers.apps.branch_app_deploy import branch_app_deploy
from inline_callback_handlers.create_app.app_name import app_name
from inline_callback_handlers.create_app.choose_region import choose_region
from inline_callback_handlers.create_app.connect_repo import connect_repo
from inline_callback_handlers.create_app.fetch_git_profile import fetch_git_profile
from inline_callback_handlers.apps.toggle_app import toggle_app
from inline_callback_handlers.settings.logout import logout
from inline_callback_handlers.apps.app_create_addon import app_create_addon
from inline_callback_handlers.apps.move_back_app_create_addons import (
    move_back_app_create_addons,
)
from inline_callback_handlers.apps.move_fwd_app_create_addons import (
    move_fwd_app_create_addons,
)
from inline_callback_handlers.apps.app_create_addon_plans import app_create_addon_plans
from inline_callback_handlers.apps.move_back_addon_plans import move_back_addon_plans
from inline_callback_handlers.apps.move_fwd_addon_plans import move_fwd_addon_plans
from inline_callback_handlers.apps.final_create_addon import (
    final_create_addon,
    yes_create_addon,
)
from inline_callback_handlers.apps.addon_plan_update import addon_plan_update
from inline_callback_handlers.apps.move_back_addon_plan_update import (
    move_back_addon_plan_update,
)
from inline_callback_handlers.apps.move_fwd_addon_plan_update import (
    move_fwd_addon_plan_update,
)
from inline_callback_handlers.apps.final_addon_update import (
    final_addon_update,
    yes_update_addon,
)
from inline_callback_handlers.apps.update_dyno import update_dyno
from inline_callback_handlers.apps.move_back_dynos import move_back_dynos
from inline_callback_handlers.apps.move_fwd_dynos import move_fwd_dynos
from inline_callback_handlers.apps.dyno_info import dyno_info, yes_update_dyno


bot = TeleBot(os.getenv("BOT_TOKEN"))

active_dict = dict()
apps_page_dict = dict()
releases_page_dict = dict()
logs_dict = dict()
config_var_dict = dict()
addons_page_dict = dict()
addon_app_id_dict = dict()
git_details_dict = dict()
app_toggle_dict = dict()
app_details_dict = dict()
dyno_page_dict = dict()
dyno_app_id_dict = dict()


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    start_bot(bot, message, db_session, active_dict)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: types.CallbackQuery):
    button_data = call.data
    chat_id = call.from_user.id
    msg_id = call.message.message_id

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
        view_app(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            app_toggle_dict,
            app_details_dict,
        )

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
        view_app(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            app_toggle_dict,
            app_details_dict,
        )

    elif button_data.startswith("go b apps_"):
        old_msg_id = int(button_data.split("_")[-1])
        logs_dict[old_msg_id] = False
        view_app(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            app_toggle_dict,
            app_details_dict,
        )

    elif button_data.startswith("logs_"):
        logs_dict[msg_id] = True
        view_logs(bot, chat_id, msg_id, button_data, active_dict, logs_dict)

    elif button_data.startswith("end logs_"):
        old_msg_id = int(button_data.split("_")[1])
        logs_dict[old_msg_id] = False
        bot.edit_message_text("Logs trail exited.", chat_id, msg_id)

    elif button_data.startswith("configs_"):
        config_vars(bot, chat_id, msg_id, button_data, active_dict, call.id)

    elif button_data.startswith("add var_"):
        add_config_var(bot, chat_id, msg_id, button_data, active_dict, config_var_dict)

    elif button_data.startswith("con var_"):
        yes_config_var(bot, chat_id, msg_id, button_data, active_dict, config_var_dict)

    elif button_data.startswith("no var_"):
        no_config_var(bot, chat_id, msg_id, button_data, active_dict, config_var_dict)

    elif button_data.startswith("del var_"):
        delete_config_var(
            bot, chat_id, msg_id, button_data, active_dict, config_var_dict
        )

    elif button_data.startswith("yes del var_"):
        yes_del_config_var(
            bot, chat_id, msg_id, button_data, active_dict, config_var_dict
        )

    elif button_data.startswith("edit var_"):
        edidt_config_var(
            bot, chat_id, msg_id, button_data, active_dict, config_var_dict
        )

    elif button_data.startswith("yes edit var_"):
        yes_edit_config_var(
            bot, chat_id, msg_id, button_data, active_dict, config_var_dict
        )

    elif button_data.startswith("app addons_"):
        get_app_addons(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move b addons_"):
        move_back_app_addons(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move f addons_"):
        move_fwd_app_addons(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("app addon_"):
        specific_addon(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("go back to addons_"):
        get_app_addons(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("del addon_"):
        delete_specific_addon(
            bot, chat_id, msg_id, button_data, active_dict, addon_app_id_dict
        )

    elif button_data.startswith("yes del addon_"):
        yes_delete_specific_addon(
            bot, chat_id, msg_id, button_data, active_dict, addon_app_id_dict
        )

    elif button_data.startswith("no del addon"):
        bot.edit_message_text("Operation aborted.", chat_id, msg_id)

    elif button_data.startswith("del app_"):
        delete_app(bot, chat_id, msg_id, button_data, active_dict)

    elif button_data.startswith("yes del app_"):
        yes_delete_app(bot, chat_id, msg_id, button_data, active_dict)

    elif button_data.startswith("no del app_"):
        view_app(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            app_toggle_dict,
            app_details_dict,
        )

    elif button_data.startswith("deploy_"):
        deploy_app(bot, chat_id, msg_id, button_data, active_dict, call.id)

    elif button_data.startswith("branch:"):
        branch_app_deploy(bot, chat_id, msg_id, button_data, active_dict)

    elif button_data == "create new app":
        choose_region(bot, chat_id, msg_id, active_dict)

    elif button_data.startswith("region "):
        app_name(bot, chat_id, msg_id, active_dict, button_data)

    elif button_data.startswith("git_"):
        fetch_git_profile(
            bot, chat_id, msg_id, active_dict, button_data, git_details_dict
        )

    elif button_data.startswith("no git_"):
        app_id = button_data.split("_")[1]
        m = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
        m.add(b)
        bot.edit_message_text("Operation aborted.", chat_id, msg_id, reply_markup=m)

    elif button_data.startswith("repo_"):
        connect_repo(bot, chat_id, msg_id, active_dict, button_data, git_details_dict)

    elif button_data == "no git_":
        app_id = button_data.split("_")[1]
        m = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
        m.add(b)
        bot.edit_message_text("Operation aborted.", chat_id, msg_id, reply_markup=m)

    elif button_data.startswith("turn_"):
        toggle_app(bot, chat_id, msg_id, button_data, active_dict, app_toggle_dict)

    elif button_data == "logout":
        logout(bot, chat_id, msg_id, active_dict)

    elif button_data.startswith("create addon_"):
        app_create_addon(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("go back to create addons_"):
        app_create_addon(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move b whole addons_"):
        move_back_app_create_addons(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move f whole addons_"):
        move_fwd_app_create_addons(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("app addon create_"):
        app_create_addon_plans(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move b addon plans_"):
        move_back_addon_plans(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move f addon plans_"):
        move_fwd_addon_plans(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("app addon plan_"):
        final_create_addon(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("yes create addon_"):
        yes_create_addon(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("u addon plan_"):
        addon_plan_update(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move b addon update plans_"):
        move_back_addon_plan_update(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move f addon update plans_"):
        move_fwd_addon_plan_update(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addons_page_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("addon update plan_"):
        final_addon_update(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("yes update addon_"):
        yes_update_addon(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            addon_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("update dyno_"):
        update_dyno(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            dyno_page_dict,
            dyno_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move b dynos_"):
        move_back_dynos(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            dyno_page_dict,
            dyno_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("move f dynos_"):
        move_fwd_dynos(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            dyno_page_dict,
            dyno_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("dyno info_"):
        dyno_info(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            dyno_app_id_dict,
            app_details_dict,
        )

    elif button_data.startswith("yes update dyno_"):
        yes_update_dyno(
            bot,
            chat_id,
            msg_id,
            button_data,
            active_dict,
            dyno_app_id_dict,
            app_details_dict,
        )


@bot.message_handler(func=lambda message: message.text == "Authorize Bot 🤖")
def handle_authorize_bot(message: types.Message):
    authorize_bot(bot, message.from_user.id, db_session, active_dict)


@bot.message_handler(func=lambda message: message.text == "Register Account 👤")
def handle_register_acc(message: types.Message):
    register_account(bot, message.from_user.id, db_session, active_dict)


@bot.message_handler(func=lambda message: message.text == "Apps ☁️")
def handle_apps(message: types.Message):
    apps(bot, message.from_user.id, db_session, active_dict, apps_page_dict)


@bot.message_handler(func=lambda message: message.text == "Settings ⚙️")
def handle_settings(message: types.Message):
    settings(bot, message.from_user.id, active_dict)


@bot.message_handler(func=lambda message: message.text == "Login 🔓")
def handle_login(message: types.Message):
    login(bot, message.from_user.id, db_session)


bot.infinity_polling()
