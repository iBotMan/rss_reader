import logging
import unittest
import requests
import os
from stat import S_IREAD, S_IWUSR
from reader.models import Item
from reader.functions import Parser
from reader.db import DBConnector
from reader.functions import _create_logger
from datetime import datetime


class ParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser('https://realt.onliner.by/feed', str(datetime.now()).split()[0], 2, False)

    def test_create_parser(self):
        self.assertIsInstance(Parser(), Parser)
        self.assertIsInstance(Parser('https://realt.onliner.by/feed'), Parser)
        self.assertIsInstance(Parser('https://realt.onliner.by/feed', '2021-10-26', ), Parser)
        self.assertIsInstance(Parser('https://realt.onliner.by/feed', '2021-10-26', 2), Parser)
        self.assertIsInstance(Parser('https://realt.onliner.by/feed', '2021-10-26', 2, False), Parser)

    def test_create_logger(self):
        self.assertIsInstance(_create_logger(True), logging.Logger)
        self.assertIsInstance(_create_logger(False), logging.Logger)

    def test_update_cash_db(self):
        self.parser = Parser('https://realt.onliner.by/feed', '2021-10-26', 2, False)
        self.assertIsInstance(self.parser.update_cash_db(), list)

    def test_update_cash_db_raises(self):
        with self.assertRaises(requests.exceptions.InvalidURL):
            self.parser.source = 'https://google.com'
            self.parser.update_cash_db()

        with self.assertRaises(requests.exceptions.InvalidURL):
            self.parser.source = 'https://realt.onliner.by/rss'
            self.parser.update_cash_db()

    def test_get_items(self):
        self.assertIsInstance(self.parser.get_items(), list)

    def test_get_with_out_filter_date(self):
        self.parser.filter_date = ''
        self.assertIsInstance(self.parser.get_items(), list)

    def test_get_with_out_source(self):
        self.parser.source = ''
        self.assertIsInstance(self.parser.get_items(), list)

    def test_check_path_to_directory_raise(self):
        only_read_file = os.path.join(self.parser.directory, 'rss_temp.tmp')
        file = open(only_read_file, "w")
        file.close()
        os.chmod(only_read_file, S_IREAD)
        with self.assertRaises(PermissionError):
            self.parser.check_path_to_directory(self.parser.directory)
        if os.path.isfile(only_read_file):
            os.chmod(only_read_file, S_IWUSR)
            os.remove(only_read_file)

    def test_check_path_to_directory(self):
        self.parser.check_path_to_directory(self.parser.directory)


class ItemTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data = {
            'link': 'https://realt.onliner.by/2021/10/26/kak-obstavit-spalnyu',
            'guid': 'https://realt.onliner.by/2021/10/26/kak-obstavit-spalnyu',
            'pubdate': 'Tue, 26 Oct 2021 12:02:57 +0300',
            'filter_date': '2021-10-26',
            'language': 'ru',
            'title': 'Как обставить спальню в разных стилях, чтобы не получилась безвкусица. Советы от дизайнера',
            'description': 'Как думаете, существует ли идеальный интерьер спальни, в '
                           'котором приятно просыпаться каждое утро и чувствовать себя героем '
                           'какого-нибудь голливудского фильма?.Читать далее…',
            'html_description': '<p><a href="https://realt.onliner.by/2021/10/26/kak-obstavit-spalnyu">'
                                '<img src="https://content.onliner.by/news/thumbnail/'
                                '1b233fe4fd9c41c0e3c52149adea9c9e.jpeg" alt="" /></a></p><p>'
                                'Как думаете, существует ли идеальный интерьер спальни, '
                                'в котором приятно просыпаться каждое утро '
                                'и чувствовать себя героем какого-нибудь голливудского фильма?'
                                '</p><p><a href="https://realt.onliner.by/2021/10/26/'
                                'kak-obstavit-spalnyu">Читать далее…</a></p>',
            'source': 'https://realt.onliner.by/feed',
            'category': ['Интерьер'],
            'image_links': ['https://content.onliner.by/news/thumbnail/1b233fe4fd9c41c0e3c52149adea9c9e.jpeg'],
            'links': [],
        }
        self.item = Item(**self.test_data)

    def test_create_item(self):
        self.assertIsInstance(Item(**self.test_data), Item)

    def test_item_formatted_date1(self):
        pubdate = '2021-10-26 14:51:20.440933'
        result_data = pubdate.split()[0]
        self.item.pubdate = pubdate
        self.assertEqual(self.item.formatted_date(), result_data)

    def test_item_formatted_date2(self):
        result_data = str(datetime.now()).split()[0]
        self.item.pubdate = 'abracadabra'
        self.assertEqual(self.item.formatted_date(), result_data)

    def test_serialize(self):
        self.assertIsInstance(self.item.serialize(), dict)

    def test_get_html_template(self):
        self.assertIsInstance(self.item.get_html_template(), str)


class DBConnectorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.test_data = {
            'link': 'https://realt.onliner.by/2021/10/26/kak-obstavit-spalnyu',
            'guid': 'e3fae1d3-39c6-4246-af92-ad51cb126325',
            'pubdate': 'Tue, 26 Oct 2021 12:02:57 +0300',
            'filter_date': '2021-10-26',
            'language': 'ru',
            'title': 'Как обставить спальню в разных стилях, чтобы не получилась безвкусица. Советы от дизайнера',
            'description': 'Как думаете, существует ли идеальный интерьер спальни, в '
                           'котором приятно просыпаться каждое утро и чувствовать себя героем '
                           'какого-нибудь голливудского фильма?.Читать далее…',
            'html_description': '<p><a href="https://realt.onliner.by/2021/10/26/kak-obstavit-spalnyu">'
                                '<img src="https://content.onliner.by/news/thumbnail/'
                                '1b233fe4fd9c41c0e3c52149adea9c9e.jpeg" alt="" /></a></p><p>'
                                'Как думаете, существует ли идеальный интерьер спальни, '
                                'в котором приятно просыпаться каждое утро '
                                'и чувствовать себя героем какого-нибудь голливудского фильма?'
                                '</p><p><a href="https://realt.onliner.by/2021/10/26/'
                                'kak-obstavit-spalnyu">Читать далее…</a></p>',
            'source': 'https://realt.onliner.by/feed',
            'category': ['Интерьер'],
            'image_links': ['https://content.onliner.by/news/thumbnail/1b233fe4fd9c41c0e3c52149adea9c9e.jpeg'],
            'links': [],
        }
        self.item = Item(**self.test_data)

    def test_init_cash_db(self):
        self.assertEqual(DBConnector.init_cash_db(Item()), True)

    def test_insert(self):
        self.assertEqual(DBConnector.insert(self.item), True)

    def test_select_items_from_cash(self):
        parameters = {'filter_date': self.item.filter_date, 'source': self.item.source}
        limit = 1
        self.assertIsInstance(DBConnector.select_items_from_cash(parameters, limit), list)

    def test_delete(self):
        self.assertEqual(DBConnector.delete(self.item), True)


if __name__ == '__main__':
    unittest.main()
