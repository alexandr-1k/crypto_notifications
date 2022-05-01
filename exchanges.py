import json
import os
from abc import ABC, abstractmethod
from contextlib import closing
from typing import Union, Generator, NamedTuple
from websocket import create_connection


class Message(NamedTuple):
    """Message structure"""
    ticker: str
    price: float
    trade_time: float
    exchange: str


class BaseConnection(ABC):

    @abstractmethod
    async def subscribe(self) -> Generator[Message, None, None]:
        """Yields Message instance.
        Throws RuntimeError if something goes wrong.
        """

    @abstractmethod
    def get_subscription_message(self) -> None:
        """Sets up initial message that is going to be sent to the exchange.
        Different exchanges can have different tickers (symbols) listed in.
        We can check valid tickers here"""


class Binance(BaseConnection):

    def __init__(self, config: dict):
        self.tickers = config.keys()

    def get_subscription_message(self) -> str:
        return json.dumps({
            "method": "SUBSCRIBE",
            "params": [f"{ticker}@trade" for ticker in self.tickers],
            "id": 1
        })

    def subscribe(self) -> Generator[Message, None, None]:
        ws_endpoint = os.environ.get('BINANCE_ENDPOINT')
        with closing(create_connection(ws_endpoint)) as conn:
            conn.send(self.get_subscription_message())

            while True:
                payload = conn.recv()
                message = json.loads(payload)

                if 'result' in message:
                    # first response has no useful payload
                    continue

                if 'error' in message:
                    raise RuntimeError(f'Binance is down: {message}')

                yield Message(ticker=message['s'].lower(),
                              price=float(message['p']),
                              trade_time=float(message['T']),
                              exchange='Binance')


def get_connection(name: str, config: dict) -> Union[Binance]:
    exchanges = {
        'Binance': Binance
    }

    return exchanges[name](config)
