from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def move_fwd_apps(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    apps_page_dict: dict,
    active_dict: dict,
    button_data: str,
):
    current_session = button_data.split(":")[1]
    page_num = apps_page_dict.get(chat_id)
    if page_num is None:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        apps_req = httpx.get("https://api.heroku.com/apps", headers=headers)
    except:
        bot.edit_message_text("Error fetching your apps. Try again.", chat_id, msg_id)
    else:
        if apps_req.status_code == 200:
            current_page = page_num + 1
            if ((current_page * 5) - len(apps_req.json())) >= 5:
                return
            apps_page_dict[chat_id] = current_page
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for index, app in enumerate(apps_req.json(), start=1):
                if (current_page * 5) - 5 < index <= (current_page * 5):
                    btn = types.InlineKeyboardButton(
                        f"{app['name']}", callback_data=f"app_{app['id']}"
                    )
                    temp_markups.append(btn)

            for m in temp_markups:
                markup.add(m)
            left_btn = types.InlineKeyboardButton(
                "<", callback_data=f"move back apps:{current_session}"
            )
            page_btn = types.InlineKeyboardButton(
                f"{current_page}", callback_data="nothing"
            )
            right_btn = types.InlineKeyboardButton(
                ">", callback_data=f"move fwd apps:{current_session}"
            )
            markup.add(left_btn, page_btn, right_btn)
            c_btn = types.InlineKeyboardButton(
                "Create App ➕", callback_data="create new app"
            )
            markup.add(c_btn)
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(close_btn)
            bot.edit_message_text(
                f"➖➖➖➖HEROKU APPS({len(apps_req.json())})➖➖➖➖\n\n",
                chat_id,
                msg_id,
                reply_markup=markup,
                parse_mode="HTML",
            )
        elif apps_req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                msg_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error fetching your apps. Try again.", chat_id, msg_id
            )
