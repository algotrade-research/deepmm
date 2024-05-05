
import optuna

class Optimzer():
    def __init__(self, opts):
        self.opts = opts
        self.study = optuna.create_study(study_name=opts['OPTIMIZER']['study_name'], storage=opts['OPTIMIZER']['storage'])

    
