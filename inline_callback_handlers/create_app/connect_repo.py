from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def connect_repo(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    active_dict: dict,
    button_data: str,
    git_details_dict: dict,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict or chat_id not in git_details_dict:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    git_details = git_details_dict.get(chat_id, [])
    git_username = git_details[0]
    git_repo = git_details[1]
    new_msg = bot.edit_message_text("Connecting repository...", chat_id, msg_id)
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req_data = {"repo": f"{git_username}/{git_repo}"}
        req = httpx.post(
            f"https://kolkrabbi.heroku.com/apps/{app_id}/github",
            headers=headers,
            json=req_data,
        )
    except:
        bot.edit_message_text("Error connecting repo.", chat_id, new_msg.message_id)
    else:
        if req.status_code == 201:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
            m.add(b)
            bot.edit_message_text(
                "Your repository has been connected ✅. You can use the button below to view and manage the app.",
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
            bot.edit_message_text("Error connecting repo.", chat_id, new_msg.message_id)
