import mehfildb
import parser
import tweeter

import requests
import shutil
import yaml

import datetime
import logging.config


with open('mehfilbot.yaml', 'r') as f:
    config = yaml.load(f)


with open('logging.yaml', 'r') as f:
    log_conf = yaml.load(f)


logger = logging.getLogger(__name__)

logging.config.dictConfig(log_conf)


def get_new_pdf():
    logger.info('Getting new menu pdf.')
    response = requests.get(config['menu']['url'], stream=True)
    with open(config['menu']['filename'], 'w') as pdf:
        shutil.copyfileobj(response.raw, pdf)


def is_new(menu):
    logger.info('Checking if menu for {0} is new.'.format(menu['date']))
    res = mehfildb.get_menu_for_date(menu['date'])
    return res is None


def log_menu(menu):
    logger.info('Recording menu for {0} in db.'.format(menu['date']))
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


def main():
    get_new_pdf()
    menu = parser.parse_menu(parser.get_text(config['menu']['filename']))
    today = datetime.date.today()
    if is_new(menu):
        log_menu(menu)
    # TODO: refactor this - leads to duplicate calls to the db
    if mehfildb.menu_exists(today) and not mehfildb.menu_is_tweeted(today):
        tweeter.tweet_menu(menu)
        mehfildb.set_menu_as_tweeted(today)

if __name__ == '__main__':
    logger.info('Starting mehfilbot.')
    main()
    logger.info('Stopping mehfilbot.')
