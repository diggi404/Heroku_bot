from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from decimal import Decimal


def specific_addon(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    addon_app_id_dict: dict,
):
    addon_id = button_data.split("_")[1]
    if chat_id not in active_dict or chat_id not in addon_app_id_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    app_id = addon_app_id_dict[chat_id]
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://api.heroku.com/apps/{app_id}/addons/{addon_id}", headers=headers
        )
    except:
        bot.edit_message_text("Error fetching addon info. Try again.", chat_id, msg_id)
    else:
        if req.status_code == 200:
            info = req.json()
            result_msg = f"""
➖➖➖➖ADDON INFO➖➖➖➖

App Name: <b>{info['app']['name']}</b>
Name: <b>{info['addon_service']['name']}</b>
Plan: <b>{info['plan']['name']}</b>
Status: <b>{info['state'].upper()}</b>
Price: <b>${(Decimal(info['billed_price']['cents']) / Decimal('100')).quantize(Decimal('0.00'))}</b>
➖➖➖➖➖➖➖➖➖➖➖➖
            """
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(
                "Delete", callback_data=f"del addon_{addon_id}"
            )
            btn2 = types.InlineKeyboardButton(
                "Update Plan", callback_data=f"u plan_{addon_id}"
            )
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data=f"go back to addons_{app_id}"
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(btn2, btn1)
            markup.add(back_btn)
            markup.add(close_btn)
            bot.edit_message_text(
                result_msg, chat_id, msg_id, parse_mode="HTML", reply_markup=markup
            )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                msg_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            print(req.status_code)
            print(req.json())
            bot.edit_message_text(
                "Error fetching addon info. Try again.", chat_id, msg_id
            )
