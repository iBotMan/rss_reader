""" Module of creation Parser, functions and action functions."""

import requests
from bs4 import BeautifulSoup
import logging
from reader.db.DBConnector import init_cash_db, select_items_from_cash
from reader.models import Item
from fpdf import FPDF

import os
from tempfile import gettempdir


def _create_logger(verbose):
    """Create logger function.
    Creates a logger considering the --verbose argument. """
    # Create a logger
    logger = logging.getLogger("rss_reader_logger")
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()

    file_log = os.path.abspath(os.path.dirname(__file__))
    file_log = os.path.join(file_log, "RSS_file_log.log")
    f_handler = logging.FileHandler(file_log)

    # Check --verbose argument
    if verbose:
        c_handler.setLevel(logging.DEBUG)
    else:
        c_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)

    return logger


class Parser:
    """Creates a Parser object."""
    """Makes a request by url and parse it into a List with Items"""

    def __init__(self, source=None, filter_date=None, limit=0, verbose=False):
        self.version = '1.5'
        self.source = source
        self.filter_date = filter_date
        self.limit = limit
        self.verbose = verbose
        self.logger = _create_logger(self.verbose)

        self.news_feed = []

        self.directory = os.path.abspath(os.path.dirname(__file__))
        self.pdf_directory = os.path.join(self.directory, "pdf")  # will save font files
        self.img_directory = gettempdir()  # or temp dir
        self.pdf_font = 'DejaVuSansCondensed.ttf'

    def __repr__(self):
        return f'Class Parser'

    @staticmethod
    def get_soup(xml, parser: str = "xml") -> BeautifulSoup:
        return BeautifulSoup(xml, parser)

    def update_cash_db(self) -> list:
        """The function receives XML by URL, parse it into ITEMS,
        saves it to the Caching Database and return list of ITEMS"""

        news_feed = []
        try:
            self.logger.info(f"Make request to {self.source}")
            response = requests.get(self.source, timeout=5)
        except requests.exceptions.ConnectionError:
            self.logger.error("Please, check your internet connection.")
            raise ConnectionError("Please, check your internet connection.")

        if response.status_code != 200:
            self.logger.error(f'Wrong answer {response.status_code}')
            raise requests.exceptions.InvalidURL(f'Wrong answer {response.status_code}')

        soup = self.get_soup(response.content)
        if soup.find('rss') is None:
            self.logger.error('Please ensure that the URL entered is correct')
            raise requests.exceptions.InvalidURL('Please ensure that the URL entered is correct')

        version = soup.find('rss')['version']
        if version != '2.0':
            self.logger.error('Wrong version of RSS-FEED')
            raise TypeError('Wrong version of RSS-FEED')

        head = {
            "title": soup.title.text,
            "version": soup.rss.get("version"),
            "language": getattr(soup.language, "text", ""),
            "description": getattr(soup.description, "text", ""),
        }

        tags = soup.find_all('item')
        for tag in tags:
            item_attrs = {
                "language": head['language'],
                "source": self.source,
                "link": tag.link.text,
                "guid": getattr(tag.guid, "text", tag.link.text),
                "title": tag.title.text,
                "pubdate": getattr(tag.pubDate, "text", ""),
                "category": getattr(tag.category, "text", ""),
                "html_description": getattr(tag.description, "text", ""),
                "description": '',
                "links": list(),
                "image_links": list(),
            }

            if item_attrs['html_description']:
                description_soup = self.get_soup(item_attrs['html_description'], "html.parser")
                item_attrs["description"] = description_soup.text
                for a_link in description_soup.findAll("a"):
                    if a_link.get("href") and a_link.get("href") != item_attrs['link']:
                        item_attrs['links'].append(a_link.get("href"))
                item_attrs['links'] = list(set(item_attrs['links']))

                for image in description_soup.findAll("img"):
                    if image.get("src"):
                        item_attrs['image_links'].append(image.get("src"))
                item_attrs['image_links'] = list(set(item_attrs['image_links']))

            item = Item(**item_attrs)
            item.save()
            news_feed.append(item)

        return news_feed

    def get_items(self):

        """The main function of the object.
        Initializes the Caching Database, updates the cache,
        and returns the ITEMS list according to the received parameters"""

        self.news_feed = []
        parameters = dict()

        try:
            self.logger.info("init RSS cash db")
            init_cash_db(Item())
        except Exception as exp:
            self.logger.error(f'Can`t init RSS cash db {exp}')
            raise Exception('Can`t init RSS cash db')

        if self.source:
            parameters['source'] = self.source
            self.news_feed = self.update_cash_db()

        if self.filter_date:
            parameters['filter_date'] = self.filter_date

        if self.source and (self.filter_date is None):
            if self.limit:
                self.news_feed = self.news_feed[:self.limit]
        else:
            self.logger.info("Get items from RSS cash db")
            self.news_feed = [Item(**body) for body in select_items_from_cash(parameters, self.limit)]

        self.logger.info(f"Return RSS feed with {len(self.news_feed)} item(s)")
        return self.news_feed

    def check_path_to_directory(self, user_path):

        """The function checks the paths to files and folders to work with saving ITEMS in PDF and HTML.
        Checks file availability and write permissions."""

        if not os.path.exists(user_path):
            self.logger.error(f'Path {user_path} not exists')
            return FileNotFoundError
        else:
            test_to_write = os.path.join(user_path, 'rss_temp.tmp')
            try:
                with open(test_to_write, 'w') as f:
                    f.write('')
                if os.path.isfile(test_to_write):
                    os.remove(test_to_write)
            except PermissionError as e:
                self.logger.error(e)
                raise PermissionError('NO Permission to write')

        if not os.path.exists(self.pdf_directory):
            os.mkdir(self.pdf_directory)

        font_path = os.path.join(self.pdf_directory, self.pdf_font)
        if not os.path.exists(font_path):
            picture_request = requests.get('https://github.com/iBotMan/fonts/raw/master/DejaVuSansCondensed.ttf',
                                           timeout=5)

            if picture_request.status_code == 200:
                with open(font_path, 'wb+') as f:
                    f.write(picture_request.content)
        return True

    def create_and_fill_pdf_file(self, user_path_to_pdf, items_list: list = None) -> os.path:

        """The function creates a PDF file from the resulting ITEMS list"""

        items = items_list if items_list is not None else self.news_feed
        if len(items) == 0:
            return ''
        """ Function for creating and filling in the pdf file with news.  """
        if not self.check_path_to_directory(user_path_to_pdf):
            return None

        self.logger.info("Creating pdf file with news.")
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_font('DejaVu', '', os.path.join(self.pdf_directory, 'DejaVuSansCondensed.ttf'), uni=True)
        pdf.set_margins(5, 13.5, 5)

        for news in items:
            pdf.add_page()
            pdf.set_font("DejaVu", size=16)
            pdf.set_text_color(255, 0, 0)
            _add_news_to_pdf_file(news, pdf, self.img_directory)

        path_to_pdf_file = os.path.join(user_path_to_pdf, "RSS_ITEMS.pdf")
        try:
            pdf.output(path_to_pdf_file, "F")
            self.logger.info(f"PDF file was created: {path_to_pdf_file}")
        except PermissionError as e:
            self.logger.error(e)
            raise e
        self.logger.info(f"PDF file was saved: {path_to_pdf_file}")
        return path_to_pdf_file

    def create_and_fill_html_file(self, user_path_to_html, items_list: list = None) -> os.path:

        """The function creates a HTML file from the resulting ITEMS list"""

        items = items_list if items_list is not None else self.news_feed
        if len(items) == 0:
            return ''
        """ Function for creating and filling in the html file with news.  """
        if not self.check_path_to_directory(user_path_to_html):
            return None
        body_template = f"""
            <!DOCTYPE html>
            <html lang="{self.news_feed[0].language}">
            <head>
            <meta charset="UTF-8">
            <title>News feed</title>
            <h1 style="color: #4485b8;">
                NEWS 
                <span style="background-color: #4485b8; color: #ffffff; padding: 0 5px;"> 
                    FEED
                </span>
            </h1>
            </head>        
                <body>
                    [BODY]
                </body>      
            </html>"""

        for news in self.news_feed:
            body_template = body_template.replace('[BODY]', news.get_html_template() + '[BODY]')

        body_template = body_template.replace('[BODY]', '')
        path_to_html_file = os.path.join(user_path_to_html, "RSS_ITEMS.html")
        try:
            with open(path_to_html_file, 'wb+') as f:
                f.write(body_template.encode('UTF-8'))
            self.logger.info(f"HTML file was created: {path_to_html_file}")
        except PermissionError as e:
            self.logger.error(e)
            raise e
        self.logger.info(f"HTML file was saved: {path_to_html_file}")
        return path_to_html_file


def _cell_to_pdf(pdf, text: str, multi=False, r=0, g=0, b=0):
    """The function adds a cell/line to the created PDF file"""

    pdf.set_text_color(r, g, b)
    if multi:
        pdf.multi_cell(0, 10, txt=f"{text}")
    else:
        pdf.write(10, f"{text}")


def _add_news_to_pdf_file(item, pdf, img_directory):
    """ Function that add item to pdf file. """

    pdf.set_font("DejaVu", size=12)
    _cell_to_pdf(pdf, "[ News title:] ")
    _cell_to_pdf(pdf, item.title, multi=True, b=0)
    if item.category:
        _cell_to_pdf(pdf, "[ Category:] ")
        _cell_to_pdf(pdf, ";".join(item.category), multi=True, b=0)
    pdf.set_font("DejaVu", size=9)
    _cell_to_pdf(pdf, "[ Pub. date:] ")
    _cell_to_pdf(pdf, item.pubdate, multi=True, b=0)
    if item.description:
        _cell_to_pdf(pdf, "[ Description:] ")
        _cell_to_pdf(pdf, item.description, multi=True)
    _cell_to_pdf(pdf, "[ News link:] ")
    _cell_to_pdf(pdf, item.link, multi=True, b=255)

    if set(item.image_links):
        _cell_to_pdf(pdf, "[ Images:] ")
        for num, image_link in enumerate(set(item.image_links)):
            if image_link:
                _add_image(image_link, pdf, img_directory)


def _add_image(image_link, pdf, img_directory):
    """ Function for getting image from image url and adding it to pdf file. """

    file_name = os.path.basename(image_link)
    file_path = os.path.join(img_directory, file_name)

    pos = file_name.rfind('.')
    img_type = '' if pos != -1 else 'jpeg'
    if img_type == '':
        img_type = file_name[pos + 1:].lower()
    if img_type not in 'jpeg jpg png gif':
        return

    try:
        picture_request = requests.get(image_link, timeout=5, verify=True)
    except Exception as e:
        raise e

    if picture_request.status_code == 200:
        with open(file_path, 'wb+') as f:
            f.write(picture_request.content)

    if os.path.isfile(file_path):
        pdf.image(file_path, x=30, y=pdf.get_y(), h=60, type=img_type, link=image_link)
        pdf.ln(10)
        os.remove(file_path)
