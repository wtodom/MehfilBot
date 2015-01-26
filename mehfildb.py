import psycopg2
import yaml

import logging.config


with open('mehfilbot.yaml', 'r') as main_conf:
    config = yaml.load(main_conf)


with open('logging.yaml', 'r') as f:
    log_conf = yaml.load(f)


logger = logging.getLogger(__name__)

logging.config.dictConfig(log_conf)

db = config['postgres']['db']
user = config['postgres']['user']


def new_menu(date):
    """
    Returns True if the row was successfully inserted, False otherwise.
    """
    logger.info('Inserting new menu for {0}'.format(date))
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    menu_id = cur.execute(
        "INSERT INTO mehfilbot.menu (menu_date) "
        "VALUES ('{0}') "
        "RETURNING menu_id;".format(date))
    res = cur.statusmessage
    # TODO: Change queries to use INSERT ... RETURNING syntax.
    # TODO: Return this value to prevent excess db calls.
    conn.commit()
    cur.close()
    conn.close()
    if res == 'INSERT 0 1':
        logger.info('Insert successful. menu_id: {0}'.format(menu_id))
        return True
    else:
        logger.error('Insert failed. menu_id: {0}'.format(menu_id))
        return False


def new_menu_item(menu_id, item_number, name, description, price):
    """
    Returns True if the row was successfully inserted, False otherwise.
    """
    logger.info('Inserting new menu_item for menu_id {0}'.format(menu_id))
    logger.info('item_number: {0}'.format(item_number))
    logger.info('name: {0}'.format(name))
    logger.info('description: {0}'.format(description))
    logger.info('price: {0}'.format(price))
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    menu_item_id = cur.execute(
        "INSERT INTO mehfilbot.menu_item ("
        "menu_id, "
        "item_number, "
        "name, "
        "description, "
        "price"
        ") "
        "VALUES ({0}, {1}, '{2}', '{3}', {4})"
        "RETURNING menu_item_id;".format(
            menu_id,
            item_number,
            name,
            description,
            price
            )
        )
    res = cur.statusmessage
    conn.commit()
    cur.close()
    conn.close()
    if res == 'INSERT 0 1':
        logger.info('Insert successful. menu_item_id: {0}'.format(
            menu_item_id))
        return True
    else:
        logger.error('Insert failed. menu_item_id: {0}'.format(menu_item_id))
        return False


def set_menu_as_tweeted(date):
    """
    Returns `True` if the update updated a single row, `False` otherwise.
    """
    logger.info('Setting has_been_tweeted to 1 for {0} menu'.format(date))
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    cur.execute(
        "UPDATE mehfilbot.menu "
        "SET has_been_tweeted=1 "
        "WHERE menu_date='{0}' and has_been_tweeted=0;".format(date))
    res = cur.statusmessage
    conn.commit()
    cur.close()
    conn.close()
    if res == 'UPDATE 1':
        logger.info('Update successful.')
        return True
    else:
        logger.error('Update failed.')
        return False


def get_menu_for_date(date):
    """
    Returns the retrieved row if it exists, or `None` if no row was found.
    """
    logger.info('Getting menu for {0}'.format(date))
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM mehfilbot.menu WHERE menu_date='{0}';".format(date))
    menu = cur.fetchone()
    res = cur.statusmessage
    cur.close()
    conn.close()
    if res == 'SELECT 1':
        logger.info('Menu exists. menu: {0}'.format(str(menu)))
    else:
        logger.info('Menu does not exist.')
    return menu


def menu_is_tweeted(date):
    # TODO: raise exception if menu not found?
    logger.info('Checking has_been_tweeted for {0} menu.'.format(date))
    res = get_menu_for_date(date)
    if not res:
        logger.warn('Menu for {0} not found.'.format(date))
        return False
    elif res[2] == 1:
        logger.info('Menu has already been tweeted.')
        return True
    logger.info('Menu hasn\'t been tweeted yet.')
    return False


def menu_exists(date):
    logger.info('Checking existance of menu for {0}'.format(date))
    res = get_menu_for_date(date) is not None
    if res:
        logger.info('Menu exists.')
    else:
        logger.info('Menu does not exist.')
    return res
