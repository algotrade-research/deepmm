import optuna

class Optimizer:
    def __init__(self, opts):
        self.opts = opts
        self.study = optuna.create_study(
                                study_name=opts['params']['study_name'], 
                                sampler=optuna.samplers.BruteForceSampler(),   # possible to change optuna.samplers.TPESampler(seed=10)
                                storage=opts['params']['storage'],
                                load_if_exists=opts['params']['load_if_exists'],
                                direction='maximize')

    def optimize_sharpe(self, datasets, objective, full_opts):
        
        gamma_list = self.opts['params']['gamma']['values']
        num_of_spread_list = self.opts['params']['num_of_spread']['values']
        historical_window_size_list = self.opts['params']['historical_window_size']['values']
        min_second_time_step_list = self.opts['params']['min_second_time_step']['values']
        def optuna_objective(trial):
            tmp_opts = full_opts.copy()
            tmp_opts['PIPELINE']['params']['gamma'] = trial.suggest_categorical('gamma', gamma_list)
            tmp_opts['PIPELINE']['params']['num_of_spread'] = trial.suggest_categorical('num_of_spread', num_of_spread_list)
            tmp_opts['PIPELINE']['params']['historical_window_size'] = trial.suggest_categorical('historical_window_size', historical_window_size_list)
            tmp_opts['PIPELINE']['params']['min_second_time_step'] = trial.suggest_categorical('min_second_time_step', min_second_time_step_list)

            _, sharpe, _ = objective(datasets, type_data='train', is_visualize=False, params = tmp_opts['PIPELINE']['params'])
            return sharpe
        
        self.study.optimize(optuna_objective, n_trials=self.opts['params']['n_trials'], n_jobs=8)
        best_params = self.study.best_params
        best_sharpe = self.study.best_value
        return best_params, best_sharpe