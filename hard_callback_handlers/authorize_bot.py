from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from database.models import HerokuTokens
from sqlalchemy.orm import Session
from datetime import datetime


def authorize_bot(bot: TeleBot, chat_id: int, db_session: Session, active_dict: dict):
    take_key = bot.send_message(
        chat_id,
        "Send your Heroku Oauth token: ",
        reply_markup=hard_buttons.canc_sending_markup,
    )
    bot.register_next_step_handler(
        take_key,
        lambda message: step_authorize_bot(message, bot, db_session, active_dict),
    )


def step_authorize_bot(
    message: types.Message, bot: TeleBot, db_session: Session, active_dict: dict
):
    chat_id = message.from_user.id
    oauth = message.text
    if oauth == "Cancel Sending ❌":
        bot.send_message(
            chat_id, "Authorization canceled.", reply_markup=hard_buttons.au_markup
        )
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {oauth}",
        }
        check_req = httpx.get("https://api.heroku.com/account", headers=headers)
    except:
        bot.send_message(
            chat_id,
            "Error checking your Oauth token. Try again later.",
            reply_markup=hard_buttons.au_markup,
        )
    else:
        if check_req.status_code == 200:
            with db_session as session:
                try:
                    email = check_req.json()["email"]
                    name = check_req.json()["name"]
                    new_rec = HerokuTokens(
                        user_id=chat_id,
                        name=name,
                        email=email,
                        token=oauth,
                        updated_at=datetime.utcnow(),
                    )
                    session.add(new_rec)
                    session.commit()
                except Exception as e:
                    print(e)
                    bot.send_message(
                        chat_id,
                        "Error saving your token. Kindly use the button below to try again.",
                        reply_markup=hard_buttons.au_markup,
                    )
                else:
                    bot.send_message(
                        chat_id,
                        f"Your account has been added ✅\n\nName: <b>{name}</b>\nEmail: <code>{email}</code>\n\nUse the buttons below to navigate your account.",
                        parse_mode="HTML",
                        reply_markup=hard_buttons.main_markup,
                    )
                    active_dict[chat_id] = oauth
        elif check_req.status_code == 401:
            bot.send_message(
                chat_id,
                "Your Oauth token is invalid.",
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.send_message(
                chat_id,
                "Error validating your token. Try again.",
                reply_markup=hard_buttons.au_markup,
            )
