from __future__ import print_function

import psycopg2
import requests
import twitter
import yaml

import calendar
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
    menu['date'] = ' '.join(words[7:12]).title()
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
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("SELECT menu_id FROM menu WHERE date='{0}';".format(menu['date']))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return len(res) == 0

def today_not_tweeted(today):
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM menu WHERE date='{0}' and has_been_tweeted=0;".format(today))
    res = cur.fetchall()
    cur.close()
    conn.close()
    return len(res) == 1

def log_menu(menu):
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("INSERT INTO menu (date) VALUES ('{0}');".format(menu['date']))
    cur.execute("SELECT menu_id FROM menu WHERE date='{0}';".format(menu['date']))
    menu_id = cur.fetchone()[0]
    for i in range(1, 6):
        cur.execute(
            "INSERT INTO menu_item (menu_id, item_number, name, description, price)\
             VALUES ({0}, {1}, '{2}', '{3}', {4});".format(
                menu_id,
                i,
                menu[str(i)]['name'],
                menu[str(i)]['description'],
                menu[str(i)]['price']
                )
            )
    conn.commit()
    cur.close()
    conn.close

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

def set_menu_as_tweeted():
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("UPDATE menu SET has_been_tweeted=1 WHERE date='{0}' and has_been_tweeted=0;".format(today))
    res = cur.fetchall()
    cur.close()
    conn.close()

def main():
    get_new_pdf()
    menu = parse_menu(get_text(config['menu']['filename']))
    today = datetime.date.today()
    if is_new(menu):
        log_menu(menu)
        if today_not_tweeted(today):
            tweet_menu(menu)
            set_menu_as_tweeted(today)

if __name__ == '__main__':
    main()
