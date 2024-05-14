from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from decimal import Decimal


def final_addon_update(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    addon_app_id_dict: dict,
    app_details_dict: dict,
):
    plan_id = button_data.split("_")[1]
    if (
        chat_id not in active_dict
        or chat_id not in app_details_dict
        or plan_id not in app_details_dict
    ):
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    app_id = addon_app_id_dict[chat_id]
    addon_name = app_details_dict["selected_addon"]
    plan_name = app_details_dict[plan_id][0]
    price = app_details_dict[plan_id][1]
    app_name = app_details_dict[chat_id]
    m = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton("✅", callback_data=f"yes update addon_{plan_id}")
    b2 = types.InlineKeyboardButton("❌", callback_data=f"no git_{app_id}")
    m.add(b1, b2)
    bot.edit_message_text(
        f"""
➖➖➖➖ADDON CHECKOUT➖➖➖➖

App Name: <b>{app_name}</b>
Addon Name: <b>{addon_name}</b>
Plan: <b>{plan_name}</b>
Price: <b>{price}</b>

Do you confirm updating your addon plan?
                          """,
        chat_id,
        msg_id,
        reply_markup=m,
        parse_mode="HTML",
    )


def yes_update_addon(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    addon_app_id_dict: dict,
    app_details_dict: dict,
):
    plan_id = button_data.split("_")[1]
    if (
        chat_id not in active_dict
        or chat_id not in app_details_dict
        or plan_id not in app_details_dict
    ):
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    new_msg = bot.edit_message_text("Updating addon...", chat_id, msg_id)
    app_id = addon_app_id_dict[chat_id]
    addon_name = app_details_dict["selected_addon"]
    plan_name = app_details_dict[plan_id][0]
    app_name = app_details_dict[chat_id]
    addon_id = app_details_dict["addon_id"]
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req_data = {"plan": f"{plan_id}"}
        req = httpx.patch(
            f"https://api.heroku.com/apps/{app_id}/addons/{addon_id}",
            headers=headers,
            json=req_data,
        )
    except:
        bot.edit_message_text(
            "Error updating addon. Try again.", chat_id, new_msg.message_id
        )
    else:
        if req.status_code == 200:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
            m.add(b)
            bot.edit_message_text(
                f"Your addon <b>{addon_name}</b> has been updated to <b>{plan_name}</b> plan associated with the app <b>{app_name}</b> ✅.",
                chat_id,
                new_msg.message_id,
                parse_mode="HTML",
                reply_markup=m,
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
                "Error updating addon. Try again.", chat_id, new_msg.message_id
            )
