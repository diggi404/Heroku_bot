from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def toggle_app(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    app_toggle_dict: dict,
):
    toggle_id = int(button_data.split("_")[1])
    app_id = button_data.split("_")[2]
    if chat_id not in active_dict or chat_id not in app_toggle_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    toggle_details = app_toggle_dict.get(chat_id, [])
    d_type = toggle_details[0]
    d_size = toggle_details[1]
    formation_id = toggle_details[2]
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req_data = {
            "quantity": 1 if toggle_id == 0 else 0,
            "size": d_size,
            "type": d_type,
        }
        req = httpx.patch(
            f"https://api.heroku.com/apps/{app_id}/formation/{formation_id}",
            headers=headers,
            json=req_data,
        )
    except:
        bot.edit_message_text(
            "Error toggling the app state. Try again.", chat_id, msg_id
        )
    else:
        if req.status_code == 200:
            m = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data=f"go back to app_{app_id}"
            )
            m.add(back_btn)
            m_status = {0: "ON ✅", 1: "OFF ❌"}
            bot.edit_message_text(
                f"Your app has been successfully turned <b>{m_status[toggle_id]}.</b>",
                chat_id,
                msg_id,
                reply_markup=m,
                parse_mode="HTML",
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
                "Error toggling the app state. Try again.", chat_id, msg_id
            )
