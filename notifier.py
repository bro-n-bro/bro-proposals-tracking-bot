from data.config import NOTIFIER_FREQUENCY, CHAT_ID, TG_BOT_API_TOKEN
from sql import get_all_rows, drop_rows, save_to_db, get_rows, drop_row_by_msg_id, get_outdated_props
from get_data import save_data
from utils import chose_next_notification, notify, get_time_left_s
import telegram

import time
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def notifier(telegram_bot, _row):
    if int(time.time()) >= _row[5]:
        time_left_s = get_time_left_s(_row)
        msg = notify(_row, time_left_s)
        t_msg = telegram_bot.send_message(CHAT_ID, msg, parse_mode="markdown")
        record = list(_row[:5])
        record.extend([
                chose_next_notification(time_left_s),
                t_msg.message_id
            ])
        save_to_db(record)
        records = get_rows(_row[0], _row[1])
        message_to_delete = min(x[6] for x in records)
        try:
            telegram_bot.delete_message(chat_id=CHAT_ID, message_id=message_to_delete)
        except Exception as e:
            print(e)
            pass
        drop_row_by_msg_id(_row[0], _row[1], message_to_delete)
    else:
        pass


def processor(telegram_bot):
    save_data()
    outdated_props = get_outdated_props()
    if outdated_props and outdated_props != []:
        msgs_to_delete = [x[6] for x in outdated_props]
        for msg in msgs_to_delete:
            try:
                telegram_bot.delete_message(chat_id=CHAT_ID, message_id=msg)
            except Exception as e:
                print(e)
                pass
    drop_rows()
    rows = get_all_rows()
    for row in rows:
        notifier(telegram_bot, row)
    logging.info("Records was checked")


if __name__ == "__main__":
    telegram_bot = telegram.Bot(token=TG_BOT_API_TOKEN)
    save_data()
    rows = get_all_rows()
    while True:
        processor(telegram_bot)
        time.sleep(NOTIFIER_FREQUENCY)
