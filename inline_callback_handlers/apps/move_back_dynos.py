from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from decimal import Decimal


def move_back_dynos(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    dyno_page_dict: dict,
    dyno_app_id_dict: dict,
    app_details_dict: dict,
):
    app_id = button_data.split("_")[1]
    if (
        chat_id not in active_dict
        or chat_id not in app_details_dict
        or "main_dyno_info" not in app_details_dict
    ):
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    page_num = dyno_page_dict.get(chat_id)
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
            f"https://api.heroku.com/dyno-sizes",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error fetching dyno sizes. Try again.",
            chat_id,
            msg_id,
        )
    else:
        if req.status_code == 200:
            prev_dyno_type = app_details_dict["main_dyno_info"][0]
            prev_dyno_size = app_details_dict["main_dyno_info"][1]
            app_name = app_details_dict[chat_id]
            dynos = req.json()
            current_page = page_num - 1
            dyno_page_dict[chat_id] = current_page
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for index, dyno in enumerate(dynos, start=1):
                if (current_page * 10) - 10 < index <= (current_page * 10):
                    btn = types.InlineKeyboardButton(
                        f"{dyno['name'].upper()} - ${'N/A' if dyno['cost']['cents'] is None else (Decimal(dyno['cost']['cents']) / Decimal('100.00')).quantize(Decimal('0.00'))} / {'N/A' if dyno['cost']['unit'] is None else 'month'}",
                        callback_data=f"dyno info_{dyno['id']}",
                    )
                    temp_markups.append(btn)

            for m in temp_markups:
                markup.add(m)
            left_btn = types.InlineKeyboardButton(
                "<", callback_data=f"move b dynos_{app_id}"
            )
            page_btn = types.InlineKeyboardButton(
                f"{current_page}", callback_data="nothing"
            )
            right_btn = types.InlineKeyboardButton(
                ">", callback_data=f"move f dynos_{app_id}"
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
            dyno_app_id_dict[chat_id] = app_id
            bot.edit_message_text(
                f"➖➖➖➖DYNO SIZES➖➖➖➖\n\nApp Name: <b>{app_name}</b>\nCurrent Dyno Type: <b>{prev_dyno_type}</b>\nCurrent Dyno Size: <b>{prev_dyno_size.upper()}</b>",
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
                "Error fetching dyno sizes. Try again.",
                chat_id,
                msg_id,
            )
