import os
import time
import pytz
import json
import logging
import optuna
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.bot.bot import Bot
from src.optimizers.bruteforce_optimizer import BruteForceOptimizer
from src.data.data_type import Tickdata
from src.metrics import sharpe_ratio, maximum_drawdown
from src.utils.visualizer import VISUALIZER

from utils.file_management import load_csv
from utils.date_management import make_date_to_tickersymbol
from utils.path_management import increment_path
from utils.file_management import write_yaml

from plutus.core.instrument import Instrument
from plutus.datahub.redis_datahub import RedisDataHub, RedisDataHandler, InternalDataHubQuote


TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')
class Pipeline():
    def __init__(self, opts):
        self.opts = opts
        if 'DATASET' in opts:
            self.train_data = load_csv(opts['DATASET']['TRAIN']['csv_file'])
            self.val_data = load_csv(opts['DATASET']['VAL']['csv_file'])
            self.test_data = load_csv(opts['DATASET']['TEST']['csv_file'])

        self.logger = None
        self.current_symbol = None
        self.model = None
        self.visualizer = None

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

        profit, sharpe, max_drawdown_value = self.calculate_performance_score(
            totalProfit,
            num_order,
            self.opts['PIPELINE']['params']['fee']
        )

        df = pd.DataFrame({
            'avg_spread': [totalAvgSpread],
            'num_trade': [num_order.sum()],
            'profit': [profit],
            'sharpe_ratio': [sharpe],
            'max_drawdown': [max_drawdown_value]
        })

        if save_dir:
            df.to_csv(save_dir/'result.csv', index=False)
        return df

    def optuna_optimizing(self, datasets):
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
        best_params = None
        # optimization
        if self.opts['PIPELINE']['params']['is_optimization']:
            optimizer = BruteForceOptimizer(self.opts['OPTIMIZER'])
            best_params, best_sharpe = optimizer.optimize_sharpe_parallel(self.train_data, self.run_dataset, self.opts)

        # Start fitting with best params
        self.run_dataset(self.train_data, type_data='train', params=best_params)
        self.run_dataset(self.val_data, type_data='val', params=best_params)
          

    def run_dataset(self, datasets, type_data='train', is_visualize=True, params=None, prefix_logger=""):
        tmp_opts = self.opts.copy()
        save_dir = tmp_opts['PIPELINE']['params']['save_dir']
        if "exp" in str(save_dir):
            save_dir = save_dir.parents[0]
        save_dir = increment_path(save_dir/"exp", mkdir=True)
        tmp_opts['PIPELINE']['params']['save_dir'] = save_dir

        write_yaml(tmp_opts, save_dir/'config.yaml')
        
        if params:
            tmp_opts['PIPELINE']['params']['gamma'] = params['gamma']
            tmp_opts['PIPELINE']['params']['num_of_spread'] = params['num_of_spread']
            tmp_opts['PIPELINE']['params']['historical_window_size'] = params['historical_window_size']
            tmp_opts['PIPELINE']['params']['min_second_time_step'] = params['min_second_time_step']
        
        save_dir = tmp_opts['PIPELINE']['params']['save_dir']
        name_logger = prefix_logger+str(save_dir.parents[0].stem)
        name_logger = f"{type_data}_logger_{name_logger}" 
        
        os.makedirs(save_dir/type_data, exist_ok=True)
        logger = self._init_logging(tmp_opts['PIPELINE']['params']['save_dir']/type_data/'log.txt', name=name_logger)
        visualizer = VISUALIZER(fees=tmp_opts['PIPELINE']['params']['fee'])
        distinct_symbols = datasets['tickersymbol'].unique()
        
        model = Bot(tmp_opts['PIPELINE']['params'])
        logger.info("Start fitting model")
        logger.info("with parameters: ")
        logger.info(tmp_opts['PIPELINE']['params'])
        for symbol in distinct_symbols:
            start_time_1m = time.time()
            monthly_data = datasets[datasets['tickersymbol'] == symbol].drop(['tickersymbol'], axis=1).to_numpy()
            
            logger.info(f"Start fitting model for {symbol}")
            model.fit(monthly_data)
            
            end_time_1m = time.time()

            logger.info(f"Execution time for {symbol}: {end_time_1m - start_time_1m}")
            logger.info("params: ", tmp_opts['PIPELINE']['params'])
            self._log_results(logger,model, symbol)
            
            self.report_monthly_data(model, save_dir=tmp_opts['PIPELINE']['params']['save_dir']/type_data/symbol)
            if is_visualize:
                visualizer.visualize_monthly_data(bot_data=model.get_monthly_history(),
                                                  bot_data_market_time_price=model.monthly_tick_data,
                                                  symbol=symbol,
                                                  save_dir=tmp_opts['PIPELINE']['params']['save_dir']/type_data)
        
        name = f"trading_with_maximum_inventory{tmp_opts['PIPELINE']['params']['maximum_inventory']}_windowsize{tmp_opts['PIPELINE']['params']['historical_window_size']}_min_second_time_step{tmp_opts['PIPELINE']['params']['min_second_time_step']}"
        if is_visualize:
            visualizer.visualize_total_data(model.total_history_data_order, 
                                            tmp_opts['PIPELINE']['params']['save_dir']/type_data,
                                            name=name)
        self.export_df_result(model, tmp_opts['PIPELINE']['params']['save_dir']/type_data)

        _, totalProfit, num_order = model.get_total_history().get_statistic()

        profit, sharpe, max_drawdown_value = self.calculate_performance_score(totalProfit, 
                                                                              num_order,
                                                                              tmp_opts['PIPELINE']['params']['fee'])
        
        logger.info(f"result on {type_data} with profit_return {profit}    sharpe {sharpe}   mdd {max_drawdown_value}")
        return profit, sharpe, max_drawdown_value

    def data_handler_func(self, instrument: Instrument, internal_data_quote: InternalDataHubQuote):
        cur_price = internal_data_quote.latest_matched_price

        now = datetime.fromtimestamp(internal_data_quote.timestamp).astimezone(TIMEZONE)
        if cur_price is None:
            self.logger.info(f"There is no price update yet at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            return

        instrument_str = str(instrument)

        if self.current_symbol is None:
            self.current_symbol = instrument_str
            self.model.init_capacity_every_month()
        elif self.current_symbol != instrument_str:
            self.visualizer.visualize_monthly_data(
                bot_data=self.model.get_monthly_history(),
                bot_data_market_time_price=self.model.monthly_tick_data,
                symbol=self.current_symbol,
                save_dir=self.opts['PIPELINE']['params']['save_dir'] / 'papertrading'
            )
            self._log_results(self.logger, self.model, self.current_symbol)
            self.report_monthly_data(
                self.model,
                save_dir=self.opts['PIPELINE']['params']['save_dir'] / 'papertrading' / self.current_symbol
            )
            self.model.init_capacity_every_month()

        self.model.fit_tickdata(Tickdata(now, cur_price))

    def run_papertrading(self, redis_datahub: RedisDataHub):
        os.makedirs(self.opts['PIPELINE']['params']['save_dir'], exist_ok=True)
        self.logger = self._init_logging(self.opts['PIPELINE']['params']['save_dir']/f'papertrading_log.txt', name='papertrading_logger')
        self.model = Bot(self.opts['PIPELINE']['params'], logger=self.logger)
        self.visualizer = VISUALIZER(fees=self.opts['PIPELINE']['params']['fee'])
        current_date = datetime.now()
        ticker_symbol = make_date_to_tickersymbol(current_date)
        instrument = Instrument(ticker_symbol=ticker_symbol, exchange_code_str='HNXDS')
        self.logger.info(f"Start papertrading with tickersymbol {ticker_symbol}")
        self.logger.info(f"with parameters: {self.opts['PIPELINE']['params']}")

        f1m_channel_pattern = instrument.id

        data_handler = RedisDataHandler(
            data_handler_function=self.data_handler_func,
            subscribed_pattern=f1m_channel_pattern,
            run_in_thread=True,
            sleep_time=1,
        )
        redis_datahub.data_handler_list.append(data_handler)
        redis_datahub.start_pubsub()
