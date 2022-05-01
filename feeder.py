import json
import logging
import operator
import os
import time
from typing import List, Generator
from telegram import send_telegram_message
from db import fetch_chat_ids
from exchanges import get_connection, Message

logging.basicConfig(level=logging.INFO,
                    filename='app.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CONFIG_PATH = os.getenv('CONFIG_PATH')
TIMEOUT = int(os.getenv('TICKER_NOTIFICATION_TIMEOUT'))

TRIGGER_OPTIONS = {
    'more': operator.gt,
    'less': operator.lt,
    'more_eq': operator.ge,
    'less_eq': operator.le
}


def get_config() -> dict:
    """Parses input config.json"""

    with open(CONFIG_PATH, 'r') as file:
        config = json.loads(file.read())

    valid_config = {}
    for key, value in config.items():
        ticker = key.lower().replace('/', '')
        config_option = value['trigger']
        conditions = {
            'trigger': TRIGGER_OPTIONS[config_option],
            'price': float(value['price']),
            'update_time': 0,
        }
        valid_config[ticker] = conditions

    return valid_config


def round_robin(sockets: list) -> Generator[Message, None, None]:
    """Polls available exchanges one at the time"""

    while True:
        if not sockets:
            break

        socket = sockets.pop(0)
        try:
            yield next(socket)
        except StopIteration:
            if len(sockets) == 0:
                return
        except RuntimeError as err_msg:
            logging.exception(err_msg)
        else:
            sockets.append(socket)


def convert_message(message: Message) -> str:
    return f"{message.exchange}: {message.ticker.upper()} at ${message.price}"


def broadcast_message(message: Message) -> None:
    """Sends the same message to all subscribers"""

    tg_msg = convert_message(message)

    for chat in fetch_chat_ids():
        response = send_telegram_message(chat_id=chat,
                                         message=tg_msg)



def feed(config: dict, exchanges: List[str]) -> None:
    """Retrieves the data from exchanges"""
    connections = (get_connection(e, config) for e in exchanges)

    subscription_streams = [ex.subscribe() for ex in connections]

    msg_counter = 0

    for message in round_robin(subscription_streams):

        # every 100 messages check if someone is subscribed.
        # if not then close our sockets and return
        msg_counter += 1
        if msg_counter == 100:
            msg_counter = 0
            subscribers = fetch_chat_ids()
            if not subscribers:
                return

        # actual data from exchange
        ticker = message.ticker
        actual_price = message.price

        # params from config
        trigger_price = config[ticker]['price']
        condition = config[ticker]['trigger']
        update_time = config[ticker]['update_time']

        # if price is below/above given level
        price_is_triggered = condition(actual_price, trigger_price)

        # if elapsed time since last notification > timeout = notify user
        should_notify = time.time() > update_time or update_time == 0

        if price_is_triggered and should_notify:
            logging.info(f"Triggered for {ticker}: {round(actual_price)} / {round(trigger_price)}")
            config[ticker]['update_time'] = time.time() + TIMEOUT
            broadcast_message(message)


def start() -> None:
    # List of connections in use. For now only Binance.
    connections_list = ['Binance']

    # Get settings
    config = get_config()

    # wait if no one subscribed
    while True:
        if not fetch_chat_ids():
            logging.warning('No subscribers!')
            time.sleep(1)
            continue
        feed(config, connections_list)
