from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def app_name(
    bot: TeleBot, chat_id: int, msg_id: int, active_dict: dict, button_data: str
):
    region = button_data.split(" ")[1]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    regs = {"us": "United States 🇺🇸", "eu": "Europe 🇪🇺"}
    take_name = bot.edit_message_text(
        f"You selected {regs[region]} region.\n\nNow send the name of your app <b>[must be unique]</b>:",
        chat_id,
        msg_id,
        parse_mode="HTML",
    )
    bot.register_next_step_handler(
        take_name, lambda message: step_app_name(message, bot, active_dict, region)
    )


def step_app_name(message: types.Message, bot: TeleBot, active_dict: dict, region: str):
    chat_id = message.from_user.id
    new_msg = bot.send_message(chat_id, "validing name...")
    new_app_name = message.text.lower().strip()
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req = httpx.get(
            f"https://api.heroku.com/apps/{new_app_name}",
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error checking app name. Try again.", chat_id, new_msg.message_id
        )
    else:
        if req.status_code == 404:
            msg = bot.edit_message_text(
                "Name accepted ✅. Creating app...", chat_id, new_msg.message_id
            )
            try:
                headers = {
                    "Accept": "application/vnd.heroku+json; version=3.process-tier",
                    "Authorization": f"Bearer {active_dict[chat_id]}",
                }
                req_data = {"region": region, "name": new_app_name}
                req = httpx.post(
                    f"https://api.heroku.com/teams/apps", headers=headers, json=req_data
                )
            except:
                bot.edit_message_text(
                    "Error creating app. Try again.", chat_id, new_msg.message_id
                )
            else:
                if req.status_code == 201:
                    bot.edit_message_text(
                        "Your app has been successfully created ✅.",
                        chat_id,
                        msg.message_id,
                    )
                    app_id = req.json()["id"]
                    m = types.InlineKeyboardMarkup()
                    b1 = types.InlineKeyboardButton("✅", callback_data=f"git_{app_id}")
                    b2 = types.InlineKeyboardButton(
                        "❌", callback_data=f"no git_{app_id}"
                    )
                    m.add(b1, b2)
                    bot.send_message(
                        chat_id,
                        "Do you want to configure Github repository for this app?",
                        reply_markup=m,
                    )
                elif req.status_code == 401:
                    bot.edit_message_text(
                        "Your Oauth token is invalid. Use the button below to reactivate.",
                        chat_id,
                        msg.message_id,
                        reply_markup=hard_buttons.au_markup,
                    )
                else:
                    bot.edit_message_text(
                        "Error creating app. Try again.",
                        chat_id,
                        msg.message_id,
                    )
        elif req.status_code == 200:
            m = types.InlineKeyboardMarkup()
            b = types.InlineKeyboardButton(
                "Create App ➕", callback_data="create new app"
            )
            m.add(b)
            bot.edit_message_text(
                "An app already exist with same name. Kindly restart the process.",
                chat_id,
                new_msg.message_id,
                reply_markup=m,
            )
        else:
            bot.edit_message_text(
                "Error checking app name. Try again.", chat_id, new_msg.message_id
            )
