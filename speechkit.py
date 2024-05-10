import logging

import requests

from info import IAM_TOKEN, FOLDER_ID, URL, URL_TTS, VOICE, EMOTION, GOOD_STATUS_KOD

logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)


def speach_to_text(data: bytes):  # ЫЫЫЫЫЫ тут я забыла как ставить тайпхинт... даже вспомнила про логическое
    # сложение с этой &, но не помогло (((
    params = '&'.join(['topic=general', f'folderId={FOLDER_ID}', 'lang=ru-Ru'])
    url = f"{URL}{params}"
    headers = {'Authorization': f'Bearer {IAM_TOKEN}'}
    decoded_data = requests.post(url=url, headers=headers, data=data).json()
    if decoded_data.get('error_code') is None:
        return True, decoded_data.get('result')
    else:
        logging.debug(f'При запросе Speechkit произошла ошибка: {decoded_data["error_code"]}')
        return False, f'При запросе к Speechkit произошла ошибка: {decoded_data["error_code"]}'


def text_to_speach(text: str):
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': VOICE,
        'emotion': EMOTION,
        'folderId': FOLDER_ID,
    }

    try:
        response = requests.post(
            URL_TTS,
            headers=headers,
            data=data
        )

        if response.status_code == GOOD_STATUS_KOD:
            return True, response.content
        else:
            return False, f"При запросе в SpeechKit возникла ошибка {response.status_code}"

    except Exception as e:
        logging.debug(f'При запросе в SpeechKit возникла ошибка {e}')
        return False, f"При запросе в SpeechKit возникла ошибка {e}"
