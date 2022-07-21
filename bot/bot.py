import os
from telegram.ext import(
    Updater,
    CommandHandler,
    CallbackContext,
    PollAnswerHandler,
)
from telegram.constants import PARSEMODE_HTML
from telegram import ParseMode

from dotenv import load_dotenv
load_dotenv(".env")
keyApi = os.environ.get("KEY_API")

enquetes = ["Gosta de pizza?","Gosta de sorvete?"]

numeros = [""]

def start(update:Updater,context:CallbackContext):
    print(update)
    userID = update.message.chat.id
    if update.effective_chat.username not in numeros:
        context.bot.send_message(
            chat_id=userID,
            text="Usuario não pode votar",
        )

    userID = update.message.chat.id
    context.bot.send_message(
        chat_id=userID,
        text=enquetes,
    )

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
dispatcher.add_handler(CommandHandler("enq",poll))
dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))


updater.start_polling()
updater.idle()