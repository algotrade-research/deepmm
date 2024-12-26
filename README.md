# Abstract

 DeepMM (Deep dive Market Making) module is a Python package for backtesting, analyzing and optimizing trading 
 strategies. It includes a number of pre-implemented strategies, but it is also possible to create new strategies, as 
 well as to combine them.

# Introduction

In this work, we implemented a variety of different strategies and market making around the midprice.
Specifically, we implemented Avellaneda-Stoikov Market Making Model [1]. This model allowed us to adjust for inventory 
and volatility in a much more profitable way. Detailed implementation of this model is given in file 
`src/strategy/asmodel.py`.

# Implementation

In this section, we demonstrate steps to install and run the project and reproduce the experimental results.

## Installation

This section guides you through installing the necessary software to run the pipeline

### Clone the GitHub repo
The GitHub repo can be cloned by running
```bash
git clone git@github.com:algotrade-research/deepmm.git
```
Please make sure you have the correct credentials/privilege to run that command.

Or download the zip file through the repo main page: `https://github.com/algotrade-research/deepmm`

### Create a virtual environment

This project use Python 3.12. Make sure you are using Python 3.12 to create virtual environment.

Run the following to create a virtual environment.
```bash
python -m venv .venv
```
where `.venv` is the folder contain the virtual environment. Refer to this [tutorial](https://docs.python.org/3/library/venv.html) for more information.

Then activate the environment by running:
```bash
source .venv/bin/activate
```

Then install the packages by `pip` through the `requirements.txt` file by running:
```bash
pip install -r requirements.txt
```

### Installing Plutus
The Plutus source code (in zip file) can be downloaded [here](https://drive.google.com/file/d/1O6i_B6EhxJ1EijGl0MHNPhykG21QD1Zz/view?usp=drive_link).

After downloading the source code, Plutus package can be installed by running:
```bash
pip install path/to/the/zip/file/plutus-0.0.1.zip
```

Now the project can be run.

## Data

### Data Format
deepmm works with data formatted like this:
```
datetime,price,tickersymbol
```
Here's what each column means:
- datetime: The timestamp for each piece of data.
- price: The price of the asset at that timestamp.
- tickersymbol: The symbol for the asset (e.g., VN30F2304).

### Downloading Data from algotrade public datasets

A comprehensive dataset, meticulously curated by algotrade experts, is available for download though [link](https://drive.google.com/drive/folders/1ZJzFUcxd5mdt8MA9r7lhx3MY1zw1uqdY?usp=sharing). This dataset contains a vast quantity of data points specifically designed to serve as a benchmark for scientific experimentation.

Unzip the dataset into the source root under the folder `datasetATDB`. Inside the folder, there should be three CSV files: `train.csv`, `test.csv`, `val.csv`.

## Configuration File

### General Parameters

* fee (float): Transaction fee charged per trade (default 0.125 points).
* save_dir (str): Directory to save the pipeline's output files. (eg: "runs/market_making")
* is_optimization (bool): Flag indicating if the pipeline is running in optimization mode (potentially tuning hyperparameters).

### Market Making Specific Parameters
* maximum_inventory (int): Maximum number of underlying assets the pipeline will hold at any given time (prevents excessive risk). (eg: 35)
* num_of_spread (float): Target spread between the bid and ask prices quoted by the pipeline (e.g., current price is 10 and spread is 3, if num_of_spread is 2.0, then bid-ask price will be 4 and 16 respectively).
* gamma (float): Risk aversion parameter used in the Avellaneda-Stoikov model (higher values indicate lower risk tolerance).
* historical_window_size (int): Number of days of historical data used to calculate the underlying asset's volatility.
* min_second_time_step (int): Minimum time (in seconds) between order updates placed by the pipeline.
* close_at (str): Time of day to stop retrieving prices and release any remaining inventory. (default: "14:20:45")
* start_at (str): Time of day to begin retrieving prices and actively participate in the market. (default: "09:00:00")

### Dataset:

* TRAIN, VAL, TEST: Definitions for training, validation, and testing datasets used by the pipeline.
    * csv_file: Path to the CSV file containing the market data for each set.

### Custom Flags for Pipeline Configuration
This section explains how to modify specific pipeline parameters at runtime using command-line flags. These flags override the defaults defined in the configuration file.

Example:
```bash
python run.py -c configs/parameters/pseudo_marketmaking.yaml -o PIPELINE.params.save_dir='new_exp'
```

In this example:

* `python run.py`: This launches the Python script (`run.py`) that executes the pipeline.
* `-c configs/parameters/pseudo_marketmaking.yaml`: This flag specifies the configuration file (`pseudo_marketmaking.yaml`) containing the default pipeline parameters.
* `-o PIPELINE.params.save_dir='new_exp'`: This is the custom flag denoted by `-o`. It overrides the default value for the `save_dir` parameter within the `PIPELINE.params` section of the configuration file. Here, we're setting the new directory to `new_exp`.

**Note**: Essentially, you can use the `-o` flag followed by the desired parameter path and its new value to customize specific parameters on the fly without modifying the configuration file itself.

## Training Pipeline

Run the Training Script: Execute the following command in your terminal, replacing `[path_to_config_file]` with the actual path to your configuration file:

```bash
python run.py -c configs/parameters/pseudo_marketmaking.yaml
```
This command launches the run.py script, performs optimization (brute-force all possible combinations of parameters 
specified in `OPTIMIZER` section), and use the best parameter combination (highest Sharpe Ratio) to on Training and 
Validation data.

It is worth noting that running hyper-parameter optimization can take a very long time, depending on data size and 
number of possible combinations in hyper-parameters. The default brute-force search will take one week continuously 
running on a Macbook Pro 2019 laptop. To reduce the running time, one can reduce the number of possible values for each 
hyper-parameters in `OPTIMIZER` section. 

After the optimization phase, one can use the best parameters picked by the optimizer (best sharpe ratio in the 
training data) for subsequent experimental result (back testing and paper trading).

## Back-testing (running inference without searching hyper-parameters)
If you only want to use the trained model for predictions (inference) without retraining (skipping optimization phase), use the following command:
```bash
python run.py -c configs/parameters/pseudo_marketmaking.yaml -o PIPELINE.params.is_optimization=False
```

This command runs the pipeline with the parameters defined in the configuration file but disables the optimization phase (`is_optimization=False`). This means the pipeline will use the pre-trained model for inference without searching for better hyperparameters.

The back-testing results can be viewed in the accompanied document (file `docs/Algotrade_marketmaking.pdf` section 3).

## Run paper-trading

In this section, we provide instructions to perform the paper trading (use real time price data and make the 
decision) with our market making strategy. 

### Redis connection setup

The paper trading run will require connection to retrieve real time price. For this reason, one has to setup a 
connection to Algotrade's Redis. Specifically, one has to create a file `configs/usr/redis_acocunt.yaml` with the 
following information:
```yaml
host: #### 
port: ####
password: ####
```
Please contact Algotrade's team to get information about host, port, and password.

### Paper-trading configuration file

An example of configuration file is `configs/parameters/papertrading.yaml`. Market making parameters will be the 
parameters you found in the training (back-testing) process.

### Run paper trading

```bash
python run_papertrading.py -c configs/parameters/papertrading.yaml  
```
This command launches the `run_papertrading.py` script with the specified configuration file.

**Note**: This simulation will receive data during Vietnamese trading hours only. If you want to conduct offline paper trading simulations with test data, please create a separate test dataset and run the run.py script as described in the run.md documentation.

We also provide the experiment on [colab](https://colab.research.google.com/drive/1gnMGsCedhIbKEm4xRO7utDPsQAFcxTXm?usp=sharing)


# References
- [Avellaneda M. & Stoikov S. (2006). High Frequency Trading in a Limit Order Book](https://www.researchgate.net/publication/24086205_High_Frequency_Trading_in_a_Limit_Order_Book)
