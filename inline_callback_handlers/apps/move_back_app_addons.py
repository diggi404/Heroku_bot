from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def move_back_app_addons(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    addons_page_dict: dict,
    addon_app_id_dict: dict,
    app_details_dict: dict,
):
    app_id = button_data.split("_")[1]
    page_num = addons_page_dict.get(chat_id)
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
            f"https://api.heroku.com/apps/{app_id}/addons",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error fetching app addons. Try again.",
            chat_id,
            msg_id,
        )
    else:
        if req.status_code == 200:
            addons = req.json()
            current_page = page_num - 1
            addons_page_dict[chat_id] = current_page
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for index, addon in enumerate(addons, start=1):
                if (current_page * 5) - 5 < index <= (current_page * 5):
                    btn = types.InlineKeyboardButton(
                        f"{addon['plan']['description']}",
                        callback_data=f"app addon_{addon['id']}",
                    )
                    temp_markups.append(btn)
                    app_details_dict[addon["id"]] = addon["addon_service"]["id"]

            for m in temp_markups:
                markup.add(m)
            left_btn = types.InlineKeyboardButton(
                "<", callback_data=f"move b addons_{app_id}"
            )
            page_btn = types.InlineKeyboardButton(
                f"{current_page}", callback_data="nothing"
            )
            right_btn = types.InlineKeyboardButton(
                ">", callback_data=f"move f addons_{app_id}"
            )
            markup.add(left_btn, page_btn, right_btn)
            c_btn = types.InlineKeyboardButton(
                "Create Addon ➕", callback_data=f"new addon_{app_id}"
            )
            markup.add(c_btn)
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data=f"go back to app_{app_id}"
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(back_btn)
            markup.add(close_btn)
            addon_app_id_dict[chat_id] = app_id
            bot.edit_message_text(
                f"➖➖➖➖APP ADDONS➖➖➖➖\n\nTotal: <b>{len(addons)}</b>",
                chat_id,
                msg_id,
                reply_markup=markup,
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
                "Error fetching app addons. Try again.",
                chat_id,
                msg_id,
            )
