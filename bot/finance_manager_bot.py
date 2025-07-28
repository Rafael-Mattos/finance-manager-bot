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
menu_messages = {}
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
    
    stacked_inline_buttons(msg.from_user.id, msg.chat.id, btn, 'Selecione a descrição da transação')


def show_menu(msg):
    btn = [
        {'label': '➕ Criar', 'callback_data': 'new_category'},
        {'label': '✏️ Editar', 'callback_data': 'edit_category'},
        {'label': '🗑️ Excluir', 'callback_data': 'delete_category'},
    ]
    inline_buttons(msg.from_user.id, msg.chat.id, btn, 'Opções para categoria:')

    btn = [
        {'label': '➕ Criar', 'callback_data': 'new_description'},
        {'label': '✏️ Editar', 'callback_data': 'edit_description'},
        {'label': '🗑️ Excluir', 'callback_data': 'delete_description'},
    ]
    inline_buttons(msg.from_user.id, msg.chat.id, btn, 'Opções para descrição:')

    btn = [
        {'label': '✏️ Editar', 'callback_data': 'edit_transaction'},
        {'label': '🗑️ Excluir', 'callback_data': 'delete_transaction'},
        {'label': '🚫 Excluir parcelas', 'callback_data': 'delete_recurring'},
    ]
    stacked_inline_buttons(msg.from_user.id, msg.chat.id, btn, 'Opções para Transações')


def show_transaction_menu(user_id, chat_id):
    btn = [
        {'label': '➕ Adicionar observação', 'callback_data': 'add_obs'},
        {'label': '📅 Escolher data', 'callback_data': 'add_data'},
        {'label': '🔁 Repetir transação', 'callback_data': 'add_recurring'},
        {'label': '❌ Descartar transação', 'callback_data': 'exit_transaction'},
        {'label': '✅ Gravar', 'callback_data': 'save_transaction'}
    ]
    stacked_inline_buttons(user_id, chat_id, btn, 'Adicione informações ou salve o lançamento.')


def show_all_descriptions(user_id, chat_id):
    descriptions = ar.get_all_descriptions()
    btn = []

    for description in descriptions:
        btn.append({
            'label': f"{description['category']['name']} - {description['name']}", 
            'callback_data': f"category-description:{description['category']['id']}-{description['id']}"
        })

    stacked_inline_buttons(user_id, chat_id, btn, 'Selecione a descrição desejada.')


def save_obs(msg):
    data_transactions[msg.from_user.id]["obs"] = msg.text
    bot.reply_to(msg, "Observação adicionada à transação")
    show_transaction_menu(msg.from_user.id, msg.chat.id)


def save_date(msg):
    try:
        transaction_date = datetime.strptime(msg.text, "%d/%m/%Y").date().isoformat()
        data_transactions[msg.from_user.id]["date"] = transaction_date
        bot.reply_to(msg, "Data editada")
    except:
        bot.reply_to(msg, "Data não adicionada. Por favor, adicione uma data como no exemplo: 15/05/2025")
    show_transaction_menu(msg.from_user.id, msg.chat.id)


def save_recurring(msg):
    try:
        repeats = int(msg.text)
        data_transactions[msg.from_user.id]["repeat"] = repeats
        bot.reply_to(msg, f'Transação será repetida por {msg.text} vezes')
    except:
        bot.reply_to(msg, 'Não foi possível adicionar um número de parcelas, digite um número inteiro.')
    show_transaction_menu(msg.from_user.id, msg.chat.id)


def save_category(msg):
    category_name = msg.text
    btn = [
        {'label': '➕ Receita', 'callback_data': f'new_category:{category_name}:r'},
        {'label': '➖ Despesa', 'callback_data': f'new_category:{category_name}:e'},
    ]
    inline_buttons(msg.from_user.id, msg.chat.id, btn, 'Selecione o tipo de categoria a ser criada:')


def select_category(user_id, chat_id, mode):
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
    
    stacked_inline_buttons(user_id, chat_id, btn, 'Selecione a categoria desejada:')


def save_description(msg):
    description_name = msg.text
    expense_btn= []
    revenue_btn = []
    
    categories = ar.get_all_categories()

    for category in categories:
        if category['type'] == 'r':
            revenue_btn.append({
                'label': category['name'], 
                'callback_data': f'new_description:{category['name']}:{category['id']}:{description_name}'
            })
        else:
            expense_btn.append({
                'label': category['name'], 
                'callback_data': f'new_description:{category['name']}:{category['id']}:{description_name}'
            })
    if len(revenue_btn) > 0:
        stacked_inline_buttons(msg.from_user.id, msg.chat.id, revenue_btn, 'Categorias de receita:')
    if len(expense_btn) > 0:
        stacked_inline_buttons(msg.from_user.id, msg.chat.id, expense_btn, 'Categorias de despesa:')
    
    btn = [{
        'label': '🚫 Cancelar', 
        'callback_data': f'new_description:cancel:0:cancel'
    }]
    stacked_inline_buttons(msg.from_user.id, msg.chat.id, btn, 'Cancelar cadastro:')


def select_description(mode, user_id, chat_id):
    btn = []
    descriptions = ar.get_all_descriptions()
    descriptions = sorted(descriptions, key=lambda x: x['category']['type'])
    
    for description in descriptions:
        btn.append({
            'label': f'{description['name']} ({description['category']['name']})', 
            'callback_data': f'{mode}:{description['id']}:{description['name']}'
        })
    
    btn.append({
        'label': '🚫 Cancelar', 
        'callback_data': f'{mode}:0:cancel'
    })

    stacked_inline_buttons(user_id, chat_id, btn, 'Selecione a descrição:')
        


def validate_users(func):
    @wraps(func)
    def wrapper(obj):
        user_id = getattr(obj.from_user, 'id', None)
        user_name = getattr(obj.from_user, 'username', None)

        if user_id in ALLOWED_USERS:
            return func(obj)
        else:
            print(f"Usuário não autorizado - id:{user_id} - username:{user_name}")
            return

    return wrapper


def inline_buttons(user_id, chat_id, buttons, text):
    markup = InlineKeyboardMarkup()
    options = []
    for button in buttons:
        options.append(
            InlineKeyboardButton(
                button['label'], 
                callback_data=button['callback_data']
            ))
    markup.row(*options)
    
    sent_msg = bot.send_message(chat_id, text, reply_markup=markup)

    try:
        menu_messages[user_id].append(sent_msg.message_id)
    except Exception as e:
        print(str(e))



def stacked_inline_buttons(user_id, chat_id, buttons, text):
    markup = InlineKeyboardMarkup()

    for button in buttons:
        markup.add(
            InlineKeyboardButton(
                button['label'], 
                callback_data=button['callback_data']
            ))
        
    sent_msg = bot.send_message(chat_id, text, reply_markup=markup)

    try:
        menu_messages[user_id].append(sent_msg.message_id)
    except Exception as e:
        print(str(e))


def delete_all_menus(user_id, chat_id):
    if user_id in menu_messages:
        for msg_id in menu_messages[user_id]:
            try:
                # bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=None)
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Erro encontrado: {e}")
        menu_messages[user_id] = []


@bot.message_handler(func=lambda msg: True)
@validate_users
def first_message(msg):
    global data_transactions
    global menu_messages
    menu_messages[msg.from_user.id] = []

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
    delete_all_menus(call.from_user.id, call.message.chat.id)

    if call.data.startswith('category-description:'):
        # bot.answer_callback_query(call.id, "Pagamento confirmado!")
        # bot.send_message(call.message.chat.id, "Obrigado!")
        _, ids = call.data.split(':')
        if ids == 'other':
            show_all_descriptions(call.from_user.id, call.message.chat.id)
        else:
            category_id, description_id = ids.split('-')
            data_transactions[call.from_user.id]['category'] = category_id
            data_transactions[call.from_user.id]['description'] = description_id

            show_transaction_menu(call.from_user.id, call.message.chat.id)
            
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
        bot.send_message(
            call.message.chat.id, 
            "❌ A transação foi descartada."
        )
        data_transactions.pop(call.from_user.id, None)
    elif call.data == 'save_transaction':
        bot.answer_callback_query(call.id, "✅ Transação cadastrada com sucesso!")

        obs = data_transactions[call.from_user.id]['obs'] if 'obs' in data_transactions[call.from_user.id] else None
        date = data_transactions[call.from_user.id]['date'] if 'date' in data_transactions[call.from_user.id] else None
        try:
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

            data_transactions.pop(call.from_user.id, None)
            if 'id' in response:
                bot.send_message(
                    call.message.chat.id, 
                    "✅ Lançamento adicionado com sucesso."
                )
            else:
                bot.send_message(
                    call.message.chat.id, 
                    "Algo deu errado, revise seu lençamento e tente novamente."
                )
                print('Erro ao tentar cadastrar transação. Veja retorno abaixo.')
                print(response)
        except Exception as e:
            print('Ocorreu um erro:', str(e))
            bot.send_message(
                call.message.chat.id, 
                "Erro ao tentar enviar lançamento. Por favor, tente novamente."
            )
    
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
            select_category(call.from_user.id, call.message.chat.id, 'edit_category')
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
            select_category(call.from_user.id, call.message.chat.id, 'delete_category')
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
        info = call.data.split(':')

        if len(info) <= 1:
            bot.send_message(call.message.chat.id, 'Lembre-se que deve haver uma categoria existente para ser atrelada à descrição')
            msg = bot.send_message(call.message.chat.id, 'Digite o nome da descrição')
            bot.register_next_step_handler(msg, save_description)
        else:
            try:
                category_name = info[1]
                category_id = info[2]
                description_name = info[3]

                if category_name == 'cancel':
                    bot.send_message(
                        call.message.chat.id, 
                        'Nenhuma descrição foi cadastrada.'
                    )
                    return

                response = ar.insert_description(category_id, description_name)

                if 'id' in response:
                    bot.send_message(
                        call.message.chat.id, 
                        f'✅ A descrição "{description_name}" foi cadastrada com sucesso dentro da categoria "{category_name}"'
                    )
                else:
                    bot.send_message(
                        call.message.chat.id, 
                        'Falha ao tentar cadastrar a nova descrição. Por favor, verifique os dados e tente novamente.'
                    )
            except Exception as e:
                bot.send_message(
                    call.message.chat.id, 
                    'Falha ao tentar cadastrar a nova descrição. Por favor, tente novamente.'
                )
                print(f'Ocorreu um erro: {e}')

    elif call.data.startswith('edit_description'):
        info = call.data.split(':')

        if len(info) <= 1:
            select_description('edit_description', call.from_user.id, call.message.chat.id)
        else:
            try:
                description_id = info[1]
                description_name = info[2]

                if int(description_id) == 0:
                    bot.send_message(
                        call.message.chat.id, 
                        'Nenhuma descrição foi editada.'
                    )
                    return
                
                bot.send_message(call.message.chat.id, f'Você selecionou a descrição "{description_name}" para edição.')

                msg = bot.send_message(call.message.chat.id, 'Digite o novo nome da descrição:')
                bot.register_next_step_handler(
                    msg, 
                    lambda message: (
                        ar.patch_description(description_id, message.text),
                        bot.send_message(
                            call.message.chat.id, 
                            f'A descrição foi editada para "{message.text}" com sucesso.'
                        )
                    )
                )
            except Exception as e:
                print(f'Ocorreu um erro: {e}')
                bot.send_message(
                    call.message.chat.id, 
                    'Falha ao tentar editar a descrição. Por favor, tente novamente.'
                )

    elif call.data.startswith('delete_description'):
        info = call.data.split(':')

        if len(info) <= 1:
            select_description('delete_description', call.from_user.id, call.message.chat.id)
        else:
            try:
                description_id = info[1]
                description_name = info[2]

                if int(description_id) == 0:
                    return_msg = 'Nenhuma descrição foi excluída.'
                    return
                
                response = ar.delete_description(description_id)

                if response.status_code == 204:
                    return_msg = f'A descrição "{description_name}" foi excluída com sucesso.'
                elif response.status_code == 500:
                        return_msg = 'Exclusão não é permitida. Verifique se existem transações atreladas a esta descrição.'
                else:
                    return_msg = 'Nenhuma descrição encontrada.'

            except Exception as e:
                print(f'Erro encontrado: {e}')
                return_msg = f'Erro ao tentar excluir a descrição "{description_name}". Por favor, tente novamente.'
            finally:
                bot.send_message(call.message.chat.id, return_msg)

    elif call.data.startswith('edit_transaction'):
        # to do
        print('Edit transaction')
        bot.send_message(call.message.chat.id, 'Edit transaction - Em desenvolvimento, feature estará disponivel em breve')
    elif call.data.startswith('delete_transaction'):
        # to do
        print('Delete transaction')
        bot.send_message(call.message.chat.id, 'Delete transaction - Em desenvolvimento, feature estará disponivel em breve')
    elif call.data.startswith('delete_recurring'):
        # to do
        print('Delete recurring transaction')
        bot.send_message(call.message.chat.id, 'elete recurring transaction - Em desenvolvimento, feature estará disponivel em breve')

    bot.answer_callback_query(call.id)


# bot.polling()
bot.infinity_polling()