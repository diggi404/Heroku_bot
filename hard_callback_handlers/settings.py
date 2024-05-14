from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def settings(bot: TeleBot, chat_id: int, active_dict: dict):
    if chat_id not in active_dict:
        m = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton(
            "Activate Session", url="https://t.me/jpqxbzp_heroku_bot?start="
        )
        m.add(b)
        bot.send_message(chat_id, "You have no active session.", reply_markup=m)
        return
    new_msg = bot.send_message(chat_id, "Gathering info...")
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        acc_req = httpx.get(
            f"https://api.heroku.com/account",
            headers=headers,
        )
        apps_req = httpx.get(
            f"https://api.heroku.com/apps",
            headers=headers,
        )
        addons_req = httpx.get(
            f"https://api.heroku.com/addons",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error gathering info. Try again.", chat_id, new_msg.message_id
        )
    else:
        if (
            acc_req.status_code == 200
            and apps_req.status_code == 200
            and addons_req.status_code == 200
        ):
            result_msg = f"""
➖➖➖ACCOUNT SETTINGS➖➖➖

Name: <b>{acc_req.json()['name']}</b>
Email: <code>{acc_req.json()['email']}</code>
Total Apps: <b>{len(apps_req.json())}</b>
Total Addons: <b>{len(addons_req.json())}</b>
➖➖➖➖➖➖➖➖➖➖➖➖➖
            """
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("Log Out", callback_data="logout")
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(btn1)
            markup.add(close_btn)
            bot.edit_message_text(
                result_msg,
                chat_id,
                new_msg.message_id,
                reply_markup=markup,
                parse_mode="HTML",
            )
        elif acc_req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                new_msg.message_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error gathering info. Try again.", chat_id, new_msg.message_id
            )
