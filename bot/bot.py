import os
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton

from telegram.ext import(
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    PollAnswerHandler,
)

from telegram.constants import PARSEMODE_HTML
from telegram import ParseMode

from dotenv import load_dotenv
load_dotenv(".env")
keyApi = os.environ.get("KEY_API")
PORT = os.environ.get("PORT")
HOST = os.environ.get("HOST")
DATABASE = os.environ.get("DATABASE")
COLLECTIONS = os.environ.get("COLLECTIONS")

from pymongo import MongoClient
client = MongoClient("mongodb://{}:{}".format(HOST,PORT))

db = client[DATABASE] 
connectionDB = db[COLLECTIONS]

connectionDB.insert_many([{"enquete":"Gosta de pizza?"},{"enquete":"Gosta de sorvete?"}])


def start(update:Updater,context:CallbackContext):
    result = connectionDB.find()
    listPoll = []
    for element in result:
        listPoll.append(element)

    listButton = []
    for obj in listPoll:
        listButton.append([InlineKeyboardButton(obj["enquete"], callback_data=str(obj["_id"]))])
    # print(listPoll)

    userID = update.message.chat.id
    context.bot.send_message(
        chat_id=userID,
        text="Enquetes disponíveis: ",
        reply_markup = InlineKeyboardMarkup(listButton)
    )

def enqueteVoto(update: Updater, context:CallbackContext):
    query = update.callback_query
    query.answer()
    enqueteEscolhida = query.data
    query.edit_message_text(text=f"Enquete: {enqueteEscolhida}")


def poll(update: Updater, context:CallbackContext):
    answers = "Gosta de pizza?"
    question = ["Sim", "Não"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        answers,
        question,
        is_anonymous=False,
        allows_multiple_answers=False,
    )

    payload = {
        message.poll.id: {
            "questions": question,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    # print(update.message)
    print(payload)
    context.bot_data.update(payload)

def receive_poll_answer(update: Updater, context:CallbackContext):
    """Summarize a users poll vote"""
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    print(answer)
    # print(answered_poll)
    # print(answered_poll['questions'])
    try:
        questions = answered_poll["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids

    answer_string = ""
    print(answer_string)
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    # print("String:",answer_string)
    # print(answered_poll["chat_id"])

    # context.bot.send_message(
    #     answered_poll["chat_id"],
    #     f"{update.effective_user.mention_html()} respondeu {answer_string}!",
    #     parse_mode=ParseMode.HTML,
    # )

    answered_poll["answers"] += 1
    # Close poll after three participants voted
    if answered_poll["answers"] == 3:
        context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])

updater = Updater(token=keyApi)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start",start))
dispatcher.add_handler(CallbackQueryHandler(enqueteVoto))
dispatcher.add_handler(CommandHandler("enq",poll))
dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))


updater.start_polling()
updater.idle()
