import os
import json
import requests
import time
import logging

from dotenv import load_dotenv


logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)

IAM_TOKEN_PATH = 'iam_token.json'


# получение нового iam_token
def create_new_token():
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {
        "Metadata-Flavor": "Google"
    }
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == GOOD_STATUS_KOD:
            token_data = response.json()  # вытаскиваем из ответа iam_token
            # добавляем время истечения iam_token к текущему времени
            token_data['expires_at'] = time.time() + token_data['expires_in']
            # записываем iam_token в файл
            with open(IAM_TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)
            logging.info("Получен новый iam_token")
        else:
            logging.error(f"Ошибка получения iam_token. Статус код: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка получения iam_token: {e}")


# чтение iam_token из файла
def get_creds():
    try:
        # чтение iam_token
        with open(IAM_TOKEN_PATH, 'r+') as f:
            file_data = json.load(f)
        # если срок годности истёк
        if time.time() >= file_data['expires_in']:
            logging.info("Срок годности iam_token истёк")
            # получаем новый iam_token
            create_new_token()
    except:
        # если что-то пошло не так - получаем новый iam_token
        create_new_token()

    # чтение iam_token
    with open(IAM_TOKEN_PATH, 'r') as f:
        file_data = json.load(f)
        iam_token = file_data["access_token"]

    return iam_token


# для db
DATABASE_NAME = 'users.db'

TABLE_NAME = 'users'

SYSTEM_PROMPT = (
    'Ты голосовой/текстовой помощник, который любит котиков. Разговаривай просто, кратко и мило, '
    'как добрый друг. Не надр ничего объяснять пользователю, он итак все знает.'
)

# для main
MAX_USERS = 5

GREETING = (
    'Здравствуйте, уважаемый пользователь! Добро пожаловать в наш дружелюбный голосовой помощник. Мы рады '
    'видеть вас и готовы помочь вам с любыми вопросами и задачами. Если вдруг что-то не понятно, воспользуйтесь '
    'командой /help'
)

TEXT_APOLOGIES = (
    'Уважаемый пользователь, Извините, мы столкнулись с превышением лимитов. Если это '
    'поднимет вам настроение, воспользуйтесь командой /send_cats и посмотрите на котиков. Спасибо за '
    'понимание.'
)

TEXT_HELP = (
    'Скажите приветствие и представьтесь. Задайте вопрос или попросите помощи. Важно помнить, '
    'что у голосового/текстового помощника есть ограничения. Он не сможет ответить на все вопросы и решить все'
    'проблемы. Но бот постарается помочь вам и поддержать беседу. Вы можете использовать как и аудио так и '
    'текстовые сообщения. Также присутствуют команды /tts и /stt , которые необходимы для озвучки и распознования '
    'текста соответственно.'
)

ADMINS = [5748890751, 5472536733]

# только так к сожалению, ибо api нынче платные пошли. а из теории брать не хочется
CATS_URl = [('https://ru.freepik.com/free-photo/cute-cat-relaxing-indoors_58601658.htm#query=%D0%BA%D0%BE%D1%88%D0%BA'
             '%D0%B8&position=3&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e-1601fedd5d4c'),
            ('https://ru.freepik.com/free-photo/adorable-cat-relaxing-indoors_58601477.htm#query=%D0%BA%D0%BE%D1%88%D0'
             '%BA%D0%B8&position=9&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e-1601fedd5d4c'),
            ('https://ru.freepik.com/premium-photo/cute-orange-cat-near-window_13818162.htm#query=%D0%BA%D0%BE%D1%88'
             '%D0%BA%D0%B8&position=15&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e-1601fedd5d4c'),
            ('https://ru.freepik.com/premium-photo/close-up-portrait-of-a-cat_117663738.htm#query=%D0%BA%D0%BE%D1%88'
             '%D0%BA%D0%B8&position=33&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e-1601fedd5d4c'),
            ('https://ru.freepik.com/free-photo/close-up-on-adorable-kitten-sleeping_65610197.htm#page=2&query=%D0%BA'
             '%D0%BE%D1%88%D0%BA%D0%B8&position=6&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e'
             '-1601fedd5d4c'),
            ('https://ru.freepik.com/premium-photo/portrait-of-a-cute-ginger-cat-sitting_9729902.htm#page=2&query=%D0%B'
             'A%D0%BE%D1%88%D0%BA%D0%B8&position=21&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e-1601fedd5'
             'd4c'),
            ('https://ru.freepik.com/free-photo/close-up-portrait-on-beautiful-cat_21194148.htm#page=2&query=%D0%BA%D0'
            '%BE%D1%88%D0%BA%D0%B8&position=19&from_view=keyword&track=ais&uuid=61ace5a3-1846-4c69-ba9e-1601fedd5d4c')]

MAX_USER_TTS_SYMBOLS = 1500

MAX_USER_GPT_TOKENS = 3000


# для ya_gpt
load_dotenv()
IAM_TOKEN = get_creds()

FOLDER_ID = os.getenv('FOLDER_ID')

NAME_GPT_MODEL = 'yandexgpt-lite'

TEMPERATURE = 0.6

MAX_GPT_TOKENS = 500

URL_GPT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

GOOD_STATUS_KOD = 200

# для speechkit
URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?'

URL_TTS = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

VOICE = 'jane'

EMOTION = 'good'

# для validators.py
URL_COUNT_TOKEN = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"


MAX_USER_STT_BLOCKS = 12
