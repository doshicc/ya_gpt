import requests
import logging
import math

from info import IAM_TOKEN, FOLDER_ID, URL_COUNT_TOKEN, NAME_GPT_MODEL, MAX_USER_STT_BLOCKS
from db import get_user_data


logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)


# подсчитываем количество токенов в сообщениях
def count_gpt_tokens(messages: list) -> int:
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/{NAME_GPT_MODEL}",
        "messages": messages
    }
    try:
        return len(requests.post(url=URL_COUNT_TOKEN, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(f'Произошла ошибка при подсчете токенов: {e}')
        return 0


def is_stt_block_limit(duration: int, user_id: int) -> int:
    audio_blocks = math.ceil(duration / 15)
    user_data = get_user_data(user_id)
    all_blocks = user_data['stt_blocks'] + audio_blocks
    return all_blocks
