import yaml
import pandas as pd


def load_yaml(path):
    with open(path, 'rt') as f:
        return yaml.safe_load(f)
    
def load_csv(path):
    return pd.read_csv(path)

def write_yaml(data, path):
    with open(path, 'wt') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)