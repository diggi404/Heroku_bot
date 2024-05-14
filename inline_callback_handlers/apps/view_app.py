from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def view_app(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    app_toggle_dict: dict,
    app_details_dict: dict,
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
        app_req = httpx.get(
            f"https://api.heroku.com/teams/apps/{app_id}", headers=headers
        )
        stat_req = httpx.get(
            f"https://api.heroku.com/apps/{app_id}/formation", headers=headers
        )
    except:
        bot.edit_message_text(
            "Error fetching the app info. Try again.", chat_id, msg_id
        )
    else:
        if app_req.status_code == 200 and stat_req.status_code == 200:
            m_status = {1: "ON ✅", 0: "OFF ❌"}
            app_info = app_req.json()
            result_msg = f"""
➖➖{app_info['name'].upper()}➖➖

Web URL: <a href='{app_info['web_url']}'>click here</a>
State: <b>{m_status[stat_req.json()[0]['quantity']] if len(stat_req.json()) > 0 else 'Not Configured'}</b>
Dyno Type: <b>{stat_req.json()[0]['size'].upper() if len(stat_req.json()) > 0 else 'Not Configured'}</b>
Region: <b>{app_info['region']['name'].upper()}</b>
Created On: <b>{app_info['released_at']}</b>
Last Updated: <b>{app_info['updated_at']}</b>
➖➖➖➖➖➖➖➖➖➖➖➖
            """
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(
                "Deploy", callback_data=f"deploy_{app_id}"
            )
            btn2 = types.InlineKeyboardButton(
                "Show Addons", callback_data=f"app addons_{app_id}"
            )
            btn3 = types.InlineKeyboardButton(
                "Show Releases", callback_data=f"app releases_{app_id}"
            )
            btn4 = types.InlineKeyboardButton(
                "Config Vars", callback_data=f"configs_{app_id}"
            )
            btn5 = types.InlineKeyboardButton(
                "View Logs", callback_data=f"logs_{app_info['name']}"
            )
            btn7 = types.InlineKeyboardButton(
                "Delete App", callback_data=f"del app_{app_id}"
            )
            back_btn = types.InlineKeyboardButton(
                "<< Back", callback_data="go back to app list"
            )
            close_btn = types.InlineKeyboardButton(
                "Close \u274C", callback_data="cancel menu"
            )
            markup.add(btn1)
            markup.add(btn5, btn4)
            markup.add(btn2, btn3)
            if len(stat_req.json()) > 0:
                app_toggle_dict[chat_id] = [stat_req.json()[0]["type"]]
                app_toggle_dict[chat_id].append(stat_req.json()[0]["size"])
                app_toggle_dict[chat_id].append(stat_req.json()[0]["id"])
                btn6 = types.InlineKeyboardButton(
                    f"Turn {'ON' if stat_req.json()[0]['quantity'] == 0 else 'OFF'}",
                    callback_data=f"turn_{stat_req.json()[0]['quantity']}_{app_id}",
                )
                markup.add(btn6, btn7)
            else:
                markup.add(btn7)
            markup.add(back_btn)
            markup.add(close_btn)
            bot.edit_message_text(
                result_msg, chat_id, msg_id, reply_markup=markup, parse_mode="HTML"
            )
            app_details_dict[chat_id] = app_info["name"]
        elif app_req.status_code == 401:
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
