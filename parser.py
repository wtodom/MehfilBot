from __future__ import print_function

import mehfildb

import psycopg2
import dateutil.parser as dateutil
import requests
import twitter
import yaml

from collections import OrderedDict
import datetime
import re
import shutil
import subprocess


config = yaml.load(file('mehfilbot.yaml', 'r'))
api = twitter.Api(
    consumer_key=config['twitter']['api_key'],
    consumer_secret=config['twitter']['api_secret'],
    access_token_key=config['twitter']['access_token'],
    access_token_secret=config['twitter']['access_token_secret']
    )

def get_new_pdf():
    response = requests.get(config['menu']['url'], stream=True)
    with open(config['menu']['filename'], 'w') as pdf:
        shutil.copyfileobj(response.raw, pdf)

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
    menu_date = ' '.join(words[7:12]).title()
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

def is_new(menu):
    res = mehfildb.get_menu_for_date(menu['date'])
    return res is not None

def log_menu(menu):
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    mehfildb.new_menu(menu['date'])
    menu_id = mehfildb.get_menu_for_date(menu['date'])[0]
    for i in range(1, 6):
        mehfildb.new_menu_item(
            menu_id,
            i,
            menu[str(i)]['name'],
            menu[str(i)]['description'],
            menu[str(i)]['price']
            )

def tweet_menu(menu):
    menu_items = []
    summary = "Today's Mehfil menu:\n"
    for item in menu.items()[1:]:
        summary += "{0}: {1}\n".format(
            item[0],
            item[1]['name']
            )
        menu_items.append(
            "{0}: {1} - {2} (${3})".format(
                item[0],
                item[1]['name'],
                item[1]['description'],
                item[1]['price']
                )
            )
    summary_tweet = api.PostUpdate(summary)
    reply_id = summary_tweet.id
    for item in menu_items:
        reply = api.PostUpdate(item, in_reply_to_status_id=reply_id)
        reply_id = reply.id

def main():
    get_new_pdf()
    menu = parse_menu(get_text(config['menu']['filename']))
    today = datetime.date.today()
    if is_new(menu):
        log_menu(menu)
    ## TODO: refactor this - leads to duplicate calls to the db
    if mehfildb.menu_exists(today) and not mehfildb.menu_already_tweeted(today):
        tweet_menu(menu)
        meehfildb.set_menu_as_tweeted(today)

if __name__ == '__main__':
    main()
