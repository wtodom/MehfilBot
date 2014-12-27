import dateutil.parser as dateutil
import yaml

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

def parse_menu(pdf_text):
    menu = OrderedDict()
    words = pdf_text.split()
    menu_date = ' '.join(words[5:8]).title()
    menu['date'] = str(dateutil.parse(menu_date).date())
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
            menu[item_number]['description'] = ''.join(c for c in description if c not in '()')
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
