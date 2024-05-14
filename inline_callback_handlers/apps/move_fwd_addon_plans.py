from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from decimal import Decimal


def move_fwd_addon_plans(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    addons_page_dict: dict,
    addon_app_id_dict: dict,
    app_details_dict: dict,
):
    addon_id = button_data.split("_")[1]
    page_num = addons_page_dict.get(chat_id)
    if page_num is None:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    if chat_id not in active_dict or chat_id not in app_details_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://api.heroku.com/addon-services/{addon_id}/plans",
            headers=headers,
        )
    except:
        bot.edit_message_text("Error fetching addons. Try again.", chat_id, msg_id)
    else:
        if req.status_code == 200:
            plans_info = req.json()
            current_page = page_num + 1
            if ((current_page * 10) - len(plans_info)) >= 10:
                return
            addons_page_dict[chat_id] = current_page
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for index, plan in enumerate(plans_info, start=1):
                if (current_page * 10) - 10 < index <= (current_page * 10):
                    btn = types.InlineKeyboardButton(
                        f"{plan['human_name']} - ${(plan['price']['cents'] / Decimal('100.00')).quantize(Decimal('0.00'))}/month",
                        callback_data=f"app addon plan_{plan['id']}",
                    )
                    temp_markups.append(btn)

            for m in temp_markups:
                markup.add(m)
            left_btn = types.InlineKeyboardButton(
                "<", callback_data=f"move b addon plans_{addon_id}"
            )
            page_btn = types.InlineKeyboardButton(
                f"{current_page}", callback_data="nothing"
            )
            right_btn = types.InlineKeyboardButton(
                ">", callback_data=f"move f addon plans_{addon_id}"
            )
            markup.add(left_btn, page_btn, right_btn)
            back_btn = types.InlineKeyboardButton(
                "<< Back",
                callback_data=f"go back to addons_{addon_app_id_dict[chat_id]}",
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(back_btn)
            markup.add(close_btn)
            bot.edit_message_text(
                f"➖➖➖➖ADDON PLANS➖➖➖➖\n\nApp Name: <b>{app_details_dict[chat_id]}</b>\nAddon Name: <b>{app_details_dict[addon_id]}</b>\n\nSelect a plan to proceed or use the arrows to nagivate.",
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
                "Error fetching addon plans. Try again.", chat_id, msg_id
            )
