import telebot
import mysql.connector
from datetime import datetime

# توکن را از فایل متنی بخوانید
with open('Token.txt', 'r') as file:
    TOKEN = file.read().strip()

# اطلاعات اتصال به بانک اطلاعاتی MySQL
db_config = {
    'host': 'localhost',
    'user': 'User_DB',
    'password': 'Password_DB',
    'database': 'Name_DB',
}

# اتصال به بانک اطلاعاتی
db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

# ایجاد یک شیء از کتابخانه Telebot
bot = telebot.TeleBot(TOKEN)

# خواندن دستورات و پاسخ‌ها از جدول در بانک اطلاعاتی
cursor.execute('SELECT command, response FROM commands_responses')
commands_and_responses = dict(cursor.fetchall())

# ایجاد یک دستور برای پردازش پیام‌های معمولی
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # اطلاعات مختلف از پیام
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    message_text = message.text
    message_date_unix = message.date
    chat_id = message.chat.id
    message_id = message.message_id

    # تبدیل تاریخ به datetime
    message_date = datetime.utcfromtimestamp(message_date_unix).strftime('%Y-%m-%d %H:%M:%S')

    # ذخیره اطلاعات در بانک اطلاعاتی
    insert_query = '''
    INSERT INTO messages (user_id, user_first_name, user_last_name, message_text, message_date, chat_id, message_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    insert_values = (user_id, user_first_name, user_last_name, message_text, message_date, chat_id, message_id)
    cursor.execute(insert_query, insert_values)
    db_connection.commit()

    # بررسی دستورات و ارسال پاسخ
    response = "متوجه نشدم. لطفاً دستور معتبری وارد کنید."
    for command, reply in commands_and_responses.items():
        if command in message_text:
            response = reply.format(user_first_name)
            break

    # ارسال پاسخ
    bot.reply_to(message, response)

# اجرای ربات
if __name__ == "__main__":
    bot.polling()

# بستن اتصال به بانک اطلاعاتی در پایان برنامه
cursor.close()
db_connection.close()
