# Test task
### Retrieve data from the exchange and notify the user in Telegram
The task itself is in task.txt

### To run locally
```commandline
 docker build -t telega_app . && docker run -d --env-file=./.env telega_app
```
### To test
The bot sould be available at @BinanceNotificator_bot . Use **/sub** to get notifications about price changes.
And use **/stop** to unsubscribe.
### Key points:
1. I used websockets.
2. I used synchronous mode because time intervals between received messages are short.
3. There is an env variable called **TICKER_NOTIFICATION_TIMEOUT** which defines how often user is going to get
notifications on each particular ticker.
