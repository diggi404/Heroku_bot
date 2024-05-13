from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def config_vars(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    call_id: int,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://api.heroku.com/apps/{app_id}/config-vars",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error fetching the app environment variables. Try again.", chat_id, msg_id
        )
    else:
        if req.status_code == 200:
            vars = dict(req.json())
            if not vars:
                bot.answer_callback_query(
                    call_id, "No environment variables found.", show_alert=True
                )
                return
            var_list = []
            for key, value in vars.items():
                var_list.append(
                    f"<b>{key}</b>: <span class='tg-spoiler'>{value}</span>"
                )
            result = (
                "➖➖ENVINRONMENT VARIABLES➖➖\n\n"
                + "\n\n".join(var_list)
                + "\n➖➖➖➖➖➖➖➖➖➖➖➖➖"
            )
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(
                "Edit", callback_data=f"edit var_{app_id}"
            )
            btn2 = types.InlineKeyboardButton("Add", callback_data=f"add var_{app_id}")
            btn3 = types.InlineKeyboardButton(
                "Delete", callback_data=f"del var_{app_id}"
            )
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data=f"go back to app_{app_id}"
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(btn2)
            markup.add(btn1, btn3)
            markup.add(back_btn)
            markup.add(close_btn)
            bot.edit_message_text(
                result, chat_id, msg_id, parse_mode="HTML", reply_markup=markup
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
                "Error fetching the app environment variables. Try again.",
                chat_id,
                msg_id,
            )
