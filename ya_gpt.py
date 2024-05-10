import requests
import logging

from info import IAM_TOKEN, NAME_GPT_MODEL, FOLDER_ID, TEMPERATURE, MAX_GPT_TOKENS, URL_GPT, GOOD_STATUS_KOD, IAM_TOKEN_PATH


logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)


def ask_ya_gpt(user_collection: list) -> str:
    headers = {'Authorization': f'Bearer {IAM_TOKEN}',
               'Content-Type': 'application/json'}
    data = {'modelUri':  f'gpt://{FOLDER_ID}/{NAME_GPT_MODEL}',
            "completionOptions": {
                "stream": False,
                "temperature": TEMPERATURE,
                "maxTokens": MAX_GPT_TOKENS
            },
            'messages': user_collection
            }

    try:
        response = requests.post(URL_GPT, headers=headers, json=data)

        if response.status_code != GOOD_STATUS_KOD:
            result = f'Ошибка при получении ответа от нейросети! Статус кода: {response.status_code}'
            logging.debug(f'Ошибка при получении ответа от GPT {response.status_code}')
            return result
        result = response.json()["result"]["alternatives"][0]["message"]["text"]

    except Exception as e:
        result = f'Произошла ошибка: {e}'
        logging.debug(f'Ошибка при получении ответа от GPT {e}')
    return result
