import redis
import json
from datetime import datetime
from pathlib import Path


from src.pipeline import Pipeline
from utils.date_management import make_date_to_tickersymbol
from utils.argument_management import Opts
from utils.loading_file import load_yaml


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]


def main():
    FLAGS = Opts().parse_args()
    pipeline = Pipeline(FLAGS)
    
    redis_opts = load_yaml(ROOT/'configs'/'usr'/'redis_account.yaml')
    redis_host, redis_port, redis_password = redis_opts['host'], redis_opts['port'], redis_opts['password']
    print(redis_host, redis_port, redis_password)
    
    # connect to redis server
    redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password
    )

    # check connection to redis OK
    print(redis_client.ping())

    current_date = datetime.now()
    tickersymbol = make_date_to_tickersymbol(current_date)
    F1M_CHANNEL = f'HNXDS:{tickersymbol}'
    print(F1M_CHANNEL)
    

    # test if redis return correct latest quote of VN30F1M
    redis_message = redis_client.get(F1M_CHANNEL)
    quote_dict = json.loads(redis_message)
    print(quote_dict)

if __name__ == "__main__":
    main()
    