from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
import time
from threading import Thread


def view_logs(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    logs_dict: dict,
):
    app_name = button_data.split("_")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        data = {"lines": 10, "tail": "true"}
        req = httpx.post(
            f"https://api.heroku.com/apps/{app_name}/log-sessions",
            headers=headers,
            json=data,
        )
    except:
        bot.edit_message_text(
            "Error fetching the app logs. Try again.", chat_id, msg_id
        )
    else:
        if req.status_code == 201:
            log_url = req.json()["logplex_url"]
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton(
                "Terminate 🔴", callback_data=f"end logs_{msg_id}"
            )
            m.add(b)
            msg_str = f"➖➖{app_name.upper()}➖➖\n\n"
            thread = Thread(
                target=log_trail,
                args=(bot, logs_dict, log_url, m, chat_id, msg_id, msg_str),
            )
            thread.start()
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                msg_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error fetching the app logs. Try again.", chat_id, msg_id
            )


def log_trail(
    bot: TeleBot,
    logs_dict: dict,
    url: str,
    markup: types.InlineKeyboardMarkup,
    chat_id: int,
    msg_id: int,
    msg_str: str,
):
    with httpx.stream("GET", url, timeout=60) as res:
        result = list()
        for line in res.iter_lines():
            if logs_dict[msg_id]:
                result.append(line)
                j = "\n".join(result)
                if len(result) > 10:
                    result = result[-10:]
                    j = "\n".join(result)
                bot.edit_message_text(
                    f"{msg_str}<pre>{j}</pre>",
                    chat_id,
                    msg_id,
                    parse_mode="HTML",
                    reply_markup=markup,
                )
            else:
                break
