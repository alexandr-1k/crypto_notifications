from multiprocessing import Process
import telegram
import feeder
from db import check_if_db_exists

if __name__ == '__main__':
    # Create database for saving ids of chats
    check_if_db_exists()

    # Start couple processes for sending notifications and retrieving data
    bot = Process(target=telegram.start)
    data = Process(target=feeder.start)

    bot.start()
    data.start()
