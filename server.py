import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, Bot
from config import BOT_TOKEN
from datetime import datetime
import pymorphy2
import asyncio
import random


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
morph = pymorphy2.MorphAnalyzer()
MONTHES = {1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель', 5: 'май', 6: 'июнь', 7: 'июль',
           8: 'август', 9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'}
bot = Bot(BOT_TOKEN)
TIMER = -1


async def echo(update, context):
    await update.message.reply_text(f'Я получил сообщение: {update.message.text}')


async def curr_time(update, context):
    await update.message.reply_text(f"Текущее время (МСК): {datetime.now().isoformat().split('T')[1].split('Z')[0]}")


async def curr_date(update, context):
    date_ = datetime.now()
    month_name = morph.parse(MONTHES[date_.month])[0].inflect({'gent'}).word
    day = date_.day
    await update.message.reply_text(f"Сегодня {day} {month_name} {date_.year}г.")


async def set_timer(update, context):
    global TIMER
    d = context.args
    try:
        if len(d) != 1:
            raise SyntaxError
        d = int(d[0])
        TIMER = d
    except ValueError or TypeError:
        await update.message.reply_text(f"Аргумент должен быть числом")
    except SyntaxError:
        await update.message.reply_text(f"Число аргументов должен быть равно 1")
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
    word = morph.parse('секунда')[0].make_agree_with_number(TIMER).word
    text = f'\U000023F3 Вернусь через {TIMER} {word}!'
    if job_removed:
        text += '\nСтарая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    word = morph.parse('секунда')[0].make_agree_with_number(TIMER).word
    word2 = morph.parse('пройти')[0].make_agree_with_number(TIMER).word
    await context.bot.send_message(context.job.chat_id, text=f'\U0000231B КУКУ! {TIMER} {word} {word2}!')


# Keyboard commands
async def six_cube(update, context):
    await update.message.reply_text(f'Allons-y: {random.randint(1, 6)}')


async def six_cube_2(update, context):
    await update.message.reply_text(f'Geronimo: {random.randint(1, 6)}, {random.randint(1, 6)}')


async def twenty_cube(update, context):
    await update.message.reply_text(f'Бум-бум, бух-бух: {random.randint(1, 20)}')


async def main_menu(update, context):
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data[update.message.chat.id] = markup
    await update.message.reply_text("Главное меню",
                                    reply_markup=context.user_data[update.message.chat.id])


async def dice_kbrd(update, context):
    reply_keyboard = [['/6_edge_cube', '/2_6_edge_cubes'], ['/20_edge_cube', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data[update.message.chat.id] = markup
    await update.message.reply_text("Меню бросков",
                                    reply_markup=context.user_data[update.message.chat.id])


async def timer_kbrd(update, context):
    reply_keyboard = [['/30sec', '/1min'], ['/5min', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.user_data[update.message.chat.id] = markup
    await update.message.reply_text("Меню таймера",
                                    reply_markup=context.user_data[update.message.chat.id])


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer_30(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task_30, 30, chat_id=chat_id, name=str(chat_id), data=30)
    text = '\U000023F3 Засек 30 секунд'
    if job_removed:
        text += '\nСтарая задача удалена.'
    await update.message.reply_text(text)


async def task_30(context):
    await context.bot.send_message(context.job.chat_id, text='\U0000231B 30 секунд истекли')


async def set_timer_60(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task_60, 60, chat_id=chat_id, name=str(chat_id), data=60)
    text = '\U000023F3 Засек 1 минуту'
    if job_removed:
        text += '\nСтарая задача удалена.'
    await update.message.reply_text(text)


async def task_60(context):
    await context.bot.send_message(context.job.chat_id, text='\U0000231B 1 минута истекла')


async def set_timer_300(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task_300, 300, chat_id=chat_id, name=str(chat_id), data=300)
    text = '\U000023F3 Засек 5 минут'
    if job_removed:
        text += '\nСтарая задача удалена.'
    await update.message.reply_text(text)


async def task_300(context):
    await context.bot.send_message(context.job.chat_id, text='\U0000231B 5 минут истекли')


async def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def dialog(update, context):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
    # Оно указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.


async def first_response(update, context):
    # Это ответ на первый вопрос.
    # Мы можем использовать его во втором вопросе.
    locality = update.message.text
    await update.message.reply_text(
        f"Какая погода в городе {locality}?")
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]
    return 2


async def second_response(update, context):
    # Ответ на второй вопрос.
    # Мы можем его сохранить в базе данных или переслать куда-либо.
    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text("Спасибо за участие в опросе! Всего доброго!")
    return ConversationHandler.END  # Константа, означающая конец диалога.
    # Все обработчики из states и fallbacks становятся неактивными.


async def skip(update, context):
    # Это ответ на первый вопрос.
    # Мы можем использовать его во втором вопросе.
    await update.message.reply_text("Какая погода у вас за окном?")
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]
    return 2


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(CommandHandler("time", curr_time))
    application.add_handler(CommandHandler("date", curr_date))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CommandHandler("back", main_menu))
    application.add_handler(CommandHandler("timer", timer_kbrd))
    application.add_handler(CommandHandler("dice", dice_kbrd))

    application.add_handler(CommandHandler("6_edge_cube", six_cube))
    application.add_handler(CommandHandler("2_6_edge_cubes", six_cube_2))
    application.add_handler(CommandHandler("20_edge_cube", twenty_cube))

    application.add_handler(CommandHandler("30sec", set_timer_30))
    application.add_handler(CommandHandler("1min", set_timer_60))
    application.add_handler(CommandHandler("5min", set_timer_300))
    application.add_handler(CommandHandler("unset", unset))

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /dialog. Она задаёт первый вопрос.
        entry_points=[CommandHandler('dialog', dialog)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response),
                CommandHandler("skip", skip)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)],
    )

    application.add_handler(conv_handler)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
