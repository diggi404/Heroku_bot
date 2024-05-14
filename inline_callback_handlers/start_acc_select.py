from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons
from database.models import HerokuTokens
from sqlalchemy.orm import Session
from datetime import datetime


def start_acc_select(
    bot: TeleBot,
    chat_id: int,
    msg_id: int,
    db_session: Session,
    button_data: str,
    active_dict: dict,
):
    email = button_data.split(" ")[1]
    get_acc = db_session.query(HerokuTokens).filter(HerokuTokens.email == email).first()
    active_dict[chat_id] = get_acc.token
    bot.delete_message(chat_id, msg_id)
    bot.send_message(
        chat_id,
        f"<code>{email}</code> has been activated and ready for navigation.",
        parse_mode="HTML",
        reply_markup=hard_buttons.main_markup,
    )
