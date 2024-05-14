from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from database.models import HerokuTokens
from sqlalchemy.orm import Session
from datetime import datetime


def login(
    bot: TeleBot,
    chat_id: int,
    db_session: Session,
):
    check_user = (
        db_session.query(HerokuTokens).filter(HerokuTokens.user_id == chat_id).all()
    )
    temp_markups = []
    markup = types.InlineKeyboardMarkup()
    for user in check_user:
        btn = types.InlineKeyboardButton(
            f"{user.email}", callback_data=f"acc {user.email}"
        )
        temp_markups.append(btn)
    for m in temp_markups:
        markup.add(m)
    bot.send_message(
        chat_id,
        "Select an account to activate.",
        reply_markup=markup,
    )
