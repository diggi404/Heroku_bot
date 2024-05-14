from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def move_back_app_create_addons(
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
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
    page_num = addons_page_dict.get(chat_id)
    if page_num == 1:
        return
    elif page_num is None:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://api.heroku.com/addon-services",
            headers=headers,
        )
    except:
        bot.edit_message_text("Error fetching addons. Try again.", chat_id, msg_id)
    else:
        if req.status_code == 200:
            addon_list = req.json()
            current_page = page_num - 1
            addons_page_dict[chat_id] = current_page
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for index, addon in enumerate(addon_list, start=1):
                if (current_page * 10) - 10 < index <= (current_page * 10):
                    btn = types.InlineKeyboardButton(
                        f"{addon['human_name']}",
                        callback_data=f"app addon create_{addon['id']}",
                    )
                    temp_markups.append(btn)
                    app_details_dict[addon["id"]] = addon["human_name"]

            for m in temp_markups:
                markup.add(m)
            left_btn = types.InlineKeyboardButton(
                "<", callback_data=f"move b whole addons_{app_id}"
            )
            page_btn = types.InlineKeyboardButton(
                f"{current_page}", callback_data="nothing"
            )
            right_btn = types.InlineKeyboardButton(
                ">", callback_data=f"move f whole addons_{app_id}"
            )
            markup.add(left_btn, page_btn, right_btn)
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
                f"➖➖➖➖ADDONS LIST➖➖➖➖\n\nApp Name: <b>{app_details_dict[chat_id]}</b> \n\nSelect an addon to proceed or use the arrows to nagivate.",
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
            bot.edit_message_text("Error fetching addons. Try again.", chat_id, msg_id)
