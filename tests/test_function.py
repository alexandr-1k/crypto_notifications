from unittest.mock import patch, call
from dotenv import load_dotenv
load_dotenv('../.env')
from feeder import broadcast_message, Message, convert_message


@patch('feeder.send_telegram_message')
@patch('feeder.fetch_chat_ids')
def test_broadcast_function(fetch_ids_mock, post_mock):
    # Arrange
    dummy_id = (1, 2, 3)
    fetch_ids_mock.return_value = dummy_id

    test_message = Message(ticker='TEST',
                           price=100,
                           trade_time=100,
                           exchange='Binance')

    calls = [call(chat_id=i, message=convert_message(test_message)) for i in dummy_id]

    # Act
    broadcast_message(test_message)

    # Assert
    assert post_mock.call_args_list == calls

