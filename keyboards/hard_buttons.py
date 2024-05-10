from telebot import types

main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Settings")
btn2 = types.KeyboardButton("Apps")
btn3 = types.KeyboardButton("Addons")
btn4 = types.KeyboardButton("Register New Account")
btn5 = types.KeyboardButton("Switch Account")
main_markup.row(btn2)
main_markup.row(btn3, btn1)
main_markup.row(btn5, btn4)


au_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
au_btn = types.KeyboardButton("Authorize Bot 🤖")
au_markup.row(au_btn)


canc_sending_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
canc_btn = types.KeyboardButton("Cancel Sending ❌")
canc_sending_markup.row(canc_btn)
