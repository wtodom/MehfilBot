from __future__ import print_function

import requests
import twitter
import yaml

import re
import subprocess


config = yaml.load(file('mehfilbot.yaml', 'r'))
api = twitter.Api(consumer_key=config['twitter']['api_key'],
                      consumer_secret=config['twitter']['api_secret'],
                      access_token_key=config['twitter']['access_token'],
                      access_token_secret=config['twitter']['access_token_secret'])

print(api.VerifyCredentials())

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

def get_menu(pdf_text):
    menu = {}
    words = pdf_text.split()
    read_item = False
    read_description = False
    item_number = -1
    menu_item = ''
    description = ''
    for word in words:
        if is_item_number(word):
            read_item = True
            item_number = word
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
            menu[item_number]['description'] = description.strip()
            menu[item_number]['price'] = word
            menu[item_number]['name'] = item
            menu_item = ''
            description = ''
        elif read_description:
            description += ' ' + word
            if is_description_end(word):
                read_description = False
        elif len(menu.keys()) == 5:
            break
    return menu

def tweet_menu():
    menu = get_menu(get_text(config['menu']['filename']))

tweet_menu()
