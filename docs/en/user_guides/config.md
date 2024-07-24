# Configuration document descriptions
Pipeline Parameters for Market Making (v1.0.0)
This pipeline implements the Avellaneda-Stoikov model for market making.

## General Parameters:

* fee (float): Transaction fee charged per trade (eg: 0.125 points).
* save_dir (str): Directory to save the pipeline's output files. (eg: "runs/market_making")
* is_optimization (bool): Flag indicating if the pipeline is running in optimization mode (potentially tuning hyperparameters).

## Market Making Specific Parameters:
* maximum_inventory (int): Maximum number of underlying assets the pipeline will hold at any given time (prevents excessive risk). (eg: 35)
* num_of_spread (float): Target spread between the bid and ask prices quoted by the pipeline (e.g., current price is 10 and spread is 3, if num_of_spread is 2.0, then bid-ask price will be 4 and 16 respectively).
* gamma (float): Risk aversion parameter used in the Avellaneda-Stoikov model (higher values indicate lower risk tolerance).
* historical_window_size (int): Number of days of historical data used to calculate the underlying asset's volatility.
* min_second_time_step (int): Minimum time (in seconds) between order updates placed by the pipeline.
* close_at (str): Time of day to cease quoting prices and unwind any remaining inventory. (eg: "14:20:45")
* start_at (str): Time of day to begin quoting prices and actively participate in the market. (eg: "09:00:00")

## Optimizer
* name: Name of the optimizer used for hyperparameter tuning
* params: Configuration parameters for the optimizer.

    * n_trials (50): Number of independent trials to run during the optimization process.
    * study_name ("market_making"): Name of the optimization study for logging and tracking purposes.
    * storage ("sqlite:///market_making.db"): Location to store optimization data (uses SQLite database).
    * load_if_exists (True): Flag indicating if existing optimization results should be loaded (useful for resuming interrupted runs).

## Dataset:

* TRAIN, VAL, TEST: Definitions for training, validation, and testing datasets used by the pipeline.
    * csv_file: Path to the CSV file containing the market data for each set.


This configuration provides a detailed explanation of all parameters used in the market making pipeline, optimizer, and dataset specifications.

# Custom Flags for Pipeline Configuration
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
