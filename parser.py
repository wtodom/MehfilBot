import dateutil.parser as dateutil

from collections import OrderedDict
import datetime
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
        if year in item:
            return i


def get_date(text_list):
    year_index = index_of_year(text_list)
    date_found = False
    backtrack = 0
    # this loop should be re-ordered to catch cases correctly
    # also, it may either default to 'today', or miss one edge case where
    #   there are no spaces in the date on the pdf. could catch by manually
    #   parsing the string at year_index in the event that it found a date
    #   at exactly that point.
    while not date_found:
        date_string = ' '.join(text_list[backtrack:year_index + 1]).title()
        try:
            potential_date = dateutil.parse(date_string).date()
        except ValueError:
            # raised in some situations when it fails to parse a valid date
            # We know there is a date here somewhere, so ignore this now.
            # We will raise another error if we don't find a date.
            potential_date = None
        if type(potential_date) == datetime.date:
            return str(potential_date)
        elif backtrack < year_index:
            backtrack += 1
        else:
            # need to write and raise a custom error here for logging
            raise ValueError('No date found ')


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
