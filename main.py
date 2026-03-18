# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime
import time

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api

import message_list

token = os.environ.get("VK_TOKEN", "")

vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

permitted_user = []
mailing_list = []
week_info = []

elder_id = 408637275
mailing_flag = 0
message_flag = 0


def load_user_list(path):
    users = []
    if not os.path.exists(path):
        return users
    with open(path, 'r') as f:
        lines = f.readlines()
    count = int(lines[0])
    for i in range(1, count + 1):
        users.append(int(lines[i]))
    return users


def save_user_list(path, users):
    with open(path, 'w') as f:
        f.write(str(len(users)) + "\n")
        for uid in users:
            f.write(str(uid) + "\n")


permitted_user = load_user_list('id_list.txt')
mailing_list = load_user_list('id_board.txt')


def send_message(session, id_type, user_id, message=None, attachment=None, keyboard=None):
    session.method('messages.send', {
        id_type: user_id,
        'message': message,
        'random_id': random.randint(-2147483648, 2147483648),
        'attachment': attachment,
        'keyboard': keyboard,
    })


def create_keyboard(response):
    keyboard = VkKeyboard(one_time=False)

    if response in ('default_1', 'default_2', 'elder_1', 'elder_2'):
        if response in ('elder_1', 'elder_2'):
            keyboard.add_button('Отправить сообщение группе', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
        keyboard.add_button('Расписание на сегодня', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Расписание на завтра', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Материал', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Преподаватели', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Закрыть', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    if response == 'закрыть':
        return keyboard.get_empty_keyboard()

    return keyboard.get_keyboard()


def week_parity():
    week_number = datetime.utcnow().isocalendar()[1]
    return 1 if week_number % 2 == 0 else 0


SCHEDULE = {
    1: {  # even week (parity=1)
        1: message_list.msg1_monday,
        2: message_list.msg1_tuesday,
        3: message_list.msg1_wednesday,
        4: message_list.msg1_thursday,
        5: message_list.msg1_friday,
        6: message_list.msg1_saturday,
        0: 'Выходной',
    },
    0: {  # odd week (parity=0)
        1: message_list.msg2_monday,
        2: message_list.msg2_tuesday,
        3: message_list.msg2_wednesday,
        4: message_list.msg2_thursday,
        5: message_list.msg2_friday,
        6: message_list.msg2_saturday,
        0: 'Выходной',
    },
}


def get_schedule(day_offset=0):
    parity = week_parity()
    weekday = (int(time.strftime('%w', time.localtime())) + day_offset) % 7
    return SCHEDULE[parity][weekday]


def get_keyboard_type(user_id, response):
    if response == 'закрыть':
        return 'закрыть'
    is_elder = (user_id == elder_id)
    prefix = 'elder' if is_elder else 'default'
    suffix = '2' if user_id in mailing_list else '1'
    return f'{prefix}_{suffix}'


while True:
    try:
        for event in longpoll.listen():
            if not (event.type == VkEventType.MESSAGE_NEW and event.from_user and not event.from_me):
                continue

            response = event.text.lower()
            user_id = event.user_id
            key_base = get_keyboard_type(user_id, response)
            keyboard = create_keyboard(key_base)

            if user_id not in permitted_user:
                send_message(vk_session, 'user_id', user_id, message=message_list.msg1, keyboard=keyboard)
                permitted_user.append(user_id)
            else:
                if response == 'расписание на сегодня':
                    send_message(vk_session, 'user_id', user_id, message=get_schedule(0), keyboard=keyboard)
                elif response == 'расписание на завтра':
                    send_message(vk_session, 'user_id', user_id, message=get_schedule(1), keyboard=keyboard)
                elif response == 'материал':
                    send_message(vk_session, 'user_id', user_id, message=message_list.msg3, keyboard=keyboard)
                elif response == 'преподаватели':
                    send_message(vk_session, 'user_id', user_id, message=message_list.msg10, keyboard=keyboard)
                elif response == 'закрыть':
                    send_message(vk_session, 'user_id', user_id, message='Ok', keyboard=keyboard)
                elif user_id == elder_id and response == 'отправить сообщение группе':
                    send_message(vk_session, 'user_id', user_id, message=message_list.msg8, keyboard=keyboard)
                    mailing_flag = 1
                elif user_id == elder_id and mailing_flag == 1:
                    mailing_message = event.text
                    message_flag = 1
                    send_message(vk_session, 'user_id', user_id, message=message_list.msg9, keyboard=keyboard)
                else:
                    send_message(vk_session, 'user_id', user_id, message=message_list.msg2, keyboard=keyboard)

            if mailing_flag == 1 and message_flag == 1:
                for uid in permitted_user:
                    send_message(vk_session, 'user_id', uid, message=mailing_message)
                mailing_flag = 0
                message_flag = 0

            save_user_list('id_list.txt', permitted_user)

    except Exception as e:
        print('error', e)
