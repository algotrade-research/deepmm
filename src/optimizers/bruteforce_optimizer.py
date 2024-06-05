import numpy as np
from tqdm import tqdm
import multiprocessing as mp
from utils.path_management import increment_path

def optimize_worker(datasets, params, run_dataset):
            profit, sharpe, mdd = run_dataset(datasets, 
                                              type_data='train', 
                                              is_visualize=False,
                                              params=params)
            return profit, sharpe, mdd, params

class BruteForceOptimizer():
    def __init__(self, opts, logger=None):
        self.opts = opts
        self.index_params = 0
        self.combination_params = self.generate_combination_params()
        self.logger = logger
    
    def generate_combination_params(self):
        gamma_list = self.opts['params']['gamma']['values']
        num_of_spread_list = self.opts['params']['num_of_spread']['values']
        historical_window_size_list = self.opts['params']['historical_window_size']['values']
        min_second_time_step_list = self.opts['params']['min_second_time_step']['values']
        params = []
        for gamma in gamma_list:
            for num_of_spread in num_of_spread_list:
                for historical_window_size in historical_window_size_list:
                    for min_second_time_step in min_second_time_step_list:
                        params.append({
                            'gamma': gamma,
                            'num_of_spread': num_of_spread,
                            'historical_window_size': historical_window_size,
                            'min_second_time_step': min_second_time_step,
                        })
        return params
    
    def sample_params(self):
        params = self.combination_params[self.index_params]
        self.index_params += 1
        return params
    
    def optimize_sharpe_parallel(self, datasets, run_dataset, opts, num_processes=4):
        mp.set_start_method('spawn')   
        with mp.Pool(processes=num_processes) as pool:
            all_params = self.combination_params
            # Use pool.starmap to distribute work across processes
            results = pool.starmap(optimize_worker, [(datasets, params, run_dataset) for params in all_params])

            # Process results
            best_sharpe = -np.inf
            best_params = None

            for profit, sharpe, mdd, params in results:
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = params

                if self.logger is not None:
                    self.logger.info(f'Params: {params}')
                    self.logger.info(f'Profit: {profit}')
                    self.logger.info(f'Sharpe: {sharpe}')
                    self.logger.info(f'MDD: {mdd}')
                    self.logger.info('')
                
        return best_params, best_sharpe

    def optimize_sharpe(self, datasets, run_dataset, opts):

        best_sharpe = -np.inf
        best_params = None

        for i in tqdm(range(len(self.combination_params))):
            params = self.sample_params()
            profit, sharpe, mdd = run_dataset(datasets, 
                                              type_data='train', 
                                              is_visualize=False,
                                              params=params)
            
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = params

            if self.logger is not None:
                self.logger.info(f'Combination {i+1}/{len(self.combination_params)}')
                self.logger.info(f'Params: {params}')
                self.logger.info(f'Profit: {profit}')
                self.logger.info(f'Sharpe: {sharpe}')
                self.logger.info(f'MDD: {mdd}')
                self.logger.info('')
                
        return best_params, best_sharpe