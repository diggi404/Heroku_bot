from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def delete_specific_addon(
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
    m = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton("✅", callback_data=f"yes del addon_{addon_id}")
    b2 = types.InlineKeyboardButton("❌", callback_data=f"no del addon")
    m.add(b1, b2)
    addon_app_id_dict["specific_addon_msg_id"] = msg_id
    bot.send_message(chat_id, "Confirm deleting this addon?", reply_markup=m)


def yes_delete_specific_addon(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    addon_app_id_dict: dict,
):
    addon_id = button_data.split("_")[1]
    if (
        chat_id not in active_dict
        or chat_id not in addon_app_id_dict
        or "specific_addon_msg_id" not in addon_app_id_dict
    ):
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    new_msg = bot.edit_message_text("deleting addon...", chat_id, msg_id)
    old_msg_id = addon_app_id_dict["specific_addon_msg_id"]
    app_id = addon_app_id_dict[chat_id]
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.delete(
            f"https://api.heroku.com/apps/{app_id}/addons/{addon_id}", headers=headers
        )
    except:
        bot.edit_message_text(
            "Error deleting addon. Try again.", chat_id, new_msg.message_id
        )
    else:
        if req.status_code == 200:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
            m.add(b)
            bot.delete_message(chat_id, old_msg_id)
            bot.edit_message_text(
                "Addon has been successfully deleted✅",
                chat_id,
                new_msg.message_id,
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
            print(req.status_code)
            print(req.json())
            bot.edit_message_text(
                "Error deleting addon. Try again.", chat_id, new_msg.message_id
            )
