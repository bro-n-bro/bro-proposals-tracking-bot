from data.config import NOTIFIER_FREQUENCY, CHAT_ID, TG_BOT_API_TOKEN, MESSAGE_THREAD_ID
from sql import get_all_rows, drop_rows, save_to_db, get_rows, drop_row_by_msg_id, get_outdated_props
from get_data import save_data
from utils import chose_next_notification, notify, get_time_left_s
import telegram
import asyncio

import time
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


async def notifier(telegram_bot, _row):
    if int(time.time()) >= _row[5]:
        time_left_s = get_time_left_s(_row)
        msg = notify(_row, time_left_s)
        t_msg = await telegram_bot.send_message(CHAT_ID, msg, parse_mode="markdown", message_thread_id=MESSAGE_THREAD_ID)
        logging.info(t_msg.text)
        record = list(_row[:5])
        record.extend([
                chose_next_notification(time_left_s),
                t_msg.message_id
            ])
        save_to_db(record)
        records = get_rows(_row[0], _row[1])
        message_to_delete = min(x[6] for x in records)
        try:
            await telegram_bot.delete_message(chat_id=CHAT_ID, message_id=message_to_delete)
        except Exception as e:
            logging.error(f'Notification error: {e}')
            pass
        drop_row_by_msg_id(_row[0], _row[1], message_to_delete)
    else:
        pass


async def processor(telegram_bot):
    outdated_props = get_outdated_props()
    if outdated_props:
        msgs_to_delete = [x[6] for x in outdated_props]
        for msg in msgs_to_delete:
            try:
                await telegram_bot.delete_message(chat_id=CHAT_ID, message_thread_id=MESSAGE_THREAD_ID, message_id=msg)
            except Exception as e:
                logging.error(f'Msg deleting error: {e}')
                pass
    drop_rows()
    await save_data()
    rows = get_all_rows()
    for row in rows:
        await notifier(telegram_bot, row)
    logging.info("All records have been checked and processed")


async def async_func(telegram_bot):
    await save_data()
    while True:
        await processor(telegram_bot)
        await asyncio.sleep(NOTIFIER_FREQUENCY)


async def main(telegram_bot):
    task = asyncio.create_task(async_func(telegram_bot))
    await task


if __name__ == "__main__":
    telegram_bot = telegram.Bot(token=TG_BOT_API_TOKEN)
    rows = get_all_rows()
    asyncio.run(main(telegram_bot))
