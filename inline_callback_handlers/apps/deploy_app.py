from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def deploy_app(
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
            f"https://kolkrabbi.heroku.com/apps/{app_id}/github/branches",
            headers=headers,
        )
        git_req = httpx.get("https://kolkrabbi.heroku.com/github/user", headers=headers)
    except:
        bot.edit_message_text(
            "Error fetching git repo branches. Try again.",
            chat_id,
            msg_id,
        )
    else:
        if req.status_code == 200 and git_req.status_code == 200:
            branches = req.json()
            temp_markups = []
            markup = types.InlineKeyboardMarkup()
            for b in branches:
                btn = types.InlineKeyboardButton(
                    f"{b}",
                    callback_data=f"branch:{b}:{app_id}",
                )
                temp_markups.append(btn)

            for m in temp_markups:
                markup.add(m)
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data=f"go back to app_{app_id}"
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(back_btn)
            markup.add(close_btn)
            bot.edit_message_text(
                "➖➖➖➖GIT BRANCHES➖➖➖➖\n\nSelect the branch to deploy.",
                chat_id,
                msg_id,
                reply_markup=markup,
            )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                msg_id,
                reply_markup=hard_buttons.au_markup,
            )
        elif git_req.status_code == 404:
            bot.answer_callback_query(
                call_id,
                "No Github account is linked to your account. Login and link one before proceeding.",
                show_alert=True,
            )
        elif req.status_code == 404:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton(
                "Configure Git", callback_data=f"git_{app_id}"
            )
            m.add(b)
            bot.edit_message_text(
                "No Github reposity exists on this app. Use the button below to link one.",
                chat_id,
                msg_id,
                reply_markup=m,
            )
        else:
            bot.edit_message_text(
                "Error fetching git repo branches. Try again.",
                chat_id,
                msg_id,
            )
