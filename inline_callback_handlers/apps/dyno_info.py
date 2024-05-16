from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from decimal import Decimal


def dyno_info(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    dyno_app_id_dict: dict,
    app_details_dict: dict,
):
    dyno_id = button_data.split("_")[1]
    if (
        chat_id not in active_dict
        or chat_id not in app_details_dict
        or "main_dyno_info" not in app_details_dict
    ):
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://api.heroku.com/dyno-sizes/{dyno_id}",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error fetching dyno info. Try again.",
            chat_id,
            msg_id,
        )
    else:
        if req.status_code == 200:
            info = req.json()
            app_name = app_details_dict[chat_id]
            app_id = dyno_app_id_dict[chat_id]
            result_msg = f"""
➖➖➖➖DYNO INFO➖➖➖➖

App Name: <b>{app_name}</b>

Dyno Name: <b>{info['name'].upper()}</b>
vCPUs: <b>{info['compute']}</b>
Memory (RAM): <b>{info['memory']}GB</b>
Dedicated: <b>{info['dedicated']}</b>
Private Space Only: <b>{info['private_space_only']}</b>
Price: <b>{'Not Available' if info['cost']['cents'] is None else '$' + str((Decimal(info['cost']['cents']) / Decimal('100.00')).quantize(Decimal('0.00')))}</b>
Unit: <b>{'Not Available' if info['cost']['unit'] is None else 'Monthly'}</b>

Confirm updating updating your app to this Dyno?
            """
            m = types.InlineKeyboardMarkup()
            b1 = types.InlineKeyboardButton(
                "✅", callback_data=f"yes update dyno_{dyno_id}"
            )
            b2 = types.InlineKeyboardButton("❌", callback_data=f"update dyno_{app_id}")
            m.add(b1, b2)
            app_details_dict["main_dyno_info"].append(info["name"])
            bot.edit_message_text(
                result_msg, chat_id, msg_id, reply_markup=m, parse_mode="HTML"
            )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                msg_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error fetching dyno info. Try again.",
                chat_id,
                msg_id,
            )


def yes_update_dyno(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    dyno_app_id_dict: dict,
    app_details_dict: dict,
):
    dyno_id = button_data.split("_")[1]
    if (
        chat_id not in active_dict
        or chat_id not in app_details_dict
        or "main_dyno_info" not in app_details_dict
    ):
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    new_msg = bot.edit_message_text("Updating dyno size...", chat_id, msg_id)
    d_type = app_details_dict["main_dyno_info"][0]
    d_size = app_details_dict["main_dyno_info"][2]
    app_name = app_details_dict[chat_id]
    app_id = dyno_app_id_dict[chat_id]
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req_data = {
            "updates": [
                {
                    "id": dyno_id,
                    "quantity": 1,
                    "type": d_type,
                    "size": d_size,
                }
            ]
        }
        req = httpx.patch(
            f"https://api.heroku.com/apps/{app_id}/formation",
            headers=headers,
            json=req_data,
        )
    except:
        bot.edit_message_text(
            "Error updating dyno size. Try again.",
            chat_id,
            new_msg.message_id,
        )
    else:
        if req.status_code == 200:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
            m.add(b)
            bot.edit_message_text(
                f"The dyno size for your app <b>{app_name}</b> has been updated to <b>{d_size}</b> ✅.",
                chat_id,
                new_msg.message_id,
                parse_mode="HTML",
                reply_markup=m,
            )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                new_msg.message_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error updating dyno size. Try again.",
                chat_id,
                new_msg.message_id,
            )
