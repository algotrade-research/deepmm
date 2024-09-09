from pathlib import Path

from deepmm.pipeline import Pipeline
from utils.argument_management import Opts

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]


def main():
    FLAGS = Opts().parse_args()
    
    pipeline = Pipeline(FLAGS)
    pipeline.fit()
    # pipeline.backtest()
    


if __name__ == "__main__":
    main()
    