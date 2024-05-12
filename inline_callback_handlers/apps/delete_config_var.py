from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def delete_config_var(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    config_var_dict: dict,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    take_var = bot.send_message(
        chat_id,
        "Send your variable names like below 👇\n\n<i>var_name1</i>\n<i>var_name2</i>",
        parse_mode="HTML",
    )
    bot.register_next_step_handler(
        take_var,
        lambda message: step_delete_config_var(
            message, bot, app_id, config_var_dict, msg_id
        ),
    )


def step_delete_config_var(
    message: types.Message,
    bot: TeleBot,
    app_id: str,
    config_var_dict: dict,
    old_msg_id: int,
):
    chat_id = message.from_user.id
    try:
        var_names = message.text.splitlines()
    except:
        bot.send_message(chat_id, "Your entry is invalid.")
    else:
        var_names.append(old_msg_id)
        config_var_dict[chat_id] = var_names
        m = types.InlineKeyboardMarkup()
        b1 = types.InlineKeyboardButton("✅", callback_data=f"yes del var_{app_id}")
        b2 = types.InlineKeyboardButton("❌", callback_data=f"no var_{app_id}")
        m.add(b1, b2)
        bot.send_message(
            chat_id, "Confirm deleting these environment variables?", reply_markup=m
        )


def yes_del_config_var(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    button_data: str,
    active_dict: dict,
    config_var_dict: dict,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict or chat_id not in config_var_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    var_names = config_var_dict.get(chat_id, [])
    req_data = dict()
    for i in range(0, len(var_names) - 1, 1):
        key = var_names[i]
        value = None
        req_data[key] = value
    old_msg_id = var_names[-1]
    new_msg = bot.edit_message_text("deleting variables...", chat_id, msg_id)
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.patch(
            f"https://api.heroku.com/apps/{app_id}/config-vars",
            json=req_data,
            headers=headers,
        )
        name_req = httpx.get(
            f"https://api.heroku.com/teams/apps/{app_id}", headers=headers
        )
    except:
        bot.edit_message_text(
            "Error deleting your environment variables. Try again.",
            chat_id,
            new_msg.message_id,
        )
    else:
        if req.status_code == 200 and name_req.status_code == 200:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton(
                "View Configs", callback_data=f"configs_{app_id}"
            )
            m.add(b)
            bot.delete_message(chat_id, old_msg_id)
            bot.edit_message_text(
                f"Your environment variables have been successfully deleted✅ for the app <b>{name_req.json()['name']}</b>",
                chat_id,
                new_msg.message_id,
                reply_markup=m,
                parse_mode="HTML",
            )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                new_msg.message_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error deleting your environment variables. Try again.",
                chat_id,
                new_msg.message_id,
            )
