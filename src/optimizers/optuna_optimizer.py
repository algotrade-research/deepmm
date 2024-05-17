
import optuna

class Optimzer():
    def __init__(self, opts):
        self.opts = opts
        self.study = optuna.create_study(study_name=opts['OPTIMIZER']['study_name'], 
                                         storage=opts['OPTIMIZER']['storage'],
                                         load_if_exists=self.opts['OPTIMIZER']['load_if_exists'],
                                         direction='maximize')

    def optimize_sharpe(self, datasets, objective, n_trials):
        self.study.optimize(objective, n_trials=n_trials)
    
    def optuna_optimizing(self, datasets, run_dataset):
        gamma_list = self.opts['OPTIMIZER']['params']['gamma']['values']
        num_of_spread_list = self.opts['OPTIMIZER']['params']['num_of_spread']['values']
        historical_window_size_list = self.opts['OPTIMIZER']['params']['historical_window_size']['values']
        min_second_time_step_list = self.opts['OPTIMIZER']['params']['min_second_time_step']['values']
        def objective(trial):
            self.opts['PIPELINE']['params']['gamma'] = trial.suggest_categorical('gamma', gamma_list)
            self.opts['PIPELINE']['params']['num_of_spread'] = trial.suggest_categorical('num_of_spread', num_of_spread_list)
            self.opts['PIPELINE']['params']['historical_window_size'] = trial.suggest_categorical('historical_window_size', historical_window_size_list)
            self.opts['PIPELINE']['params']['min_second_time_step'] = trial.suggest_categorical('min_second_time_step', min_second_time_step_list)

            _, sharpe, _ = run_dataset(datasets, type_data='train', is_visualize=False)
            return sharpe
        
        return objective