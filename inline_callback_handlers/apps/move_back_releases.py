from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def move_back_releases(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    releases_page_dict: dict,
):
    app_id = button_data.split("_")[1]
    page_num = releases_page_dict.get(chat_id)
    if page_num == 1:
        return
    elif page_num is None:
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
        req = httpx.get(
            f"https://api.heroku.com/apps/{app_id}/releases", headers=headers
        )
    except:
        bot.edit_message_text(
            "Error fetching the app info. Try again.", chat_id, msg_id
        )
    else:
        if req.status_code == 200:
            app_name = str()
            releases = req.json()
            for r in releases:
                app_name = r["app"]["name"]
                break
            markup = types.InlineKeyboardMarkup()
            current_page = page_num - 1
            releases_page_dict[chat_id] = current_page
            r_list = [
                f"<b>{index}.</b> Description: <b>{r['description']}</b> | "
                f"Status: <b>{r['status']}</b> | "
                f"Version: <b>{r['version']}</b> | "
                f"Current: <b>{r['current']}</b> | "
                f"Date: <b>{r['created_at']}</b>"
                for index, r in enumerate(releases, start=1)
                if (current_page * 5) - 5 < index <= (current_page * 5)
            ]
            left_btn = types.InlineKeyboardButton(
                "<", callback_data=f"move back r_{app_id}"
            )
            page_btn = types.InlineKeyboardButton(
                f"{current_page}", callback_data="nothing"
            )
            right_btn = types.InlineKeyboardButton(
                ">", callback_data=f"move fwd r_{app_id}"
            )
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data=f"go back to app_{app_id}"
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(left_btn, page_btn, right_btn)
            markup.add(back_btn)
            markup.add(close_btn)
            bot.edit_message_text(
                f"➖➖➖➖APP RELEASES➖➖➖➖\n\nApp Name: <b>{app_name}</b>\n\n"
                + "\n\n".join(r_list)
                + "\n➖➖➖➖➖➖➖➖➖➖➖➖",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=markup,
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
                "Error fetching the app info. Try again.", chat_id, msg_id
            )
