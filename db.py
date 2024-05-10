import sqlite3
import logging
import json

from info import DATABASE_NAME, TABLE_NAME, SYSTEM_PROMPT


logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
)


# подключение/создание базы данных
def create_db(database_name: str = DATABASE_NAME):
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()


def execute_query(sql_query: str, data: tuple = None, database_name: str = DATABASE_NAME):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)
            connection.commit()

    except Exception as e:
        logging.debug(f'Ошибка при изменении данных в бд: {e}')


def execute_selection_query(sql_query: str, data: tuple = None, database_name: str = DATABASE_NAME) -> list:
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)
            row = cursor.fetchall()

            return row
    except Exception as e:
        logging.debug(f'Данные не были получены из бд. Ошибка: {e}')


def create_table(table_name: str = TABLE_NAME):
    sql_query = (
        f'CREATE TABLE IF NOT EXISTS {table_name} '
        f"(id INTEGER PRIMARY KEY, "
        f"user_id INTEGER, "
        f"tokens INTEGER, "
        f"tts_symbols INTEGER,"
        f"stt_blocks INTEGER,"
        f"messages TEXT);"
    )

    execute_query(sql_query)


def is_user_in_db(user_id: int, table_name: str = TABLE_NAME) -> bool:
    sql_query = f'SELECT user_id FROM {table_name} WHERE user_id=?;'
    result = execute_selection_query(sql_query, (user_id,))
    return bool(result)


def get_all_from_table() -> list:
    sql_query = f'SELECT * FROM {TABLE_NAME};'
    res = execute_selection_query(sql_query)
    return res


def add_new_user(user_id: int, table_name: str = TABLE_NAME):
    if not is_user_in_db(user_id):
        sql_query = (
            f'INSERT INTO {table_name} (user_id, tokens, tts_symbols, stt_blocks, messages) '
            f'VALUES (?, 0, 0, 0, ?);'
        )
        json_values = json.dumps([{'role': 'system', 'text': SYSTEM_PROMPT}])
        execute_query(sql_query, (user_id, json_values))
        logging.info(f'Юзер {user_id} добавлен в таблицу')
    else:
        logging.info(f'Пользователь {user_id} уже добавлен в таблицу')


def get_user_data(user_id: int, table_name: str = TABLE_NAME) -> dict:
    sql_query = f'SELECT * FROM {table_name} WHERE user_id = ?;'
    row = execute_selection_query(sql_query, (user_id,))[0]
    result = {'tokens': row[2],
              'tts_symbols': row[3],
              'stt_blocks': row[4],
              'messages': json.loads(row[5])}
    return result


def update_row(user_id: int, column_name: str, new_value: int | str, table_name: str = TABLE_NAME):
    sql_query = f'UPDATE {table_name} SET {column_name} = ? WHERE user_id = ?;'
    execute_query(sql_query, (new_value, user_id))
    logging.info(f'{column_name} поменялось на {new_value} у пользователя {user_id}')
