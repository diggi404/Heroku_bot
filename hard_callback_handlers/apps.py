from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from database.models import HerokuTokens
from sqlalchemy.orm import Session
from datetime import datetime


def apps(
    bot: TeleBot,
    chat_id: int,
    db_session: Session,
    active_dict: dict,
    apps_page_dict: dict,
):
    current_session = str()
    if chat_id not in active_dict:
        get_tokens = (
            db_session.query(HerokuTokens).filter(HerokuTokens.user_id == chat_id).all()
        )
        if len(get_tokens) == 1:
            new_msg = bot.send_message(chat_id, "Fetching apps...")
            for details in get_tokens:
                active_dict[chat_id] = details.token
                current_session = details.email
                break
            try:
                headers = {
                    "Accept": "application/vnd.heroku+json; version=3",
                    "Authorization": f"Bearer {active_dict[chat_id]}",
                }
                apps_req = httpx.get("https://api.heroku.com/apps", headers=headers)
            except:
                bot.edit_message_text(
                    "Error fetching your apps. Try again.", chat_id, new_msg.id
                )
            else:
                if apps_req.status_code == 200:
                    if len(apps_req.json()) == 0:
                        m = types.InlineKeyboardMarkup()
                        b = types.InlineKeyboardButton(
                            "Create App ➕", callback_data="create heroku app"
                        )
                        m.add(b)
                        bot.edit_message_text(
                            "You have no apps. Use the button below to create one.",
                            chat_id,
                            new_msg.id,
                            reply_markup=m,
                        )
                    else:
                        temp_markups = []
                        markup = types.InlineKeyboardMarkup()
                        for index, app in enumerate(apps_req.json(), start=1):
                            if index <= 5:
                                btn = types.InlineKeyboardButton(
                                    f"{app['name']}", callback_data=f"app_{app['id']}"
                                )
                                temp_markups.append(btn)
                            else:
                                break
                        for m in temp_markups:
                            markup.add(m)
                        left_btn = types.InlineKeyboardButton(
                            "<", callback_data=f"move back apps:{current_session}"
                        )
                        page_btn = types.InlineKeyboardButton(
                            "1", callback_data="nothing"
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
                        apps_page_dict[chat_id] = 1
                        bot.edit_message_text(
                            f"➖➖➖➖HEROKU APPS ({len(apps_req.json())})➖➖➖➖\n\n",
                            chat_id,
                            new_msg.id,
                            reply_markup=markup,
                            parse_mode="HTML",
                        )
                elif apps_req.status_code == 401:
                    bot.edit_message_text(
                        "Your Oauth token is invalid. Use the button below to reactivate.",
                        chat_id,
                        new_msg.id,
                        reply_markup=hard_buttons.au_markup,
                    )
                else:
                    bot.edit_message_text(
                        "Error fetching your apps. Try again.", chat_id, new_msg.id
                    )
        else:
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for index, user in enumerate(get_tokens, start=1):
                btn = types.InlineKeyboardButton(
                    f"{user.email}", callback_data=f"acc {user.email}"
                )
                temp_markups.append(btn)
            for m in temp_markups:
                markup.add(m)
            bot.send_message(
                chat_id,
                "You have no active session. Kindly select an account to proceed.",
                reply_markup=markup,
            )
    else:
        new_msg = bot.send_message(chat_id, "Fetching apps...")
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        get_mail = (
            db_session.query(HerokuTokens.email)
            .filter(HerokuTokens.token == active_dict[chat_id])
            .first()
        )
        current_session = get_mail[0]
        try:
            apps_req = httpx.get("https://api.heroku.com/apps", headers=headers)
        except:
            bot.edit_message_text(
                "Error fetching your apps. Try again.", chat_id, new_msg.id
            )
        else:
            if apps_req.status_code == 200:
                if len(apps_req.json()) == 0:
                    m = types.InlineKeyboardMarkup()
                    b = types.InlineKeyboardButton(
                        "Create App ➕", callback_data="create heroku app"
                    )
                    m.add(b)
                    bot.edit_message_text(
                        "You have no apps. Use the button below to create one.",
                        chat_id,
                        new_msg.id,
                        reply_markup=m,
                    )
                else:
                    temp_markups = []
                    markup = types.InlineKeyboardMarkup()
                    for index, app in enumerate(apps_req.json(), start=1):
                        if index <= 5:
                            btn = types.InlineKeyboardButton(
                                f"{app['name']}", callback_data=f"app_{app['id']}"
                            )
                            temp_markups.append(btn)
                        else:
                            break
                    for m in temp_markups:
                        markup.add(m)
                    left_btn = types.InlineKeyboardButton(
                        "<", callback_data=f"move back apps:{current_session}"
                    )
                    page_btn = types.InlineKeyboardButton("1", callback_data="nothing")
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
                    apps_page_dict[chat_id] = 1
                    bot.edit_message_text(
                        f"➖➖➖➖HEROKU APPS ({len(apps_req.json())})➖➖➖➖\n\n",
                        chat_id,
                        new_msg.id,
                        reply_markup=markup,
                        parse_mode="HTML",
                    )
            elif apps_req.status_code == 401:
                bot.edit_message_text(
                    "Your Oauth token is invalid. Use the button below to reactivate.",
                    chat_id,
                    new_msg.id,
                )
            else:
                bot.edit_message_text(
                    "Error fetching your apps. Try again.", chat_id, new_msg.id
                )
