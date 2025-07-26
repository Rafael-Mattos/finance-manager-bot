
from decimal import Decimal
from datetime import datetime
import os

from dotenv import load_dotenv
from functools import wraps
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from api_requests import ApiRequests


load_dotenv()
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split(",")))
TELEGRAM_TOKEN = os.getenv("TELEGRAMTOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
data_transactions = {}
ar = ApiRequests()


def show_top_ten_descriptions(msg):
    descriptions = ar.get_top_descriptions()
    btn = []

    for description in descriptions:
        btn.append({
            'label': f"{description['category__name']} - {description['description__name']}", 
            'callback_data': f"category-description:{description['category__id']}-{description['description__id']}"
            })
    
    btn.append({
        'label': 'Outra', 
        'callback_data': "category-description:other"
    })
    
    stacked_inline_buttons(msg.chat.id, btn, 'Selecione a descrição da transação')


def show_menu():
    print('Abrir menu')


def show_transaction_menu(chat_id):
    btn = [
        {'label': '➕ Adicionar observação', 'callback_data': 'add_obs'},
        {'label': '📅 Escolher data', 'callback_data': 'add_data'},
        {'label': '🔁 Repetir transação', 'callback_data': 'add_recurring'}, # 
        {'label': '❌ Descartar transação', 'callback_data': 'exit_transaction'},
        {'label': '✅ Gravar', 'callback_data': 'save_transaction'}
    ]
    stacked_inline_buttons(chat_id, btn, 'Adicione informações ou salve o lançamento.')


def save_obs(msg):
    data_transactions[msg.from_user.id]["obs"] = msg.text
    bot.reply_to(msg, "Observação adicionada à transação")
    show_transaction_menu(msg.chat.id)


def save_date(msg):
    try:
        transaction_date = datetime.strptime(msg.text, "%d/%m/%Y").date().isoformat()
        data_transactions[msg.from_user.id]["date"] = transaction_date
        bot.reply_to(msg, "Data editada")
    except:
        bot.reply_to(msg, "Data não adicionada. Por favor, adicione uma data como no exemplo: 15/05/2025")
    show_transaction_menu(msg.chat.id)


def save_recurring(msg):
    try:
        repeats = int(msg.text)
        data_transactions[msg.from_user.id]["repeat"] = repeats
        bot.reply_to(msg, f'Transação será repetida por {msg.text} vezes')
    except:
        bot.reply_to(msg, 'Não foi possível adicionar um número de parcelas, digite um número inteiro.')
    show_transaction_menu(msg.chat.id)


def validate_users(func):
    @wraps(func)
    def wrapper(obj):
        user_id = getattr(obj, 'from_user', None)

        if not user_id and hasattr(obj, 'message'):
            user_id = getattr(obj.from_user, 'id', None)
        else:
            user_id = getattr(obj.from_user, 'id', None)

        if user_id in ALLOWED_USERS:
            return func(obj)
        else:
            print(f"Usuário não autorizado: {user_id}")
            return

    return wrapper


def inline_buttons(chat_id, buttons, text):
    markup = InlineKeyboardMarkup()
    options = []
    for button in buttons:
        options.append(
            InlineKeyboardButton(
                button['label'], 
                callback_data=button['callback_data']
            ))
    markup.row(*options)
    bot.send_message(chat_id, text, reply_markup=markup)


def stacked_inline_buttons(chat_id, buttons, text):
    markup = InlineKeyboardMarkup()

    for button in buttons:
        markup.add(
            InlineKeyboardButton(
                button['label'], 
                callback_data=button['callback_data']
            ))
        
    bot.send_message(chat_id, text, reply_markup=markup)


@bot.message_handler(func=lambda msg: True)
@validate_users
def first_message(msg):
    try:
        amount = msg.text.replace(',','.')
        _ = Decimal(amount)

        data_transactions[msg.from_user.id] = {
            "amount": amount
        }

        show_top_ten_descriptions(msg)
    except Exception as e:
        print(str(e))
        show_menu()
    

@bot.callback_query_handler(func=lambda call: True)
@validate_users
def callback_handler(call):
    if call.data.startswith('category-description:'):
        # bot.answer_callback_query(call.id, "Pagamento confirmado!")
        # bot.send_message(call.message.chat.id, "Obrigado!")
        _, ids = call.data.split(':')
        if ids == 'other':
            ...
        else:
            category_id, description_id = ids.split('-')
            data_transactions[call.from_user.id]['category'] = category_id
            data_transactions[call.from_user.id]['description'] = description_id

            show_transaction_menu(call.message.chat.id)
            
    elif call.data == 'add_obs':
        msg = bot.send_message(call.message.chat.id, "Digite a observação:")
        bot.register_next_step_handler(msg, save_obs)
    elif call.data == 'add_data':
        msg = bot.send_message(call.message.chat.id, "Digite a data:")
        bot.register_next_step_handler(msg, save_date)
    elif call.data == 'add_recurring':
        msg = bot.send_message(
            call.message.chat.id, 
            "Digite o número de repetições para este lançamento ou 0 para não estabelecer limites."
        )
        bot.register_next_step_handler(msg, save_recurring)
    elif call.data == 'exit_transaction':
        bot.answer_callback_query(call.id, "❌ A transação foi descartada.")
        data_transactions.pop(call.from_user.id, None)
    elif call.data == 'save_transaction':
        bot.answer_callback_query(call.id, "✅ Transação cadastrada com sucesso!")

        obs = data_transactions[call.from_user.id]['obs'] if 'obs' in data_transactions[call.from_user.id] else None
        date = data_transactions[call.from_user.id]['date'] if 'date' in data_transactions[call.from_user.id] else None

        if 'repeat' in data_transactions[call.from_user.id]:
            response = ar.insert_recurring_transaction(
                data_transactions[call.from_user.id]['category'],
                data_transactions[call.from_user.id]['description'],
                data_transactions[call.from_user.id]['amount'],
                date,
                obs,
                data_transactions[call.from_user.id]['repeat']
            )
            print(response)
        else:
            ar.insert_transaction(
                data_transactions[call.from_user.id]['category'],
                data_transactions[call.from_user.id]['description'],
                data_transactions[call.from_user.id]['amount'],
                date,
                obs
            )

        data_transactions.pop(call.from_user.id, None)
    
    bot.answer_callback_query(call.id)


# bot.polling()
bot.infinity_polling()