import sqlite3
import requests
import json
from telegram import (
    Update,
    ForceReply,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)

API_TOKEN = "5944951221:AAGCvhtcYWGsyxqhbYmaDuO-4A7vD_J-738"

# Define states of the conversation
FUll_NAME, SUMMARY = range(1, 3)

# Define function to start the bot
facilities = {
    "XF": "Xorijiy filologiya ",
    "TF": "Tabiiy fanlar",
    "IG": "Ijtimoiy gumanitar",
    "AFT": "Aniq fanlar (texnika)",
    "AFI": "Aniq fanlar (iqtisod)",
}

button_enter_text = "Litseyga ro'yxatdan o'tish"
button_list_text = "O'quvchilar haqida ma'lumot"


def start_bot(update: Update, context: CallbackContext):
    print("run start_bot")

    # Define the two buttons
    button_enter = KeyboardButton(text=button_enter_text)
    button_list = KeyboardButton(text=button_list_text)

    # Create the keyboard markup with the buttons
    keyboard = ReplyKeyboardMarkup(
        [[button_enter], [button_list]], resize_keyboard=True
    )

    # Send a message with the keyboard markup
    if update.message:
        update.message.reply_text("Menyuni tanlang", reply_markup=keyboard)
    else:
        if update.callback_query.data == "done":
            register(update, context)
            return
        if update.callback_query.data in ("XF", "TF", "IG", "AFT", "AFI"):
            get_option(update, context, update.callback_query.data)
            return
        update.callback_query.message.reply_text("Bosh menu", reply_markup=keyboard)


def start(update: Update, context: CallbackContext) -> int:
    print("run start")
    # Define the keyboard layout
    keyboard = [
        [InlineKeyboardButton(facilities["XF"], callback_data="XF")],
        [InlineKeyboardButton(facilities["TF"], callback_data="TF")],
        [InlineKeyboardButton(facilities["IG"], callback_data="IG")],
        [InlineKeyboardButton(facilities["AFT"], callback_data="AFT")],
        [InlineKeyboardButton(facilities["AFT"], callback_data="AFI")],
        [InlineKeyboardButton("Bosh menyuga qaytish", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message and ask the user to choose an option
    message = "Yo'nalishni tanlang:"
    a = update.message.reply_text(".", reply_markup=ReplyKeyboardRemove())
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=a.message_id)

    update.message.reply_text(message, reply_markup=reply_markup)


# Define function to handle user's chosen option
def get_option(update: Update, context: CallbackContext, option="") -> int:
    # Get the user's chosen option
    print("I ran")
    query = update.callback_query
    if query:
        query.answer
        query.answer()
        option = query.data
    # Check if the user chose to not do anything

    if option == "back":
        cancel(update, context)
        return ConversationHandler.END

    if option == "done":
        register(update, context)

    message = "Ism va familiyangizni kiriting"
    query.answer()
    query.message.reply_text(text=message, reply_markup=ForceReply(selective=True))

    # Set the next state to get the user's faculty name
    context.user_data["option"] = option
    return FUll_NAME


# Define function to handle user's full name


def get_fullname(update: Update, context: CallbackContext) -> int:
    # Get the user's full name
    fullname = update.message.text

    message = "Tuman va maktab nomi. Misol uchun 'Andijion , 35-DIM'. (Iltimos vergul qo'yishni unutmang)"
    update.message.reply_text(message, reply_markup=ForceReply(selective=True))
    context.user_data["fullname"] = fullname
    return SUMMARY


def summary(update: Update, context: CallbackContext) -> int:
    # Get the user's group name
    city_school = update.message.text
    data = context.user_data
    faculty = data["option"]
    fullname = data["fullname"]
    try:
        city = city_school.split(",")[0]
        school = city_school.split(",")[1]
    except:
        return SUMMARY
    message = f"""Siz quyidagi ma'lumotlar bilan ro'yxatdan o'tmoqchisiz:
Ismi va familiyangiz: {fullname}
Tuman: {city}
Maktab: {school}
Yo'nalish: {facilities[faculty]}
    """
    keyboard = [
        [
            InlineKeyboardButton("Tasdiqlash", callback_data="done"),
            InlineKeyboardButton("Bekor qilish", callback_data="cancel_all"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=markup)

    context.user_data["city"] = city
    context.user_data["school"] = school

    # End the conversation
    return SUMMARY

    # Define function to summarize user input and write to database


def register(update: Update, context: CallbackContext) -> None:
    # from main.models import BasicUser, User
    import requests

    data = context.user_data
    json_data = {
        "data": {
            "full_name": data["fullname"],
            "city": data["city"].strip(),
            "school": data["school"].strip(),
            "faculty": data["option"],
        }
    }
    response = requests.post("http://127.0.0.1:8000/main/api/register", json=json_data)
    response_json = response.json()
    message = f"""Ro'yxatdan muvvaffaqiyatli o'tdingiz! Testni quyidagi havolani ochish orqali boshlashingiz mumkin. http://127.0.0.1:8000/main/api/login/{response_json['student']['uuid']}
    """
    update.callback_query.message.reply_text(message)


# Define function to handle cancelling the conversation
def cancel(update: Update, context: CallbackContext) -> int:
    # Get the user's chat ID and message ID
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    message_id = query.message.message_id
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    start_bot(update, context)
    # Delete the message that triggered the conversation

    # End the conversation
    return ConversationHandler.END


class User:
    def __init__(self, id, full_name, faculty, group_name):
        self.id = id
        self.full_name = full_name
        self.faculty = faculty
        self.group_name = group_name


# def get_stats(update: Update, context: CallbackContext, option: str) -> None:
#     con = sqlite3.connect("users.db")
#     cursor = con.cursor()
#     databases = ["first", "second", "third"]
#     a = []
#     for i in databases:
#         cursor.execute(f"SELECT * FROM {i}_group_users")
#         rows = cursor.fetchall()
#         a.append([User(*row) for row in rows])

#     message = ""
#     if option == "fc1":
#         message += facilities[0] + "+\n"
#         for i in a[0]:
#             message += f"{i.id}. {i.full_name} - {i.faculty} - {i.group_name}\n"
#     elif option == "fc2":
#         message += facilities[1] + "+\n"
#         for i in a[1]:
#             message += f"{i.id}. {i.full_name} - {i.faculty} - {i.group_name}\n"

#     elif option == "fc3":
#         message += facilities[2] + "+\n"
#         for i in a[2]:
#             message += f"{i.id}. {i.full_name} - {i.faculty} - {i.group_name}\n"
#     context.bot.send_message(
#         chat_id=update.callback_query.message.chat_id, text=message
#     )


updater = Updater(token=API_TOKEN)


def main() -> None:
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_option)],
        states={
            FUll_NAME: [MessageHandler(Filters.text & ~Filters.command, get_fullname)],
            SUMMARY: [MessageHandler(Filters.text & ~Filters.command, summary)],
        },
        fallbacks=[CallbackQueryHandler(cancel)],
    )
    enter_student_handler = MessageHandler(
        Filters.regex(f"^{button_enter_text}$"), start
    )
    dispatcher.add_handler(CommandHandler("start", start_bot))
    dispatcher.add_handler(CommandHandler("add", start))
    dispatcher.add_handler(enter_student_handler)
    dispatcher.add_handler(conv_handler)
    updater.start_polling()


main()
