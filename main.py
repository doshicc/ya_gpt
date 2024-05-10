import logging
import os
import random
import json

import telebot
from dotenv import load_dotenv
from telebot.types import Message

from db import create_db, create_table, is_user_in_db, get_all_from_table, add_new_user, get_user_data, update_row
from info import MAX_USERS, GREETING, TEXT_APOLOGIES, TEXT_HELP, ADMINS, CATS_URl, MAX_USER_GPT_TOKENS, \
    MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, SYSTEM_PROMPT
from keyboard import create_keyboard
from speechkit import speach_to_text, text_to_speach
from validators import count_gpt_tokens, is_stt_block_limit
from ya_gpt import ask_ya_gpt

create_db()
create_table()

logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['start'])
def say_start(message: Message):
    user_id = message.from_user.id
    if not is_user_in_db(user_id) and len(get_all_from_table()) > MAX_USERS:
        bot.send_message(user_id, TEXT_APOLOGIES, reply_markup=create_keyboard(['/send_cats']))
        return
    elif not is_user_in_db(message.from_user.id) and len(get_all_from_table()) < MAX_USERS:
        add_new_user(message.from_user.id)
    update_row(user_id, 'messages', json.dumps([{'role': 'system', 'text': SYSTEM_PROMPT}]))
    bot.send_message(user_id, GREETING, reply_markup=create_keyboard(['/stt', '/tts', '/help']))


@bot.message_handler(commands=['debug'])
def send_logs(message: Message):
    user_id = message.from_user.id
    if user_id in ADMINS:
        try:
            with open("logs.txt", "rb") as f:
                bot.send_document(message.chat.id, f)

        except Exception as e:
            bot.send_message(message.chat.id, f'Не удалось отправить файл {e}')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь админом. Если очень интересно обратитесь к @C4_H6_O6')


@bot.message_handler(commands=['tts'])
def voiceover(message: Message):
    bot.send_message(message.from_user.id, 'Отправь текст, а я его озвучу.')
    bot.register_next_step_handler(message, tts)


def tts(message: Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    request = message.text

    if len(request) + user_data['tts_symbols'] >= MAX_USER_TTS_SYMBOLS:
        bot.send_message(user_id, TEXT_APOLOGIES, reply_markup=create_keyboard(['/send_cats']))
    update_row(user_id, 'tts_symbols', len(request) + user_data['tts_symbols'])
    status, result = text_to_speach(request)

    if status:
        bot.send_voice(user_id, result)
    else:
        bot.send_message(user_id, result)


@bot.message_handler(commands=['stt'])
def recognition(message: Message):
    bot.send_message(message.from_user.id, 'Отправь голосовое, а я преобразую его в текст.')
    bot.register_next_step_handler(message, stt)


def stt(message: Message):
    user_id = message.from_user.id

    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    if is_stt_block_limit(message.voice.duration, user_id) >= MAX_USER_STT_BLOCKS:  # если пользователь вышел за пределы stt блоков
        bot.send_message(user_id, TEXT_APOLOGIES, reply_markup=create_keyboard(['/send_cats']))
        return

    update_row(user_id, 'stt_blocks', is_stt_block_limit(message.voice.duration, user_id))
    status, res = speach_to_text(file)  # получаем статус и результат

    if not status:  # если произошла какая-то ошибка отправдяем сообщение о ней и выходим из функции
        bot.send_message(user_id, res)
    else:
        bot.send_message(user_id, res)


@bot.message_handler(commands=['send_cats'])
def send_cats(message: Message):
    bot.send_photo(message.from_user.id, random.choice(CATS_URl))


@bot.message_handler(commands=['help'])
def say_help(message: Message):
    bot.send_message(message.from_user.id, TEXT_HELP, reply_markup=create_keyboard(['/stt', '/tts']))


@bot.message_handler(content_types=['text', 'voice'])
def process_request(message: Message):
    user_id = message.from_user.id  # достаем id
    user_data = get_user_data(user_id)
    user_collection = user_data['messages']  # достаем промты от нейронки и юзера и системный где-то там
    if count_gpt_tokens(user_collection) >= MAX_USER_GPT_TOKENS:  # проверяем не вышел ли пользователь за лимит токенов
        bot.send_message(user_id, TEXT_APOLOGIES, reply_markup=create_keyboard(['/send_cats']))
        return

    if message.content_type == 'voice':  # если юзер отправил голосовое
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)

        if is_stt_block_limit(message.voice.duration, user_id) >= MAX_USER_STT_BLOCKS:  # если пользователь вышел за пределы stt блоков
            bot.send_message(user_id, TEXT_APOLOGIES, reply_markup=create_keyboard(['/send_cats']))
            return
        update_row(user_id, 'stt_blocks', is_stt_block_limit(message.voice.duration, user_id))
        status, res = speach_to_text(file)  # получаем статус и результат

        if not status:  # если произошла какая-то ошибка отправдяем сообщение о ней и выходим из функции
            bot.send_message(user_id, res)
            return
        user_collection.append({'role': 'user', 'text': res})  # добавляем в messages юзера его запрос

    else:  # если это текст, то кладем текст
        user_collection.append({'role': 'user', 'text': message.text})

    update_row(user_id, 'tokens', count_gpt_tokens(user_collection))  # вносим в бд количество потраченных токенов

    answer = ask_ya_gpt(user_collection)  # получаем ответ от нейросети
    user_collection.append({'role': 'assistant', 'text': answer})
    update_row(user_id, 'messages', user_collection)  # обновляем messages

    if message.content_type == 'voice':  # если пользователь отправлял голсовое, то пробразуем ответ в голосовое
        if len(answer) + user_data['tts_symbols'] >= MAX_USER_TTS_SYMBOLS:
            bot.send_message(user_id, TEXT_APOLOGIES, reply_markup=create_keyboard(['/send_cats']))
        update_row(user_id, 'tts_symbols', len(answer) + user_data['tts_symbols'])
        status, result = text_to_speach(answer)

        if status:
            bot.send_voice(user_id, result)
        else:
            bot.send_message(user_id, result)

    else:
        bot.send_message(user_id, answer)  # если текст, то просто отправляем ответ


bot.polling(non_stop=True)
