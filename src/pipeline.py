import os
import time
import json
import logging
import optuna
import numpy as np
import pandas as pd
from datetime import datetime

from src.bot.bot import Bot
from src.metrics import sharpe_ratio, maximum_drawdown
from src.utils.visualizer import VISUALIZER

from utils.loading_file import load_csv
from utils.date_management import get_num_days_to_maturity, make_date_to_tickersymbol


class Pipeline():
    def __init__(self, opts):
        self.opts = opts
        self.train_data = load_csv(opts['DATASET']['TRAIN']['csv_file'])
        self.val_data = load_csv(opts['DATASET']['VAL']['csv_file'])
        self.test_data = load_csv(opts['DATASET']['TEST']['csv_file'])
        self._init_save_dir()
        self.opts.save_yaml(self.opts['PIPELINE']['params']['save_dir']/'config.yaml')

    def _init_save_dir(self):
        os.makedirs(self.opts['PIPELINE']['params']['save_dir'], exist_ok=True)
        os.makedirs(self.opts['PIPELINE']['params']['save_dir']/'train', exist_ok=True)
        os.makedirs(self.opts['PIPELINE']['params']['save_dir']/'val', exist_ok=True)
        os.makedirs(self.opts['PIPELINE']['params']['save_dir']/'test', exist_ok=True)


    def _init_logging(self, log_file='log.txt', name='logger'):
        """ Initialize logging
        """
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def calculate_performance_score(self, returns, num_order, fees=0.3):
        profit_array = np.array(returns)
        max_drawdown_value = maximum_drawdown(profit_array)
        profit = np.sum(returns - (num_order)*fees)
        sharpe = sharpe_ratio(returns)
        return profit, sharpe, max_drawdown_value
    

    def _log_results(self, logger, model, symbol):
        monthlyAvgSpread, monthlyProfit, num_order = model.get_monthly_history().get_statistic()
        profit, sharpe, max_drawdown_value = self.calculate_performance_score(monthlyProfit, 
                                                                              num_order, 
                                                                              self.opts['PIPELINE']['params']['fee'])

        logger.info("                   Results                   ")
        logger.info("---------------------------------------------")
        logger.info("%14s %21s" % ('statistic on', str(symbol)))
        logger.info(40 * "-")
        logger.info("%14s %20.5f" % ("Average spread :", monthlyAvgSpread))
        logger.info("%14s %20.5f" % ("Number of transaction :", num_order.sum()))
        logger.info("%16s %20.5f" % ("Profit :", profit))
        logger.info("%16s %20.5f" % ("Sharpe ratio :", sharpe))
        logger.info("%16s %20.5f" % ("Max drawdown :", max_drawdown_value))

        return monthlyAvgSpread, num_order, profit, sharpe, max_drawdown_value

    def report_monthly_data(self, model, save_dir=None):
        os.makedirs(save_dir, exist_ok=True)
        model.get_monthly_history().export_df_inventory(save_file=save_dir/'inventory.csv')
        df_order_analysis = model.get_monthly_history().export_df_order_analysis(save_file=save_dir/'order.csv')
        model.get_monthly_history().export_df_profit_per_day(save_file=save_dir/'profit.csv')
        bids,asks = model.get_monthly_history().get_bidsask_spread()
        df = model.monthly_tick_data.export_df_market_timeprice()
        df_spread = pd.DataFrame({'datetime':df['datetime'],'ask': asks, 'bid': bids})
        df_spread.to_csv(save_dir/'ask_bid.csv', index=False)

    def export_df_result(self, model, save_dir=None):
        totalAvgSpread, totalProfit, num_order = model.get_total_history().get_statistic()

        profit, sharpe, max_drawdown_value = self.calculate_performance_score(totalProfit, 
                                                                              num_order,
                                                                              self.opts['PIPELINE']['params']['fee'])

        df = pd.DataFrame({'avg_spread': [totalAvgSpread],
                           'num_trade': [num_order.sum()],
                           'profit': [profit],
                           'sharpe_ratio': [sharpe],
                           'max_drawdown': [max_drawdown_value]})

        if save_dir:
            df.to_csv(save_dir/'result.csv', index=False)
        return df
    

    def optimizing(self, datasets):
        gamma_list = self.opts['OPTIMIZER']['params']['gamma']['values']
        num_of_spread_list = self.opts['OPTIMIZER']['params']['num_of_spread']['values']
        historical_window_size_list = self.opts['OPTIMIZER']['params']['historical_window_size']['values']
        min_second_time_step_list = self.opts['OPTIMIZER']['params']['min_second_time_step']['values']
        def objective(trial):
            self.opts['PIPELINE']['params']['gamma'] = trial.suggest_categorical('gamma', gamma_list)
            self.opts['PIPELINE']['params']['num_of_spread'] = trial.suggest_categorical('num_of_spread', num_of_spread_list)
            self.opts['PIPELINE']['params']['historical_window_size'] = trial.suggest_categorical('historical_window_size', historical_window_size_list)
            self.opts['PIPELINE']['params']['min_second_time_step'] = trial.suggest_categorical('min_second_time_step', min_second_time_step_list)

            _, sharpe, _ = self.run_dataset(datasets, type_data='train', is_visualize=False)
            return sharpe
        
        return objective
    

    def fit(self):
        study = optuna.create_study(study_name=self.opts['OPTIMIZER']['params']['study_name'], 
                                    storage=self.opts['OPTIMIZER']['params']['storage'],
                                    load_if_exists=self.opts['OPTIMIZER']['params']['load_if_exists'],
                                    direction='maximize')
        
        
        objective = self.optimizing(self.train_data)
        # optimization
        if self.opts['PIPELINE']['params']['is_optimization']:
            study.optimize(objective, n_trials=self.opts['OPTIMIZER']['params']['n_trials'])
            best_params = study.best_params

            self.opts['PIPELINE']['params']['gamma'] = best_params['gamma']
            self.opts['PIPELINE']['params']['num_of_spread'] = best_params['num_of_spread']
            self.opts['PIPELINE']['params']['historical_window_size'] = best_params['historical_window_size']
            self.opts['PIPELINE']['params']['min_second_time_step'] = best_params['min_second_time_step']

        # Start fitting with best params
        train_result = self.run_dataset(self.train_data, type_data='train')
        val_result = self.run_dataset(self.val_data, type_data='val')
          

    def run_dataset(self, datasets, type_data='train', is_visualize=True):
        save_dir = self.opts['PIPELINE']['params']['save_dir']
        name_logger = str(save_dir.parents[0].stem)
        name_logger = f"{type_data}_logger_{name_logger}" 
        logger = self._init_logging(self.opts['PIPELINE']['params']['save_dir']/type_data/'log.txt', name=name_logger)
        visualizer = VISUALIZER(fees=self.opts['PIPELINE']['params']['fee'])
        distinct_symbols = datasets['tickersymbol'].unique()
        
        model = Bot(self.opts['PIPELINE']['params'])
        logger.info("Start fitting model")
        logger.info("with parameters: ")
        logger.info(self.opts['PIPELINE']['params'])
        for symbol in distinct_symbols:
            start_time_1m = time.time()
            monthly_data = datasets[datasets['tickersymbol'] == symbol].drop(['tickersymbol'], axis=1).to_numpy()

            first_date = monthly_data[0][0]
            num_day = get_num_days_to_maturity(symbol, first_date)
            self.opts['PIPELINE']['params']['M'] = num_day
            
            logger.info(f"Start fitting model for {symbol}")
            model.fit(monthly_data)
            
            end_time_1m = time.time()

            logger.info(f"Execution time for {symbol}: {end_time_1m - start_time_1m}")
            self._log_results(logger,model, symbol)
            
            self.report_monthly_data(model, save_dir=self.opts['PIPELINE']['params']['save_dir']/type_data/symbol)
            if is_visualize:
                visualizer.visualize_monthly_data(bot_data=model.get_monthly_history(),
                                                  bot_data_market_time_price=model.monthly_tick_data,
                                                  symbol=symbol,
                                                  save_dir=self.opts['PIPELINE']['params']['save_dir']/type_data)
        
        name = f"trading_with_maximum_inventory{self.opts['PIPELINE']['params']['maximum_inventory']}_windowsize{self.opts['PIPELINE']['params']['historical_window_size']}_min_second_time_step{self.opts['PIPELINE']['params']['min_second_time_step']}"
        if is_visualize:
            visualizer.visualize_total_data(model.total_history_data_order, 
                                            self.opts['PIPELINE']['params']['save_dir']/type_data,
                                            name=name)
        self.export_df_result(model, self.opts['PIPELINE']['params']['save_dir']/type_data)

        _, totalProfit, num_order = model.get_total_history().get_statistic()

        profit, sharpe, max_drawdown_value = self.calculate_performance_score(totalProfit, 
                                                                              num_order,
                                                                              self.opts['PIPELINE']['params']['fee'])
        
        logger.info(f"result on {type_data} with profit_return {profit}    sharpe {sharpe}   mdd {max_drawdown_value}")
        return profit, sharpe, max_drawdown_value
    
    def init_opts_papetrading(self, type_data = 'papertrading', name_logger='papertrading'):
        logger = self._init_logging(self.opts['PIPELINE']['params']['save_dir']/type_data/'log.txt', name=name_logger)
        visualizer = VISUALIZER(fees=self.opts['PIPELINE']['params']['fee'])
        model = Bot(self.opts['PIPELINE']['params'])

    def redis_message_handler(redis_message):

        quote = json.loads(redis_message['data'])
        cur_price = quote['latest_matched_price']

    def run_papertrading(self, redis_client):
        # check connection to redis OK
        print(redis_client.ping())

        # current_date = datetime.now()
        # tickersymbol = make_date_to_tickersymbol(current_date)
        # F1M_CHANNEL = f'HNXDS:{tickersymbol}'

        # pub_sub = redis_client.pubsub()

        # # subcribe to channel F1M channel
        # # register a callback function to handle message received from redis-server
        # pub_sub.psubscribe(**{F1M_CHANNEL: redis_message_handler})
        # pubsub_thread = pub_sub.run_in_thread(sleep_time=1)

        # time.sleep(60)

        # pubsub_thread.stop()

        # print('FINISH.')