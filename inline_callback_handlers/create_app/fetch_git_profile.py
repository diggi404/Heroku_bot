from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def fetch_git_profile(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    active_dict: dict,
    button_data: str,
    git_details_dict: dict,
):
    app_id = button_data.split("_")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    new_msg = bot.edit_message_text("Fetching git profile...", chat_id, msg_id)
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://kolkrabbi.heroku.com/github/user",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error fetching your git info.", chat_id, new_msg.message_id
        )
    else:
        if req.status_code == 200:
            git_username = req.json()["login"]
            git_details_dict[chat_id] = [git_username]
            take_repo = bot.edit_message_text(
                "Profile fetch successful ✅.\n\n<b>Send the name of the repository you want to link:</b>",
                chat_id,
                new_msg.message_id,
                parse_mode="HTML",
            )
            bot.register_next_step_handler(
                take_repo,
                lambda message: step_fetch_profile(
                    message, bot, git_username, app_id, active_dict, git_details_dict
                ),
            )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                new_msg.message_id,
                reply_markup=hard_buttons.au_markup,
            )
        elif req.status_code == 404:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton("View App", callback_data=f"app_{app_id}")
            m.add(b)
            bot.edit_message_text(
                "No Github account is linked to your account yet. Login and configure one before you can configure repositories for apps.",
                chat_id,
                new_msg.message_id,
                reply_markup=m,
            )
        else:
            bot.edit_message_text(
                "Error fetching git profile.", chat_id, new_msg.message_id
            )


def step_fetch_profile(
    message: types.Message,
    bot: TeleBot,
    git_username: str,
    app_id: str,
    active_dict: dict,
    git_details_dict: dict,
):
    chat_id = message.from_user.id
    new_msg = bot.send_message(chat_id, "searching repository...")
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3.repositories-api",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://kolkrabbi.heroku.com/github/search/repositories?q=fork%3Atrue%20user%3A{git_username}%20{message.text.strip()}",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error searcing repository. Try again.", chat_id, new_msg.message_id
        )
    else:
        if req.status_code == 200:
            if req.json()["total_count"] == 0:
                m = types.InlineKeyboardMarkup()
                b = types.InlineKeyboardButton(
                    "View App", callback_data=f"app_{app_id}"
                )
                m.add(b)
                bot.edit_message_text(
                    "No such repository exists on your Github profile.",
                    chat_id,
                    new_msg.message_id,
                    reply_markup=m,
                )
                return
            git_details_dict[chat_id].append(message.text.strip())
            m = types.InlineKeyboardMarkup()
            b1 = types.InlineKeyboardButton("✅", callback_data=f"repo_{app_id}")
            b2 = types.InlineKeyboardButton("❌", callback_data=f"no git_{app_id}")
            m.add(b1, b2)
            bot.edit_message_text(
                "Repository found ✅. Do you want to connect this repository now?",
                chat_id,
                new_msg.message_id,
                reply_markup=m,
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
                "Error searcing repository. Try again.", chat_id, new_msg.message_id
            )
