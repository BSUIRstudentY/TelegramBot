import telebot
from telebot import types

bot = telebot.TeleBot('7818502719:AAEpJ3gL-9NrzvJosFWyvKEd2xUuH1Xg-9c')


bucket_map = {}  # Словарь корзины {chat_id: {product_id: quantity}}
accept_map = {}
ADMIN = [1795108376, 5342639460]

@bot.message_handler(commands=['start'])
def start(message):


    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Каталог🙈")
    btn3 = types.KeyboardButton("Корзина🛒")
    markup.add(btn1, btn3)
    bot.send_message(message.chat.id, f"💯 Я БОТ по продукции от QRsharmstudio, выберай действие 💯 ", reply_markup=markup)



@bot.message_handler(content_types=['text'])
def func(message):

    if message.text == "Каталог🙈":
        for i in range(1, 4):
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("❌ Не интересно", callback_data='delete_photo')
            btn2 = types.InlineKeyboardButton(f"Добавить в корзину ✅", callback_data=f'button_clicked_{i}')
            markup.add(btn1, btn2)

            with open(f"{i}.jpeg", "rb") as photo:
                bot.send_photo(message.chat.id, photo, caption=f'✅ Цена 7 BYN ✅ ', reply_markup=markup)

    elif message.text == 'Корзина🛒':
        username = message.from_user.username
        user_link = 'https://t.me/'

        if(username == None):
            username = message.chat.id
            user_link = f"https://web.telegram.org/k/#{username}"
        else:
            user_link+= username



        summ = 0
        if user_link in bucket_map:
            for product_id, quantity in bucket_map[user_link].items():
                with open(f"{product_id}.jpeg", "rb") as photo:
                    bot.send_document(message.chat.id, photo, caption=f'Цена 7 BYN, в заказе указано {quantity} шт.')
                summ += 7 * quantity

            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("❌ Отказаться", callback_data='cancel')
            btn2 = types.InlineKeyboardButton(f"Оформить ✅", callback_data=f'accept')
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id, f"💯 Итоговая цена 🟰 {summ} BYN 💳", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Корзина пуста ⛔')
    elif message.text == 'BUCKET_DATABASE':
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("❌ Отказаться", callback_data='cancel_offer')
        btn2 = types.InlineKeyboardButton(f"Оформить ✅", callback_data='api')
        markup.add(btn1, btn2)
        for chat_id, chat_map in accept_map.items():

            text = f'✅ Link: {chat_id}\n'
            summ = 0
            for product_id, quantity in chat_map.items():

                text += f'📌 Брелок №{product_id}: {quantity}\n'
                summ += 7 * quantity
            text += f'Цена 🟰 {summ} BYN 💳'

            bot.send_message(message.chat.id, text, reply_markup=markup)

    else:
        send_main_menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('button_clicked_'))
def callback_button(call):
    product_id = int(call.data.split('_')[-1])  # Получаем ID товара
    bot.send_message(call.message.chat.id, f"Введите количество для товара:")

    bot.register_next_step_handler(call.message, save_quantity, product_id)
    print(bucket_map)  # Выводим состояние корзины в консоль


def save_quantity(message, product_id):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            bot.send_message(message.chat.id, "Количество должно быть больше 0! Попробуйте снова.")
            bot.register_next_step_handler(message, save_quantity, product_id)
            return

        # Если пользователь уже имеет корзину
        username = message.from_user.username
        user_link = 'https://t.me/'

        if (username == None):
            username = message.chat.id
            user_link = f"https://web.telegram.org/k/#{username}"
        else:
            user_link += username
        if user_link in bucket_map:
            if product_id in bucket_map[user_link]:
                # Если товар уже есть, прибавляем количество
                bucket_map[user_link][product_id] += quantity
            else:
                # Если товара еще нет, просто добавляем
                bucket_map[user_link][product_id] = quantity
        else:
            # Если корзины ещё нет, создаём новую
            bucket_map[user_link] = {product_id: quantity}

        bot.send_message(message.chat.id, f"✅ Добавлено {quantity} шт. товара в корзину!\n"
                                          f"Всего в корзине: {bucket_map[user_link][product_id]} шт данного товара.")
        print(bucket_map)  # Выводим состояние корзины

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число!")
        bot.register_next_step_handler(message, save_quantity, product_id)


@bot.callback_query_handler(func=lambda call: call.data == "delete_photo")
def delete_photo(call):

    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel(call):
    username = call.from_user.username
    user_link = 'https://t.me/'

    if (username == None):
        username = call.message.chat.id
        user_link = f"https://web.telegram.org/k/#{username}"
    else:
        user_link += username
    bucket_map.pop(user_link, None)
    accept_map.pop(user_link, None)
    bot.edit_message_text("Заказ анулирован ⁉",call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Корзина пуста ⛔')
    print(bucket_map)


@bot.callback_query_handler(func=lambda call: call.data == 'accept')
def accept(call):
    bot.edit_message_text("Заказ зарегестрирован успешно ✅", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Ожидайте, наш сотрудник в ближайшее время вам напишет ⏳')
    username = call.from_user.username
    user_link = 'https://t.me/'

    if (username == None):
        username = call.message.chat.id
        user_link = f"https://web.telegram.org/k/#{username}"
    else:
        user_link += username
    accept_map[user_link] = bucket_map[user_link]
    print(accept_map)
    for i in ADMIN:
        text = '✅ Новый заказ зарегестрирован\n🔗 Ссылка: '
        summ = 0
        text += user_link + '\n'
        for product_id,quantity in accept_map[user_link].items():
            text += f'📌 Брелок №{product_id}: {quantity}\n'
            summ += 7*quantity
        text += f'💳 Сумма: {summ} BYN'
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("❌ Отказаться", callback_data='cancel_offer')
        btn2 = types.InlineKeyboardButton(f"Оформить ✅", callback_data='api')
        markup.add(btn1, btn2)
        bot.send_message(i, text, reply_markup=markup)





@bot.callback_query_handler(func=lambda call: call.data == "cancel_offer")
def cancel_offer(call):
    username = call.from_user.username
    user_link = 'https://t.me/'

    if (username == None):
        username = call.message.chat.id
        user_link = f"https://web.telegram.org/k/#{username}"
    else:
        user_link += username
    bucket_map.pop(user_link, None)
    accept_map.pop(user_link, None)
    bot.delete_message(call.message.chat.id, call.message.message_id)


def send_main_menu(chat_id):
    """Функция отправки главного меню с кнопками"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Каталог🙈")
    btn2 = types.KeyboardButton("Корзина🛒")
    markup.add(btn1, btn2)

    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)


bot.polling(none_stop=True)
