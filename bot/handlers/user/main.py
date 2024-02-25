import datetime
from urllib.parse import urlparse

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, ChatType
from aiogram.utils.exceptions import ChatNotFound

from bot.database.methods import select_max_role_id, create_user, check_channel, check_role, check_helper, check_user, \
    get_all_categories, get_all_items, select_bought_items, get_bought_item_info, get_item_info, \
    select_item_values_amount, get_user_balance, get_item_value, buy_item, add_bought_item, buy_item_for_balance, \
    select_user_operations, select_user_items, check_user_referrals, check_rules, start_operation, \
    select_unfinished_operations, get_user_referral, finish_operation, update_balance, create_operation, \
    bought_items_list, check_value
from bot.handlers.other import get_bot_user_ids, check_sub_channel
from bot.keyboards import check_sub, main_menu, categories_list, goods_list, user_items_list, back, item_info, \
    profile, rules, payment_menu, close
from bot.logger_mesh import logger
from bot.misc import TgConfig, EnvKeys
from bot.misc.payment import quick_pay, check_payment_status


async def start(message: Message):
    bot, user_id = await get_bot_user_ids(message)

    if message.chat.type != ChatType.PRIVATE:
        return

    TgConfig.STATE[user_id] = None

    owner = select_max_role_id()
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    referral_id = message.text[7:] if message.text[7:] != str(user_id) else None
    user_role = owner if str(user_id) == EnvKeys.OWNER else 1
    create_user(telegram_id=user_id, registration_date=formatted_time, referral_id=referral_id, role=user_role)
    chat = check_channel()
    role_data = check_role(user_id)

    try:
        if chat is not None:
            parsed_url = urlparse(chat)
            channel_username = parsed_url.path.lstrip('/')
            chat_member = await bot.get_chat_member(chat_id='@' + channel_username, user_id=user_id)
            if not await check_sub_channel(chat_member):
                await bot.send_message(user_id,
                                       'Для начала подпишитесь на новостной канал',
                                       reply_markup=check_sub())
                await bot.delete_message(chat_id=message.chat.id,
                                         message_id=message.message_id)
                return

    except ChatNotFound:
        await bot.send_message(user_id,
                               '⛩️ Основное меню',
                               reply_markup=main_menu(role_data, chat, check_helper()))
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id)
        return

    keyboard = main_menu(role_data, chat, check_helper())
    await bot.send_message(user_id,
                           '⛩️ Основное меню',
                           reply_markup=keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def back_to_menu_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user = check_user(call.from_user.id)
    keyboard = main_menu(user.role_id, check_channel(), check_helper())
    await bot.edit_message_text('⛩️ Основное меню',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=keyboard)


async def close_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    await bot.delete_message(chat_id=call.message.chat.id,
                             message_id=call.message.message_id)


async def shop_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    categories = get_all_categories()
    max_index = len(categories) // 10
    if len(categories) % 10 == 0:
        max_index -= 1
    markup = categories_list(categories, 0, max_index)
    await bot.edit_message_text('🏪 Категории магазина',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=markup)


async def navigate_categories(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    categories = get_all_categories()
    current_index = int(call.data.split('_')[1])
    max_index = len(categories) // 10
    if len(categories) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = categories_list(categories, current_index, max_index)
        await bot.edit_message_text(message_id=call.message.message_id,
                                    chat_id=call.message.chat.id,
                                    text='🏪 Категории магазина',
                                    reply_markup=markup)
    else:
        await bot.answer_callback_query(callback_query_id=call.id,
                                        text="❌ Такой страницы нет")


async def dummy_button(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    await bot.answer_callback_query(callback_query_id=call.id, text="")


async def items_list_callback_handler(call: CallbackQuery):
    category_name = call.data[9:]
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    goods = get_all_items(category_name)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    markup = goods_list(goods, category_name, 0, max_index)
    await bot.edit_message_text('🏪 выберите нужный товар', chat_id=call.message.chat.id,
                                message_id=call.message.message_id, reply_markup=markup)


async def navigate_goods(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    category_name = call.data.split('_')[1]
    current_index = int(call.data.split('_')[2])
    goods = get_all_items(category_name)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = goods_list(goods, category_name, current_index, max_index)
        await bot.edit_message_text(message_id=call.message.message_id,
                                    chat_id=call.message.chat.id,
                                    text='🏪 выберите нужный товар',
                                    reply_markup=markup)
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="❌ Такой страницы нет")


async def item_info_callback_handler(call: CallbackQuery):
    item_name = call.data[5:]
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    item_info_list = get_item_info(item_name)
    category = item_info_list['category_name']
    if check_value(item_name) is False:
        amount = select_item_values_amount(item_name)
        await bot.edit_message_text(
            f'🏪 Товар {item_name}\n'
            f'Описание: {item_info_list["description"]}\n'
            f'Цена - {item_info_list["price"]}₽\n'
            f'Количество - {round(amount)}шт.',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=item_info(item_name, category))
    else:
        await bot.edit_message_text(
            f'🏪 Товар {item_name}\n'
            f'Описание: {item_info_list["description"]}\n'
            f'Цена - {item_info_list["price"]}₽\n'
            f'Количество - неограниченно',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=item_info(item_name, category))


async def buy_item_callback_handler(call: CallbackQuery):
    item_name = call.data[4:]
    bot, user_id = await get_bot_user_ids(call)
    msg = call.message.message_id
    item_info_list = get_item_info(item_name)
    item_price = item_info_list["price"]
    user_balance = get_user_balance(user_id)

    if user_balance >= item_price:
        value_data = get_item_value(item_name)

        if value_data:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            buy_item(value_data['id'], value_data['is_infinity'])
            add_bought_item(value_data['item_name'], value_data['value'], item_price, user_id, formatted_time)
            new_balance = buy_item_for_balance(user_id, item_price)
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=msg,
                                        text=f'✅ Товар куплен. '
                                             f'<b>Баланс</b>: <i>{new_balance}</i>₽\n\n{value_data["value"]}',
                                        parse_mode='HTML',
                                        reply_markup=back(f'item_{item_name}'))
            user_info = await bot.get_chat(user_id)
            logger.info(f"Пользователь {user_id} ({user_info.first_name})"
                        f" купил 1 товар позиции {value_data['item_name']} за {item_price}р")
            return

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=msg,
                                    text='❌ Товара нет в  наличие',
                                    reply_markup=back(f'item_{item_name}'))
        return

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=msg,
                                text='❌ Недостаточно средств',
                                reply_markup=back(f'item_{item_name}'))


async def bought_items_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    bought_goods = select_bought_items(user_id)
    goods = bought_items_list(user_id)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    keyboard = user_items_list(bought_goods, 'user', 'profile', 'bought_items', 0, max_index)
    await bot.edit_message_text('Ваши товары:', chat_id=call.message.chat.id,
                                message_id=call.message.message_id, reply_markup=keyboard)


async def navigate_bought_items(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    goods = bought_items_list(user_id)
    bought_goods = select_bought_items(user_id)
    current_index = int(call.data.split('_')[1])
    data = call.data.split('_')[2]
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        if data == 'user':
            back_data = 'profile'
            pre_back = 'bought_items'
        else:
            back_data = f'check-user_{data}'
            pre_back = f'user-items_{data}'
        markup = user_items_list(bought_goods, data, back_data, pre_back, current_index, max_index)
        await bot.edit_message_text(message_id=call.message.message_id,
                                    chat_id=call.message.chat.id,
                                    text='Ваши товары:',
                                    reply_markup=markup)
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="❌ Такой страницы нет")


async def bought_item_info_callback_handler(call: CallbackQuery):
    item_id = call.data.split(":")[1]
    back_data = call.data.split(":")[2]
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    item = get_bought_item_info(item_id)
    await bot.edit_message_text(
        f'<b>Товар</b>: <code>{item["item_name"]}</code>\n'
        f'<b>Цена</b>: <code>{item["price"]}</code>₽\n'
        f'<b>Дата покупки</b>: <code>{item["bought_datetime"]}</code>\n'
        f'<b>Уникальный ID операции</b>: <code>{item["unique_id"]}</code>\n'
        f'<b>Значение</b>:\n<code>{item["value"]}</code>',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=back(back_data))


async def rules_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    rules_data = check_rules()

    if rules_data:
        keyboard = rules()
        await bot.edit_message_text(rules_data, chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, reply_markup=keyboard)
        return

    await call.answer(text='❌ Правила не были добавлены')


async def profile_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user = call.from_user
    TgConfig.STATE[user_id] = None
    user_info = check_user(user_id)
    balance = user_info.balance
    operations = select_user_operations(user_id)
    overall_balance = 0

    if operations:

        for i in operations:
            overall_balance += i

    items = select_user_items(user_id)
    await bot.edit_message_text(text=f"👤 <b>Профиль</b> — {user.first_name}\n🆔"
                                     f" <b>ID</b> — <code>{user_id}</code>\n"
                                     f"💳 <b>Баланс</b> — <code>{balance}</code> ₽\n"
                                     f"💵 <b>Всего пополнено</b> — <code>{overall_balance}</code> ₽\n"
                                     f" 🎁 <b>Куплено товаров</b> — {items} шт",
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id, reply_markup=profile(items),
                                parse_mode='HTML')


async def referral_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    referrals = check_user_referrals(user_id)
    await bot.edit_message_text(f'💚 Реферальная система\n'
                                f'🔗 Ссылка: https://t.me/aiogram_examination_bot?start={user_id}\n'
                                f'Количество рефералов: {referrals}\n'
                                f'📔 Реферальная система позволит Вам заработать деньги без всяких вложений. '
                                f'Необходимо всего лишь распространять свою реферальную ссылку и Вы будете получать'
                                f' пожизненно 5% от суммы пополнений Ваших рефералов на Ваш баланс бота.',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=back('profile'))


async def replenish_balance_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    message_id = call.message.message_id

    if EnvKeys.CLIENT_TOKEN and EnvKeys.RECEIVER_TOKEN is not None:
        TgConfig.STATE[f'{user_id}_message_id'] = message_id
        TgConfig.STATE[user_id] = 'process_replenish_balance'
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text='💰 Введите сумму для пополнения:',
                                    reply_markup=back('profile'))
        return

    await call.answer('Пополнение не было настроено')


async def process_replenish_balance(message: Message):
    bot, user_id = await get_bot_user_ids(message)

    text = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if not text.isdigit() or int(text) < 20 or int(text) > 10000:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text="❌ Неверная сумма пополнения. "
                                         "Сумма пополнения должна быть числом не меньше 20₽ и не более 10 000₽",
                                    reply_markup=back('replenish_balance'))
        return

    label, url = quick_pay(message)
    start_operation(user_id, text, label)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text=f'Вы пополняете баланс на сумму {text}₽. '
                                     f'Нажмите «Оплатить» для перехода на сайт платежной системы.\n\n'
                                     f'❗️ После оплаты нажмите кнопку «Проверить»',
                                reply_markup=payment_menu(url, label))


async def checking_payment(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    message_id = call.message.message_id
    label = call.data[6:]
    info = select_unfinished_operations(label)

    if info:
        operation_value = info[0]
        payment_status = await check_payment_status(label)

        if payment_status == "success":
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            referral_id = get_user_referral(user_id)
            finish_operation(label)

            if referral_id:
                referral_operation = round(0.05 * operation_value)
                update_balance(referral_id, referral_operation)
                await bot.send_message(referral_id,
                                       f'✅ Вы получили {referral_operation}₽ '
                                       f'от вашего реферал {call.from_user.first_name}',
                                       reply_markup=close())

            create_operation(user_id, operation_value, formatted_time)
            update_balance(user_id, operation_value)
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=message_id,
                                        text=f'✅ Баланс пополнен на {operation_value}₽',
                                        reply_markup=back('profile'))
        else:
            await call.answer(text='❌ Оплата не прошла успешно')
    else:
        await call.answer(text='❌ Счет не найден')


async def check_sub_to_channel(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    chat = check_channel()
    parsed_url = urlparse(chat)
    channel_username = parsed_url.path.lstrip('/')
    helper = check_helper()
    chat_member = await bot.get_chat_member(chat_id='@' + channel_username, user_id=call.from_user.id)

    if await check_sub_channel(chat_member):
        user = check_user(call.from_user.id)
        role = user.role_id
        keyboard = main_menu(role, chat, helper)
        await bot.edit_message_text('⛩️ Основное меню', chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, reply_markup=keyboard)
    else:
        await call.answer(text='Вы не подписались')


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start,
                                commands=['start'])

    dp.register_callback_query_handler(shop_callback_handler,
                                       lambda c: c.data == 'shop')
    dp.register_callback_query_handler(dummy_button,
                                       lambda c: c.data == 'dummy_button')
    dp.register_callback_query_handler(profile_callback_handler,
                                       lambda c: c.data == 'profile')
    dp.register_callback_query_handler(rules_callback_handler,
                                       lambda c: c.data == 'rules')
    dp.register_callback_query_handler(check_sub_to_channel,
                                       lambda c: c.data == 'sub_channel_done')
    dp.register_callback_query_handler(replenish_balance_callback_handler,
                                       lambda c: c.data == 'replenish_balance')
    dp.register_callback_query_handler(referral_callback_handler,
                                       lambda c: c.data == 'referral_system')
    dp.register_callback_query_handler(bought_items_callback_handler,
                                       lambda c: c.data == 'bought_items')
    dp.register_callback_query_handler(back_to_menu_callback_handler,
                                       lambda c: c.data == 'back_to_menu')
    dp.register_callback_query_handler(close_callback_handler,
                                       lambda c: c.data == 'close')

    dp.register_callback_query_handler(navigate_categories,
                                       lambda c: c.data.startswith('categories-page_'))
    dp.register_callback_query_handler(navigate_bought_items,
                                       lambda c: c.data.startswith('bought-goods-page_'))
    dp.register_callback_query_handler(navigate_goods,
                                       lambda c: c.data.startswith('goods-page_'))
    dp.register_callback_query_handler(bought_item_info_callback_handler,
                                       lambda c: c.data.startswith('bought-item:'))
    dp.register_callback_query_handler(items_list_callback_handler,
                                       lambda c: c.data.startswith('category_'))
    dp.register_callback_query_handler(item_info_callback_handler,
                                       lambda c: c.data.startswith('item_'))
    dp.register_callback_query_handler(buy_item_callback_handler,
                                       lambda c: c.data.startswith('buy_'))
    dp.register_callback_query_handler(checking_payment,
                                       lambda c: c.data.startswith('check_'))

    dp.register_message_handler(process_replenish_balance,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'process_replenish_balance')
