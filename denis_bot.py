import time
import telebot
import schedule
import threading

# Токен от BotFather
API_TOKEN = 'PERSONAL_ACCESS_TOKEN'

# Телеграм бот
bot = telebot.TeleBot(API_TOKEN)

# Отправляет опрос в чат
def send_poll(chat_id, poll: telebot.types.Poll):
    bot.send_poll(chat_id,
                    question=poll.question, 
                    options=poll.options, 
                    allows_multiple_answers=poll.allows_multiple_answers, 
                    is_anonymous=poll.is_anonymous)

# Проверяет, что строка содержит время
def is_valid_time(time_str: str):
    try:
        time.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

# TODO: расширить логику на несколько чатов и запоминать chat_id
schedule_data = {
    'poll': None,
    'time': None
}
 
# Начало работы с ботом
@bot.message_handler(commands=['start'])
def start(msg: telebot.types.Message):
    bot.send_message(msg.chat.id, 'Привет!\nЯ умею отправлять опросы в группу по расписанию')
    bot.send_message(msg.chat.id, 'Для начала работы добавь меня в свою группу')

# Получение помощи
@bot.message_handler(commands=['help'])
def help_handler(msg: telebot.types.Message):
    help_msg = 'Чтобы создать рассылку, напиши в какое время присылать опрос: /set HH:WW. Например: /set 9:00\n'
    help_msg += 'А чтобы отключить используй /turnoff'
    bot.send_message(msg.chat.id, help_msg)

# Установка времени
@bot.message_handler(commands=['set'])
def set_time(msg: telebot.types.Message):
    if not schedule_data['poll'] is None and not schedule_data['time'] is None:
        bot.send_message(msg.chat.id, 'В группе уже создана рассылка. Чтобы создать новую, нужно сперва отменить имеющуюся. Подробнее: /help')
        return
    args = msg.text.split()
    if len(args) == 2:
        time_str = args[1]
        if is_valid_time(time_str):
            schedule_data['time'] = time_str
            bot.reply_to(msg, f"Супер, время я запомнил: {schedule_data['time']}")
            bot.send_message(msg.chat.id, 'А теперь опрос, который буду присылать сюда. Обязательно отправь ответом на моё сообщения, иначе я могу его не увидеть)')
        else:
            bot.reply_to(msg, 'Что-то не так с форматом, попробуй еще раз')
    else:
        bot.reply_to(msg, 'Что-то не так, попробуй еще раз')

# Отключение рассылки
@bot.message_handler(commands=['turnoff'])
def turnoff_mailing(msg: telebot.types.Message):
    schedule.clear(msg.chat.id)
    schedule_data['time'] = None
    schedule_data['poll'] = None
    bot.send_message(msg.chat.id, f'Все рассылки в группу {msg.chat.title} отменены')

# Добавление бота в чат
@bot.my_chat_member_handler()
def my_chat_m(msg: telebot.types.ChatMemberUpdated):
    bot.send_message(msg.chat.id,"Всем привет!\nЯ умею отправлять опросы каждый будний день в определнное время")
    bot.send_message(msg.chat.id,"Чтобы создать рассылку, напиши в какое время присылать опрос: /set HH:WW. Например: /set 9:00")

# Получение опроса
@bot.message_handler(content_types=['poll'])
def poll_handler(msg: telebot.types.Message):
    if schedule_data['time'] is None:
        bot.send_message(msg.chat.id,"Чтобы создать рассылку, напиши в какое время присылать опрос: /set HH:WW. Например: /set 9:00")
    elif schedule_data['poll'] is None:
        # TODO: здесь сохранить параметры рассылки в файл на случай перезапуска бота
        schedule_data['poll'] = msg.poll
        bot.reply_to(msg, f"Отлично! Рассылка создана. Опрос будет приходить с пн по пт в {schedule_data['time']}")
        bot.send_message(msg.chat.id, 'Для отмены рассылки используй команду /turnoff')
        # Создаем рассылку опроса
        
        # Заглушка для тестирования
        # schedule.every(5).seconds.do(send_poll, msg.chat.id, msg.poll).tag(msg.chat.id)

        # Отправка каждый будний день в определенное время
        schedule.every().monday.at(schedule_data['time']).do(send_poll, msg.chat.id, msg.poll).tag(msg.chat.id)
        schedule.every().tuesday.at(schedule_data['time']).do(send_poll, msg.chat.id, msg.poll).tag(msg.chat.id)
        schedule.every().wednesday.at(schedule_data['time']).do(send_poll, msg.chat.id, msg.poll).tag(msg.chat.id)
        schedule.every().thursday.at(schedule_data['time']).do(send_poll, msg.chat.id, msg.poll).tag(msg.chat.id)
        schedule.every().friday.at(schedule_data['time']).do(send_poll, msg.chat.id, msg.poll).tag(msg.chat.id)
    else:
        bot.send_message(msg.chat.id, 'В группе уже создана рассылка. Чтобы создать новую, нужно сперва отменить имеющуюся. Подробнее: /help')

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    try:
        while True:
            schedule.run_pending()
            time.sleep(0.01)
    except:
        print('Occured some exception')
    finally:
        # Останавливаем все работы
        schedule.clear()
        print('All jobs had been stopped')