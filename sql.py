import sqlite3
import time


from data.config import SQL_PATH


def connection_wrapper(func):
    def open_close_connection(*args, **kwargs):
        con = sqlite3.connect(SQL_PATH)
        cur = con.cursor()
        func(cur, *args, **kwargs)
        con.commit()
        con.close()
    return open_close_connection


@connection_wrapper
def create_table(cur):
    try:
        cur.execute('''CREATE TABLE proposals(
            network text, 
            prop_id int, 
            title text, 
            voting_end_time int, 
            option bool,
            next_notification int,
            msg_id int
        )''')
    except sqlite3.OperationalError as er:
        pass


@connection_wrapper
def save_to_db(cur, data):
    cur.execute("insert into proposals values (?, ?, ?, ?, ?, ?, ?)", tuple(data))


def check_dublicates(network, prop_id):
    con = sqlite3.connect(SQL_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM proposals WHERE network=? AND prop_id=?", (network, prop_id))
    fetched_data = cur.fetchall()
    if not fetched_data:
        return False
    else:
        return True
    con.commit()
    con.close()


def get_rows(network, prop_id):
    con = sqlite3.connect(SQL_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM proposals WHERE network=? AND prop_id=?", (network, prop_id))
    fetched_data = cur.fetchall().copy()
    con.commit()
    con.close()
    return fetched_data


@connection_wrapper
def drop_rows(cur):
    current_time = int(time.time())
    cur.execute("""DELETE from proposals where voting_end_time < ?""", (current_time,))
    cur.execute("""DELETE from proposals where option = 1""")


@connection_wrapper
def get_outdated_props(cur):
    current_time = int(time.time())
    cur.execute("SELECT * FROM proposals WHERE voting_end_time < ? OR option = 1", (current_time,))
    fetched_data = cur.fetchall().copy()
    return fetched_data


def drop_row_by_msg_id(network, prop_id, msg_id):
    con = sqlite3.connect(SQL_PATH)
    cur = con.cursor()
    cur.execute("""DELETE from proposals where msg_id = ? and network = ? and prop_id = ?""", (msg_id, network, prop_id))
    con.commit()
    con.close()


@connection_wrapper
def set_option(cur, network, prop_id, value):
    cur.execute("UPDATE proposals set option = ? where network = ? and prop_id = ?",
                (value, network, prop_id))


def get_all_rows():
    con = sqlite3.connect(SQL_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM proposals")
    fetched_data = cur.fetchall()
    con.commit()
    con.close()
    return fetched_data

