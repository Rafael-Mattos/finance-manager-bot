
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
        'callback_data': 'category-description:other'
    })
    
    stacked_inline_buttons(msg.chat.id, btn, 'Selecione a descrição da transação')


def show_menu(msg):
    # bot.send_message(msg.chat.id, "Opções para categoria:")
    btn = [
        {'label': '➕ Criar', 'callback_data': 'new_category'},
        {'label': '✏️ Editar', 'callback_data': 'edit_category'},
        {'label': '🗑️ Excluir', 'callback_data': 'delete_category'},
    ]
    inline_buttons(msg.chat.id, btn, 'Opções para categoria:')

    btn = [
        {'label': '➕ Criar', 'callback_data': 'new_description'},
        {'label': '✏️ Editar', 'callback_data': 'edit_description'},
        {'label': '🗑️ Excluir', 'callback_data': 'delete_description'},
    ]
    inline_buttons(msg.chat.id, btn, 'Opções para descrição:')

    btn = [
        {'label': '✏️ Editar', 'callback_data': 'edit_transaction'},
        {'label': '🗑️ Excluir', 'callback_data': 'delete_transaction'},
        {'label': '🚫 Excluir parcelas', 'callback_data': 'delete_recurring'},
    ]
    stacked_inline_buttons(msg.chat.id, btn, 'Opções para Transações')



def show_transaction_menu(chat_id):
    btn = [
        {'label': '➕ Adicionar observação', 'callback_data': 'add_obs'},
        {'label': '📅 Escolher data', 'callback_data': 'add_data'},
        {'label': '🔁 Repetir transação', 'callback_data': 'add_recurring'},
        {'label': '❌ Descartar transação', 'callback_data': 'exit_transaction'},
        {'label': '✅ Gravar', 'callback_data': 'save_transaction'}
    ]
    stacked_inline_buttons(chat_id, btn, 'Adicione informações ou salve o lançamento.')


def show_all_descriptions(chat_id):
    descriptions = ar.get_all_descriptions()
    btn = []

    for description in descriptions:
        btn.append({
            'label': f"{description['category']['name']} - {description['name']}", 
            'callback_data': f"category-description:{description['category']['id']}-{description['id']}"
        })

    stacked_inline_buttons(chat_id, btn, 'Selecione a descrição desejada.')


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


def save_category(msg):
    category_name = msg.text
    btn = [
        {'label': '➕ Receita', 'callback_data': f'new_category:{category_name}:r'},
        {'label': '➖ Despesa', 'callback_data': f'new_category:{category_name}:e'},
    ]
    inline_buttons(msg.chat.id, btn, 'Selecione o tipo de categoria a ser criada:')


def select_category(chat_id, mode):
    categories = ar.get_all_categories()
    btn = []

    for category in categories:
        btn.append({
            'label': category['name'], 
            'callback_data': f'{mode}:{category['name']}:{category['id']}:{category['type']}'
        })
    btn.append({
        'label': '🚫 Cancelar', 
        'callback_data': f'{mode}:cancel:0:cancel'
    })
    
    stacked_inline_buttons(chat_id, btn, 'Selecione a categoria desejada:')


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
        if 'data_transactions' in globals():
            data_transactions = {}
        
        show_menu(msg)
    

@bot.callback_query_handler(func=lambda call: True)
@validate_users
def callback_handler(call):
    if call.data.startswith('category-description:'):
        # bot.answer_callback_query(call.id, "Pagamento confirmado!")
        # bot.send_message(call.message.chat.id, "Obrigado!")
        _, ids = call.data.split(':')
        if ids == 'other':
            show_all_descriptions(call.message.chat.id)
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
            
        else:
            response = ar.insert_transaction(
                data_transactions[call.from_user.id]['category'],
                data_transactions[call.from_user.id]['description'],
                data_transactions[call.from_user.id]['amount'],
                date,
                obs
            )

        print(response)
        data_transactions.pop(call.from_user.id, None)
    
    elif call.data.startswith('new_category'):
        info = call.data.split(':')

        if len(info) <= 1:
            msg = bot.send_message(call.message.chat.id, 'Digite o nome da categoria a ser criada.')
            bot.register_next_step_handler(msg, save_category)
        else:
            category_name = info[1]
            is_expense = info[2] == 'e'
            response = ar.insert_category(category_name, is_expense)
            msg = bot.send_message(call.message.chat.id, f'A categoria "{response['name']}" foi criada com sucesso!')

    elif call.data.startswith('edit_category'):
        info = call.data.split(':')
        if len(info) <= 1:
            select_category(call.message.chat.id, 'edit_category')
        else:
            try:
                old_category_name = info[1]
                category_id = info[2]
                category_type = 'despesa' if info[3] == 'e' else 'receita'

                if old_category_name == 'cancel':
                    bot.send_message(call.message.chat.id, 'Operação cancelada com sucesso. Nenhuma categoria foi editada.')
                else:
                    msg = bot.send_message(call.message.chat.id, 'Digite o novo nome da categoria')
                    bot.register_next_step_handler(
                        msg, 
                        lambda message: (
                            ar.patch_category(category_id, message.text),
                            bot.send_message(
                                call.message.chat.id, 
                                f'A categoria "{old_category_name}" foi editada para "{message.text}" com sucesso e permanece do tipo "{category_type}"'
                            )
                        )
                    )

            except Exception as e:
                print(f'Erro encontrado: {e}')
                bot.send_message(
                    call.message.chat.id, 
                    f'Ops... Erro encontrado, por favor repita o processo.'
                )


    elif call.data.startswith('delete_category'):
        info = call.data.split(':')

        if len(info) <= 1:
            select_category(call.message.chat.id, 'delete_category')
        else:
            category_name = info[1]
            category_id = info[2]

            if category_name == 'cancel':
                bot.send_message(
                    call.message.chat.id, 
                    f'Operação cancelada com sucesso. Nenhuma categoria foi excluída.'
                )
            else:
                response = ar.delete_category(category_id)
                if response.status_code == 204:
                    return_msg = f'A categoria "{category_name}" foi excluída com sucesso!'
                elif response.status_code == 500:
                    return_msg = f'Não foi possível excluir a camada "{category_name}". Verifique se existem descrições atreladas a ela.'
                else:
                    return_msg = f'Não foi possível excluir a camada "{category_name}". Por favor, tente novamente.'

                bot.send_message(
                    call.message.chat.id, 
                    return_msg
                )

    elif call.data.startswith('new_description'):
        ...
    elif call.data.startswith('edit_description'):
        ...
    elif call.data.startswith('delete_description'):
        ...
    elif call.data.startswith('edit_transaction'):
        ...
    elif call.data.startswith('delete_transaction'):
        ...
    elif call.data.startswith('delete_recurring'):
        ...

    bot.answer_callback_query(call.id)


# bot.polling()
bot.infinity_polling()