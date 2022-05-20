import telebot
import requests
import json
from config import keys, TOKEN

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.send_message(message.chat.id,
                     f'Привет, {message.chat.username}. \nЧтобы узнать, как пользоваться '
                     f'ботом, введи команду /help')


@bot.message_handler(commands=['help'])
def values_message(message):
    bot.send_message(message.chat.id,
                     f'Чтобы воспользоваться ботом отправь сообщение вида: \n\n'
                     f'<Имя валюты, цену которой хочешь узнать> <Имя валюты, в которой надо узнать цену первой валюты> <Сумуу для перевода> \n\n'
                     f'Увидеть список всех доступных валют, введи команду /values')


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for key in keys.keys():
        text = "\n".join((text, key)) #получение названий валют
    bot.send_message(message.chat.id, text) #вывод


class ConvertionExeption(Exception):
    pass


@bot.message_handler(content_types=['text', ])
def converter(message: telebot.types.Message):
    try:
        values = message.text.split(' ') #проверка что введено три параметра

        if len(values) != 3:
            raise ConvertionExeption('Слишком много параметров.')

        quote, base, amount = values
        if quote == base:
            raise ConvertionExeption(
                f'Невозможно перевести одинаковые валюты {base}')

        try:
            quote_ticker = keys[quote.upper()] #RUB

        except KeyError:
            raise ConvertionExeption(f'Не удалось обработать валюту {quote}')

        try:
            base_ticker = keys[base.upper()] #EUR
        except KeyError:
            raise ConvertionExeption(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount) #1000
        except ValueError:
            raise ConvertionExeption(
                f'Не удалось обработать количество {amount}')

        r = requests.get(
            f'https://free.currconv.com/api/v7/convert?q={quote_ticker}_{base_ticker}&compact=ultra&apiKey=d84cf1bb0ece1d1a78a5')
        total_base = json.loads(r.content)
        total_base = list(total_base.values())
    except ConvertionExeption as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду.\n{e}')
    else:
        text = f'{amount} {quote} = {round(float(*total_base), 3) * amount} {base} ' #вывод подсчётов
        bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)
