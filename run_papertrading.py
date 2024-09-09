import time

import json
import pytz
from datetime import datetime
from pathlib import Path

from src.pipeline import Pipeline
from utils.date_management import make_date_to_tickersymbol
from utils.argument_management import Opts
from utils.file_management import load_yaml

from plutus.datahub.redis_datahub import RedisDataHub

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')

# handle pricehub quote
def redis_message_handler(redis_message):
    quote = json.loads(redis_message['data'])
    cur_price = quote['latest_matched_price']

    # check if cur_price updated yet
    if cur_price is None:
        return

    datetime_now = datetime.fromtimestamp(quote['timestamp']).astimezone(TIMEZONE).time()


def main():
    FLAGS = Opts().parse_args()
    pipeline = Pipeline(FLAGS)

    redis_opts = load_yaml(ROOT/'configs'/'usr'/'redis_account.yaml')
    redis_host, redis_port, redis_password = redis_opts['host'], redis_opts['port'], redis_opts['password']
    print(redis_host, redis_port, redis_password)

    # connect to redis server
    redis_data_hub = RedisDataHub(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password
    )

    current_date = datetime.now()
    ticker_symbol = make_date_to_tickersymbol(current_date)
    F1M_CHANNEL = f'HNXDS:{ticker_symbol}'
    print(F1M_CHANNEL)

    pipeline.run_papertrading(redis_data_hub)


if __name__ == "__main__":
    main()
    while True:
        time.sleep(0.01)
