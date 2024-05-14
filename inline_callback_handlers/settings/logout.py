from telebot import TeleBot, types


def logout(bot: TeleBot, chat_id: int, msg_id: int, active_dict: dict):
    if chat_id in active_dict:
        del active_dict[chat_id]
    bot.delete_message(chat_id, msg_id)
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b = types.KeyboardButton("Login 🔓")
    m.row(b)
    bot.send_message(chat_id, "You have been logged out.", reply_markup=m)
