import dateutil.parser as dateutil

from collections import OrderedDict
import re
import subprocess


def get_text(pdf_filename):
    return subprocess.check_output(['pdf2txt.py', pdf_filename])


def is_item_name(word):
    return word == word.upper() and '(' not in word


def is_item_number(word):
    return re.match('\([0-9]\)', word)


def is_price(word):
    return re.match('\$[0-9]\.[0-9][0-9]', word)


def is_description_start(word):
    return word.strip()[0] == '('


def is_description_end(word):
    return word[-1] == ')'


def index_of_year(text_list):
    year = re.findall('[0-9]{4}', ' '.join(text_list))[0]
    for i, item in enumerate(text_list):
        print(year in item)
        if year in item:
            return i
    # return text_list.index(year)


def index_of_month(text_list, year_index):
    month = re.findall('[A-Z]{3}', ' '.join(text_list[:year_index]))[-1]
    for i, item in enumerate(text_list):
        print(month in item)
        if month in item:
            return i
    # return text_list.index(month)


def get_date(text_list):
    year_index = index_of_year(text_list)
    month_index = index_of_month(text_list, year_index)
    menu_date = ' '.join(text_list[month_index:year_index + 1]).title()
    return str(dateutil.parse(menu_date).date())


def parse_menu(pdf_text):
    menu = OrderedDict()
    words = pdf_text.split()
    menu['date'] = get_date(words)
    read_item = False
    read_description = False
    item_number = -1
    menu_item = ''
    description = ''
    for word in words:
        if is_item_number(word):
            read_item = True
            item_number = word[1]
        elif read_item and is_item_name(word):
            menu_item += ' ' + word.title()
        elif read_item and not is_item_name(word):  # item name finished
            read_item = False
            read_description = True
            description += ' ' + word
        elif menu_item != '' and is_price(word):  # price and not reading name
            read_description = False
            item = menu_item.strip()
            menu[item_number] = {}
            menu[item_number]['name'] = item
            menu[item_number]['description'] = ''.join(
                c for c in description if c not in '()')
            menu[item_number]['price'] = word[1:]
            menu_item = ''
            description = ''
        elif read_description:
            description += ' ' + word
            if is_description_end(word):
                read_description = False
        elif len(menu.keys()) == 6:  # TODO: this is a bad way to check
            break
    return menu
