from telebot import TeleBot, types


def choose_region(bot: TeleBot, chat_id: int, msg_id: int, active_dict: dict):
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly restart the process.", chat_id, msg_id)
        return
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Europe 🇪🇺", callback_data="region eu")
    btn2 = types.InlineKeyboardButton("United States 🇺🇸", callback_data="region us")
    close_btn = types.InlineKeyboardButton("Close \u274C", callback_data="cancel menu")
    markup.add(btn2)
    markup.add(btn1)
    markup.add(close_btn)
    bot.edit_message_text(
        "➖➖➖➖APP REGIONS➖➖➖➖\n\nKindly choose the region for your new app.",
        chat_id,
        msg_id,
        reply_markup=markup,
    )
