import psycopg2
import yaml


with open('mehfilbot.yaml', 'r') as main_conf:
    config = yaml.load(main_conf)

db = config['postgres']['db']
user = config['postgres']['user']


def new_menu(date):
    """
    Returns True if the row was successfully inserted, False otherwise.
    """
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mehfilbot.menu (menu_date) VALUES ('{0}');".format(date))
    res = cur.statusmessage
    # TODO: Change queries to use INSERT ... RETURNING syntax.
    # TODO: Return this value to prevent excess db calls.
    conn.commit()
    cur.close()
    conn.close()
    return res == 'INSERT 0 1'


def new_menu_item(menu_id, item_number, name, description, price):
    """
    Returns True if the row was successfully inserted, False otherwise.
    """
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mehfilbot.menu_item ("
        "menu_id, "
        "item_number, "
        "name, "
        "description, "
        "price"
        ") "
        "VALUES ({0}, {1}, '{2}', '{3}', {4});".format(
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
    return res == 'INSERT 0 1'


def set_menu_as_tweeted(date):
    """
    Returns `True` if the update updated a single row, `False` otherwise.
    """
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
    return res == 'UPDATE 1'


def get_menu_for_date(date):
    """
    Returns the retrieved row if it exists, or `None` if no row was found.
    """
    conn = psycopg2.connect(dbname=db, user=user)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM mehfilbot.menu WHERE menu_date='{0}';".format(date))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res


def menu_is_tweeted(date):
    # TODO: raise exception if menu not found?
    res = get_menu_for_date(date)
    if res and res[2] == 1:
        return True
    return False


def menu_exists(date):
    return get_menu_for_date(date) is not None
