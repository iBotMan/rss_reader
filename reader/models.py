""" Module of creation Item """

import json
from datetime import datetime
from colorama import Back, Fore, Style
from reader.db.DBConnector import insert, delete

_months = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
    'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
}


class Item:
    """The ITEM class. It is created from the received data from the <item> xml file"""

    def __init__(self, **kwargs):

        self.link = kwargs.get('link', '')
        self.guid = kwargs.get('guid', self.link)
        self.pubdate = str(kwargs.get('pubdate', datetime.now()))
        self.filter_date = self.formatted_date()
        self.language = kwargs.get('language', '')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', self.title)
        self.html_description = kwargs.get('html_description', self.description)
        self.source = kwargs.get('source', '')
        self.category = kwargs.get('category', list())
        self.image_links = kwargs.get('image_links', list())
        self.links = kwargs.get('links', list())
        self.commit_data()

    def commit_data(self):

        """The function checks and converts the object data."""

        self.source = self.source.lower()
        if self.description:
            self.description = self.description.replace('\n', '').replace('\r', '')

        if isinstance(self.category, str):
            self.category = self.category.split(';')
        self.category = list(set(self.category))

        if isinstance(self.image_links, str):
            self.image_links = self.image_links.split(';')
        self.image_links = list(set(self.image_links))

        if isinstance(self.links, str):
            self.links = self.links.split(';')
        self.links = list(set(self.links))

    def formatted_date(self):

        """ The function converts the pubdate of the object to the format: 'YYYY-MM-DD'"""

        date_list = str(self.pubdate).split()
        if len(date_list) == 6:
            result = date_list[3] + '-' + _months[date_list[2].lower()] + '-' + date_list[1]
        elif len(date_list) == 2:
            result = date_list[0]
        else:
            result = str(datetime.now()).split()[0]
        return result

    def save(self):

        """The function saves the object to the cache database"""
        insert(self)

    def delete(self):

        """The function delete the object from the cache database"""
        delete(self)

    def get_fields(self):

        """The function returns a list of object attributes for the cache database"""
        return [field for field in self.__dict__]

    def serialize(self):
        """the function converts copies the object,
        converts the iterated fields to a string, and returns a copy."""
        copy_dict = self.__dict__.copy()
        for key in copy_dict:
            if isinstance(copy_dict[key], (list, set, tuple)):
                copy_dict[key] = ';'.join(copy_dict[key])
            else:
                copy_dict[key] = str(copy_dict[key])
        return copy_dict

    def get_html_template(self):
        """the function returns the completed html template of the object"""
        template = f"""
        <table class="ItemTable" style="vertical-align: top; height: 87px;">
            <thead>
                <tr style="height: 23px;"> 
                    <td style="height: 23px;" colspan="3">
                        <strong> 
                            {self.title}
                        </strong>
                    </td> 
                </tr>
                <tr>
                <td style="width: 93px;" colspan="3">
                    <p><a href="{self.link}">Link to item</a></p>
                </td> 
                </tr>
            </thead>
            <tbody>
                <tr style="height: 10px;">
                    <td style="width: 690px; height: 10px;" colspan="3"><strong><br /></strong>
                        <h4>[html_description]</h4>               
                        [images]
                    </td>
                </tr>
            </tbody>
        </table>
        <hr/>"""
        images = ''
        for _, link in enumerate(self.image_links):
            if link not in self.html_description:
                images = images + f'Image: <img src="{link}" width="255" height="189" alt=""><br>'

        template = template.replace('[html_description]', self.html_description)
        template = template.replace('[images]', images)
        return template

    def colorized(self, as_json=False):
        """The function print object in colorized mode"""
        if not as_json:
            print()
            print(Style.NORMAL, Back.WHITE, Fore.BLACK, end="\b\b")
            print(
                f"Item ({self.language or ''}): {self.source}",
                Style.RESET_ALL,
            )
            print(Style.NORMAL, Back.WHITE, Fore.BLACK, end="\b\b")
            print(f"Title: {self.title}", Style.RESET_ALL)

            if self.pubdate:
                print(Style.BRIGHT, Fore.WHITE, end="\b")
                print(f"Publication date: {self.pubdate}", Style.RESET_ALL)
            if self.category:
                print(Style.BRIGHT, Fore.WHITE, end="\b")
                print(f"Category: {self.category}", Style.RESET_ALL)
            if self.link:
                print(Style.BRIGHT, Fore.WHITE, end="\b")
                print(f"Link: {self.link}", Style.RESET_ALL)

            print(Style.BRIGHT, Fore.YELLOW)
            print(f"{self.description}\n", Style.RESET_ALL)

            if self.image_links:
                print(Style.BRIGHT, Fore.WHITE, end="\b")
                print("Description images:")
                for num, image in enumerate(self.image_links, 1):
                    print(f"[{num}]: {image}")
            if self.links:
                print("Description links:")
                for num, link in enumerate(self.links, 1):
                    print(f"[{num}]: {link}")
            print(2 * "\n")
            print(Style.RESET_ALL, end="")
        else:
            self.print_news(as_json)

    def print_news(self, as_json=False):
        """The function print object"""
        if not as_json:
            print(f"Source: {self.source}", end="\n")
            print(f"Language: {self.language}", end="\n")
            if self.category:
                print(f"Category: {'; '.join(self.category)}", end="\n")
            print(f"Title: {self.title}", end="\n")
            print(f"Description: {self.description}", end="\n")
            print(f"Date: {self.pubdate}", end="\n")
            print(f"Item Link: {self.link}", end="\n")
            if self.links:
                print(f"Links: {'; '.join(self.links)}", end="\n")
            if self.image_links:
                print(f"Images: {'; '.join(self.image_links)}", end="\n")
            print("****************************")
        else:
            print(json.dumps(self.serialize(), indent=4, ensure_ascii=False, default=lambda obj: obj.__dict__))
            print("****************************")

    def __str__(self):
        return f'Item {self.title}: {self.formatted_date()}'

    def __repr__(self):
        return f'Item {self.title}: {self.formatted_date()}'

    def __hash__(self):
        return hash(self.guid)

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.guid == other.guid
        else:
            return False
