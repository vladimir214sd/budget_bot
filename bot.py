import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7382866600:AAHxlueonwshvRwcAiHmSSbzJl3Hra9oxyM'
APP_URL = 'https://t.me/afafajfgajfgbot/dfgdf'
FILE_PATH = r'C:\Users\batal\OneDrive\Рабочий стол\budget_bot\MyBudget Руководство пользователя.pdf'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="Открыть приложение", url=APP_URL)
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        "Привет! Нажмите кнопку ниже, чтобы открыть приложение.\n\nДля получения помощи используйте команду /help",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def send_help_file(message):
    bot.send_message(
        message.chat.id,
        "Ниже представлено руководство пользователя. Если вы не нашли ответ на свой вопрос или у вас есть предложение, обращайтесь к нам на электронную почту vabatalov@edu.hse.ru"
    )
    with open(FILE_PATH, 'rb') as file:
        bot.send_document(message.chat.id, file)

if __name__ == '__main__':
    bot.polling(none_stop=True)
