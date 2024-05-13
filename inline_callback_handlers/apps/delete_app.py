from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def delete_app(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    m = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton("✅", callback_data=f"yes del app_{app_id}")
    b2 = types.InlineKeyboardButton("❌", callback_data=f"no del app_{app_id}")
    m.add(b1, b2)
    bot.edit_message_text("Confirm deleting this app?", chat_id, msg_id, reply_markup=m)


def yes_delete_app(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
            "Content-Type": "application/json",
        }
        req = httpx.delete(
            f"https://api.heroku.com/apps/{app_id}",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error deleting the app. Try again.",
            chat_id,
            msg_id,
        )
    else:
        if req.status_code == 200:
            bot.edit_message_text(
                "The app has been successfully deleted ✅.", chat_id, msg_id
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
                "Error deleting the app. Try again.",
                chat_id,
                msg_id,
            )
