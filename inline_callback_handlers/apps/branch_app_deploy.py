from telebot import TeleBot, types
import httpx
from keyboards import hard_buttons


def branch_app_deploy(
    bot: TeleBot, chat_id: int, msg_id: int, button_data: str, active_dict: dict
):
    branch_name = button_data.split(":")[1]
    app_id = button_data.split(":")[2]
    if chat_id not in active_dict:
        bot.edit_message_text("Kindly refetch your apps.", chat_id, msg_id)
        return
    try:
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {active_dict[chat_id]}",
        }
        req_data = {"branch": f"{branch_name}"}
        req = httpx.post(
            f"https://kolkrabbi.heroku.com/apps/{app_id}/github/push",
            json=req_data,
            headers=headers,
        )
    except:
        bot.edit_message_text(
            "Error deploying branch. Try again.",
            chat_id,
            msg_id,
        )
    else:
        if req.status_code == 202:
            output_log = req.json()["build"]["output_stream_url"]
            result_msg = f"""
➖➖➖➖APP DEPLOYMENT➖➖➖➖

Deployed Branch: <b>{branch_name}</b>
Status: PENDING 🔄
            """
            with httpx.stream("GET", output_log, timeout=60) as res:
                result = list()
                for line in res.iter_lines():
                    result.append(line)
                    j = "\n".join(result)
                    if len(result) > 10:
                        result = result[-10:]
                        j = "\n".join(result)

                    if "Released" in line:
                        m = types.InlineKeyboardMarkup()
                        b = types.InlineKeyboardButton(
                            "View App", callback_data=f"app_{app_id}"
                        )
                        m.add(b)
                        result_msg = f"""
➖➖➖➖APP DEPLOYMENT➖➖➖➖

Deployed Branch: <b>{branch_name}</b>
Status: DEPLOYED ✅
            """
                        bot.edit_message_text(
                            f"{result_msg}<pre>{j}</pre>",
                            chat_id,
                            msg_id,
                            parse_mode="HTML",
                            reply_markup=m,
                        )
                        return
                    bot.edit_message_text(
                        f"{result_msg}<pre>{j}</pre>",
                        chat_id,
                        msg_id,
                        parse_mode="HTML",
                    )
        elif req.status_code == 401:
            bot.edit_message_text(
                "Your Oauth token is invalid. Use the button below to reactivate.",
                chat_id,
                msg_id,
                reply_markup=hard_buttons.au_markup,
            )
        else:
            bot.edit_message_text(
                "Error deploying branch. Try again.",
                chat_id,
                msg_id,
            )
