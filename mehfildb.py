import psycopg2

def new_menu(date):
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("INSERT INTO menu (menu_date) VALUES ('{0}');".format(date))
    res = cur.statusmessage
    conn.commit()
    cur.close()
    conn.close()
    return res == 'INSERT 0 1'

def new_menu_item(menu_id, item_number, name, description, price):
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO menu_item (menu_id, item_number, name, description, price)\
         VALUES ({0}, {1}, '{2}', '{3}', {4});".format(
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
    Returns True if the update updated a single row, False otherwise.
    """
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("UPDATE menu SET has_been_tweeted=1 WHERE menu_date='{0}' and has_been_tweeted=0;".format(date))
    res = cur.statusmessage
    conn.commit()
    cur.close()
    conn.close()
    return res == 'UPDATE 1'

def get_menu_for_date(date):
    conn = psycopg2.connect(dbname='mehfilbot', user='westonodom')
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu WHERE menu_date='{0}';".format(date))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res

def menu_already_tweeted(date):
    ## TODO: raise exception if menu not found?
    res = get_menu_for_date(date)
    if res and res[2] == 1:
        return True
    return False

def menu_exists(date):
    return get_menu_for_date(date) is not None
