import logging


from aiogram import Bot, Dispatcher, types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.dispatcher import FSMContext

from aiogram.utils import executor

import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup




########   #####  ####### ######

########  ##   ## ##      #

##       ##    ## ######  ######

##       ##    ## ##      #    #

##       ##    ## ####### ######


# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ --- #

game_state = False  # True - идет игра, false - пассивная

registration_state = False  # True - регистрация идет, false - пассивная

players = dict()  # Ключ: ID игрока, значение: объект класса Player

quantity = 0

used = []

roles = dict()  # Ключ: роль, значение: ID игрока

mafioso_list = []

reg_message_id = None

game_chat_id = None

last_message_id = dict()  # Ключ: id игрока, значение: последний id сообщения


# --- КОНСТАНТЫ --- #

BOT_TOKEN = "8204427695:AAFGdX5h7JjNye8mk1F0ZHhmR2Vp0Gw17M0"

REGISTRATION_TIME = 60  # В секундах

REQUIRED_PLAYERS = 1

LEADERS_INNOCENTS = ['detective']

SPECIAL_INNOCENTS = ['doctor', 'prostitute']

SPECIAL_MAFIOSI = ['godfather']

OTHERS = ['maniac']


# Инициализация бота и диспетчера

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot)


QUANTITY_OF_ROLES = {

    1: '0 0 0 1 0 0', 2: '1 0 0 1 0 0', 3: '1 1 0 1 0 0', 4: '1 1 0 2 0 0', 5: '1 2 0 2 0 0',

    6: '1 3 0 2 0 0', 7: '1 2 1 3 0 0', 8: '1 3 1 2 1 0', 9: '1 3 1 3 1 0', 10: '1 3 1 3 1 1',

    11: '1 5 1 2 1 1', 12: '1 5 2 2 1 1', 13: '1 6 2 2 1 1', 14: '1 6 2 3 1 1', 15: '1 7 2 3 1 1',

    16: '1 7 2 4 1 1'

}

ROLES_PRIORITY = ['prostitute', 'doctor', 'mafioso', 'detective', 'maniac', 'godfather', 'innocent']

ROLE_GREETING = {

    "Detective": '\n'.join(["Ты Детектив Дилан Бернс. Твоя цель - спасти невиновных и уничтожить мафию.",

                            "Твоя специальная способность - проверка карты или убийство кого-то ночью.",

                            "Удачи, детектив, пусть победит справедливость!"]),

    "Doctor": '\n'.join(["Ты Доктор Смолдер Брэвстоун. Твоя цель - спасти невиновных и остаться живым.",

                         "Твоя специальная способность - лечение одного человека ночью.",

                         "Удачи, доктор, пусть победит справедливость!"]),

    "Prostitute": '\n'.join(["Ты проститутка Слоан Джайлс",

                             "Твоя цель - выжить, однако ты помогаешь невиновным.",

                             "Твоя специальная способность - отключить одного игрока на один раунд ночью.",

                             "Удачи, Слоан!"]),

    "Godfather": '\n'.join(["Ты крестный отец Витторе Гуаренте.",

                            "Твоя цель - уничтожить невиновных и помочь мафии.",

                            "Твоя специальная способность - отключить одного игрока в качестве избирателя.",

                            "Удачи, крестный отец, пусть темные силы победят!"]),

    "Maniac": '\n'.join(["Ты маньяк Фрэнк МакСтайн. Твоя цель - убить всех в городе.",

                         "Ты можешь убить одного игрока ночью.",

                         "Удачи, маньяк, пусть победят силы безумия!"]),

    "Innocent": '\n'.join(["Ты Невиновный. Ты создание дня, поэтому ночью ты всегда спишь.",

                           "Твоя цель - уничтожить мафию в своем городе.",

                           "Удачи, невиновный, пусть победит закон!"]),

    "Mafioso": '\n'.join(["Ты мафиози. Твоя специальная способность - убить одного игрока ночью.",

                          "Однако помни, что сотрудничество с другими мафиози для тебя крайне важно.",

                          "Удачи, мафиози, пусть победят темные силы!"])

}


API_TOKEN = "647431231asdasidalksjdlasd"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)



class Player:

    def __init__(self, user):

        self.ID = user.id

        self.name = user.first_name + (' ' + user.last_name if user.last_name else '')

        self.nick = user.username

        self.card = None

        self.is_alive = True

        self.is_abilities_active = True

        self.can_be_killed = True

        self.able_to_vote = True

        self.able_to_discuss = True

        self.chat_id = None



def distribute_roles():

    global roles

    global players

    global QUANTITY_OF_ROLES

    global LEADERS_INNOCENTS

    global SPECIAL_MAFIOSI

    global SPECIAL_INNOCENTS

    global OTHERS

    global quantity

    global mafioso_list


    print('Раздача ролей...')


    roles_q = list(map(int, QUANTITY_OF_ROLES[quantity].split(' ')))


    leaders_innocents = random.sample(LEADERS_INNOCENTS, roles_q[0])

    special_innocents = random.sample(SPECIAL_INNOCENTS, roles_q[2])

    special_mafiosi = random.sample(SPECIAL_MAFIOSI, roles_q[4])

    others = random.sample(OTHERS, roles_q[5])


    rand_players = [i.ID for i in players.values()]

    random.shuffle(rand_players)


    ind = 0

    for i in range(len(leaders_innocents)):

        players[rand_players[ind]].card = leaders_innocents[i].capitalize()

        roles[leaders_innocents[i].capitalize()] = rand_players[ind]

        ind += 1


    for i in range(len(special_innocents)):

        players[rand_players[ind]].card = special_innocents[i].capitalize()

        roles[special_innocents[i].capitalize()] = rand_players[ind]

        ind += 1


    for i in range(len(special_mafiosi)):

        players[rand_players[ind]].card = special_mafiosi[i].capitalize()

        roles[special_mafiosi[i].capitalize()] = rand_players[ind]

        ind += 1


    for i in range(len(others)):

        players[rand_players[ind]].card = others[i].capitalize()

        roles[others[i].capitalize()] = rand_players[ind]

        ind += 1


    roles['Innocent'] = []

    for i in range(roles_q[1]):

        players[rand_players[ind]].card = 'Innocent'

        roles['Innocent'].append(rand_players[ind])

        ind += 1


    roles['Mafioso'] = []

    for i in range(roles_q[3]):

        players[rand_players[ind]].card = 'Mafioso'

        roles['Mafioso'].append(rand_players[ind])

        mafioso_list.append(

            '[' + players[rand_players[ind]].name + ']' + '(tg://user?id=' + str(rand_players[ind]) + ')')

        ind += 1


        print('Раздача ролей завершена:')

        for key, value in roles.items():

            if key == 'Mafioso':

                print('Мафиози: {}'.format(', '.join([players[i].name for i in value])))

            elif key == 'Innocent':

                print('Невиновные: {}'.format(', '.join([players[i].name for i in value])))

            else:

                print(key + ': ' + players[value].name)


    # Эти условия для отладки, так как ситуация без мафии/невиновных противоречит правилам

    if not roles['Mafioso']:

        del roles['Mafioso']


    if not roles['Innocent']:

        del roles['Innocent']



def send_roles(bot):

    global roles

    global mafioso_list

    global players

    global ROLE_GREETING

    global last_message_id


    print('Отправка ролей...')


    for role, player in roles.items():

        if role == 'Mafioso':

            for pl in player:

                bot.send_message(chat_id=pl, text=ROLE_GREETING[role])

                if len(mafioso_list) &gt; 1:

                    bot.send_message(chat_id=pl, text='Другие мафиози: \n{}'.format(

                        '\n'.join(i for i in mafioso_list if not (str(pl) in i))),

                                     parse_mode='Markdown')

                last_message_id[pl] += 1

        elif role == 'Innocent':

            for pl in player:

                bot.send_message(chat_id=pl, text=ROLE_GREETING[role])

                last_message_id[pl] += 1

        else:

            bot.send_message(chat_id=player, text=ROLE_GREETING[role])

            last_message_id[player] += 1


    print('Роли успешно отправлены')



# Функции ролей

# ВАЖНО: названия функций такие же, как и роли, в нижнем регистре

def detective(bot):

    global roles

    global players


    print('Детектив проснулся')


    check_or_shoot = InlineKeyboardMarkup(

        [[InlineKeyboardButton('Выстрел', callback_data='detective_shoot'),

          InlineKeyboardButton('Проверить личность', callback_data='detective_check')]])


    bot.send_message(chat_id=roles['Detective'], text='Ты чувствуешь себя миролюбивым сегодня?',

                     reply_markup=check_or_shoot)

    last_message_id[roles['Detective']] += 1



def mafioso(bot):

    global roles

    global players

    global mafioso_list


    print('Мафиози проснулись')


    shoot_voting = []

    for role, _id in roles.items():

        if role == 'Innocent':

            for inn in _id:

                shoot_voting.append([InlineKeyboardButton(players[inn].name, callback_data='maf_kill:{}'.format(inn))])

        elif role != 'Mafioso':

            shoot_voting.append([InlineKeyboardButton(players[_id].name, callback_data='maf_kill:{}'.format(_id))])


    for i in roles['Mafioso']:

        bot.send_message(chat_id=i, text='Выберите цель внимательно',

                         reply_markup=InlineKeyboardMarkup(shoot_voting))

        last_message_id[i] += 1



def innocent():

    print('Невиновные все еще спят!')



# Основной код

def game(bot, chat_id):

    global game_state

    global players

    global roles

    global ROLES_PRIORITY


    game_state = True

    print('Игра началась')

    bot.send_message(chat_id=chat_id, text='Игра началась. Пусть победит сильнейший.')


    distribute_roles()

    send_roles(bot)


    ordered_roles = sorted(roles.keys(),

                           key=lambda x: ROLES_PRIORITY.index(x.lower()))


    for i in ordered_roles:

        exec(i.lower() + '(bot)')  # Функции для каждой роли названы так же, как и сами роли



# На команду '/game'

async def registration_command(message: types.Message, state: FSMContext):

  global game_state

  global quantity

  global registration_state

  global players

  global reg_message_id

  global game_chat_id


  if not (game_state or registration_state):

      await message.answer('И пусть удача всегда будет с вами')

      registration_state = True


      keyboard = [[InlineKeyboardButton('🤵‍♂️Присоединиться', url="https://t.me/chpokpokbot?start=Register")]]

      markup = InlineKeyboardMarkup(inline_keyboard=keyboard)


      reg_message_id = message.message_id + 2

      game_chat_id = message.chat.id

      await message.answer('🎉 *Регистрация активна!* 🎉', parse_mode="Markdown", reply_markup=markup)


      await dp.bot.pin_chat_message(chat_id=message.chat.id, message_id=reg_message_id, disable_notification=True)

  else:

      await message.answer('Игра уже идет')



# На команду '/stop'

async def stop_command(message: types.Message, state: FSMContext):

    global game_state

    global registration_state

    global quantity

    global players

    global mafioso_list

    global roles

    global reg_message_id


    if game_state or registration_state:

        await message.answer('¡Sí, señor!')


        if registration_state:

            await dp.bot.delete_message(chat_id=message.chat.id, message_id=reg_message_id)

            await dp.bot.delete_message(chat_id=message.chat.id, message_id=reg_message_id - 1)


        game_state = False

        registration_state = False


        quantity = 0

        players.clear()

        roles.clear()

        used.clear()

        mafioso_list.clear()


        await message.answer('Игра успешно отменена.')

    else:

        await message.answer('Нет активной игры для отмены :(')



# На команду '/start'

async def reg_player_command(message: types.Message, state: FSMContext):

    global registration_state

    global quantity

    global reg_message_id

    global game_chat_id

    global last_message_id


    if registration_state:

        new_user = Player(message.from_user)


        if new_user.ID in used:

            await message.answer('Вы уже зарегистрированы. Пожалуйста, подождите других игроков :)')

            return


        players[new_user.ID] = new_user

        quantity += 1


        print(f'Игрок {quantity}: {new_user.name}, {new_user.ID}')


        last_message_id[new_user.ID] = message.message_id

        used.append(new_user.ID)


        keyboard = [[InlineKeyboardButton('🤵‍♂️Присоединиться', url="https://t.me/chpokpokbott?start=Register")]]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)


        await dp.bot.edit_message_text(chat_id=game_chat_id, message_id=reg_message_id,

                                       text=f'Регистрация активна!\n\n*Зарегистрированные игроки:* \n'

                                            f'{", ".join([f"[{i.name}](tg://user?id={i.ID})" for _, i in players.items()])}\n\n'

                                            f'Итого: *{quantity}*',

                                       parse_mode="Markdown", reply_markup=markup)

    else:

        await message.answer('Регистрация сейчас не активна. Пожалуйста, используйте "/game", чтобы начать регистрацию.')

    

# На команду '/begin_game'

async def begin_game_command(message: types.Message, state: FSMContext):

    global quantity

    global registration_state

    global game_state

    global REQUIRED_PLAYERS

    global reg_message_id


    if game_state:

        await message.answer('Игра уже идет!')

        return


    if registration_state:

        if quantity &gt;= REQUIRED_PLAYERS:

            await message.answer('Регистрация успешно завершена! Игра начинается...')

            registration_state = False


            await dp.bot.delete_message(chat_id=message.chat.id, message_id=reg_message_id)

            await dp.bot.delete_message(chat_id=message.chat.id, message_id=reg_message_id - 1)


            await game(dp.bot, message.chat.id)

        else:

            await message.answer('\n'.join(['Слишком мало игроков :(',

                                             f'Текущее количество игроков: {quantity}',

                                             f'Необходимое количество игроков: {REQUIRED_PLAYERS}.']))

    else:

        await message.answer('Пожалуйста, используйте "/game", чтобы начать регистрацию.')





dp.register_message_handler(registration_command, commands=['game'])



dp.register_message_handler(stop_command, commands=['stop'])



dp.register_message_handler(reg_player_command, commands=['start'])



dp.register_message_handler(begin_game_command, commands=['begin_game'])



if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)
