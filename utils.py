from data.config import NOTIFIER_FREQUENCY, NOTIFIER_REMINDER_MODES, PHRASES, NETWORKS
from datetime import timedelta

import time
import random


def notify(row, time_left):
    print(time_left)
    phrase = get_phrase(time_left)
    print(phrase)
    t = timedelta(seconds=time_left)
    msg = f"Warning {t} left before voting ends"
    network = [n for n in NETWORKS if n['name'] == row[0]][0]
    url = f"{network['explorer']}{row[1]}"
    return '\n' + "🚨" + "*" + msg + "*" + "🚨" + '\n' + phrase + '\n\n' + url


def get_phrase(time_left_s):
    if time_left_s in NOTIFIER_REMINDER_MODES["SOFT"][0]:
        return random.choice(PHRASES['SOFT'])
    elif time_left_s in NOTIFIER_REMINDER_MODES["MEDIUM"][0]:
        return random.choice(PHRASES['MEDIUM'])
    elif time_left_s in NOTIFIER_REMINDER_MODES["HARD"][0]:
        return random.choice(PHRASES['HARD'])
    elif time_left_s in NOTIFIER_REMINDER_MODES["EXTREME"][0]:
        return random.choice(PHRASES['EXTREME'])


def chose_next_notification(time_left_s):
    if time_left_s in NOTIFIER_REMINDER_MODES["SOFT"][0]:
        next_notification = int(time.time()) + NOTIFIER_REMINDER_MODES["SOFT"][1] + random.randint(0, 5)
    elif time_left_s in NOTIFIER_REMINDER_MODES["MEDIUM"][0]:
        next_notification = int(time.time()) + NOTIFIER_REMINDER_MODES["MEDIUM"][1] + random.randint(0, 5)
    elif time_left_s in NOTIFIER_REMINDER_MODES["HARD"][0]:
        next_notification = int(time.time()) + NOTIFIER_REMINDER_MODES["HARD"][1] + random.randint(0, 5)
    elif time_left_s in NOTIFIER_REMINDER_MODES["EXTREME"][0]:
        next_notification = int(time.time()) + NOTIFIER_REMINDER_MODES["EXTREME"][1] + random.randint(0, 5)
    return next_notification


def get_time_left_s(row):
    return row[3] - int(time.time())