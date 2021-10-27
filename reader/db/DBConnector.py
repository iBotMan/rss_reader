""" A module for working with a cache database """
from os import path
import sqlite3

DIRECTORY = path.abspath(path.dirname(__file__))
DB_NAME = 'rss_cash.db'


class SQLite:
    """ Creates a context manager for working with Sqlite """

    def __init__(self, file='rss_cash.db'):
        self.file = path.join(DIRECTORY, file)

    def __enter__(self):
        self.connect = sqlite3.connect(self.file)
        self.connect.row_factory = sqlite3.Row
        return self.connect.cursor()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connect.commit()
        self.connect.close()


def init_cash_db(item_obj) -> bool:
    """The function creates an sqlite database based on the received fields of the item object"""

    fields = ''
    for field in item_obj.get_fields():
        fields += field + ' TEXT,'

    fields = fields[:len(fields) - 1]
    fields = fields.replace('guid TEXT', 'guid TEXT NOT NULL UNIQUE')

    with SQLite() as cursor:
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS ITEMS({fields}); """)
        cursor.execute(f"""CREATE INDEX IF NOT EXISTS filter_date on ITEMS (filter_date); """)
        cursor.execute(f"""CREATE INDEX IF NOT EXISTS source_filter_date on ITEMS (source, filter_date); """)
    return True


def insert(item) -> bool:
    """The function saves the received ITEM to the cache database"""

    with SQLite() as cursor:
        result = cursor.execute('select guid from ITEMS where guid = ?', [item.guid])
        if result.fetchone() is None:
            column_list = ''
            values_list = ''
            serialize_data = item.serialize()
            for key in serialize_data:
                column_list += f'{key}, '
                values_list += f'?, '
            column_list = column_list[:len(column_list) - 2]
            values_list = values_list[:len(values_list) - 2]
            q_text = f"INSERT INTO ITEMS({column_list}) VALUES({values_list});"
            cursor.execute(q_text, [value for value in serialize_data.values()])
    return True


def insert_many(items_list: list) -> bool:
    """The function saves the received ITEMS LIST to the cache database"""

    column_list = ''
    values_list = ''
    for key in items_list[0].serialize():
        column_list += f'{key}, '
        values_list += f'?, '
    column_list = column_list[:len(column_list) - 2]
    values_list = values_list[:len(values_list) - 2]
    q_text = f"INSERT OR REPLACE INTO ITEMS({column_list}) VALUES({values_list});"

    with SQLite() as cursor:
        for item in items_list:
            cursor.execute(q_text, [val for val in item.serialize().values()])
    return True


def select_items_from_cash(parameters: dict, limit=0) -> list:
    """the function retrieves data from the database cache
    and returns a list of dictionaries for creating ITEMS"""

    q_text = """SELECT * from ITEMS """
    if parameters:
        request_conditions = ''
        for key in parameters.keys():
            request_conditions += f'{key}= ? and '

        if request_conditions:
            request_conditions = request_conditions[:len(request_conditions) - 4]
            q_text += 'Where ' + request_conditions

    q_text += ' order by source, filter_date '
    if limit:
        q_text += f'LIMIT {limit}'

    result = []
    with SQLite() as cursor:
        fetchall = cursor.execute(q_text, [val for val in parameters.values()])
        for row in fetchall:
            body = dict()
            for key in row.keys():
                if row[key]:
                    body[key] = row[key]
            result.append(body)

    return result


def delete(item) -> bool:
    """Removes ITEM from the database cache by guid"""

    with SQLite() as cursor:
        cursor.execute('delete from ITEMS where guid = ?', [item.guid])
    return True
