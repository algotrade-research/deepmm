![Static Badge](https://img.shields.io/badge/PLUTUS-50%25-%23BA8E23)
![Static Badge](https://img.shields.io/badge/PLUTUS-Sample-darkblue)


# DeepMM: Deep Dive Market Making

## Overview

**DeepMM** (Deep Dive Market Making) is a Python-based framework designed for backtesting, analyzing, and optimizing market-making trading strategies. It offers a modular architecture that supports the implementation of custom strategies and includes pre-implemented models like the Avellaneda-Stoikov model.

## Table of Contents

1. [Installation](#installation)
2. [Data Acquisition](#data-acquisition)
3. [Quick Start](#quick-start)
4. [Project Structure](#project-structure)
5. [Strategy Implementation](#strategy-implementation)
6. [Backtesting](#backtesting)
7. [Optimization](#optimization)
8. [Out-of-Sample Testing](#out-of-sample-testing)
9. [Paper Trading](#paper-trading)
10. [Results](#results)
11. [Contributing](#contributing)
12. [License](#license)

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/algotrade-research/deepmm.git
   cd deepmm
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Installing Plutus:**
- The Plutus source code (in zip file) can be downloaded [here](https://drive.google.com/file/d/1O6i_B6EhxJ1EijGl0MHNPhykG21QD1Zz/view?usp=drive_link).
- After downloading the source code, Plutus package can be installed by running:
    ```bash
    pip install path/to/the/zip/file/plutus-0.0.1.zip
    ```

---

## Data Acquisition

To run simulations, you'll need historical market data. There are two options to acquire the data:
1. **Option 1: Download data from the database:**

   ```bash
   python download_data_from_db.py
   ```

   *Ensure that your database credentials and configurations are set appropriately in `configs/`.*

2. **Option 2: Downloading Data from algotrade public datasets**

- A comprehensive dataset, meticulously curated by algotrade experts, is available for download though [link](https://drive.google.com/drive/folders/1ZJzFUcxd5mdt8MA9r7lhx3MY1zw1uqdY?usp=sharing). This dataset contains a vast quantity of data points specifically designed to serve as a benchmark for scientific experimentation.
- Unzip the dataset into the source root under the folder `datasetATDB`. Inside the folder, there should be three CSV files: `train.csv`, `test.csv`, `val.csv`.

3. **Data Structure:**

   The data should be structured as follows:

   ```
   datasetATDB/
   └── [instrument_name]/
       ├── [date].csv
       └── ...
   ```

You can read more the data [here](./docs/en/user_guides/preparing_dataset.md).

---

## Quick Start

After setting up the environment and acquiring data:

1. **Run a backtest:**

   ```bash
   python run.py -c [path_to_config_file]
   ```

2. **Run paper trading simulation:**

   ```bash
   python run_papertrading.py -c [path_to_config_file]
   ```

*Configuration parameters can be adjusted in `configs/`.*

---

## Project Structure

```
deepmm/
├── configs/               # Configuration files
├── datasetATDB/           # Market data
├── docs/                  # Documentation
├── src/                   # Source code
│   ├── strategy/          # Strategy implementations
│   └── ...                # Other modules
├── utils/                 # Utility functions
├── download_data_from_db.py
├── run.py                 # Backtesting script
├── run_papertrading.py    # Paper trading script
├── requirements.txt
└── README.md
```

---

## Strategy Implementation

The framework includes the **Avellaneda-Stoikov Market Making Model**, which adjusts quotes based on inventory and market volatility.

- **Location:** `src/strategy/asmodel.py`

You can implement custom strategies by extending the base strategy class provided in the framework.

---

## Backtesting

To perform in-sample backtesting:

```bash
python run.py -c [path_to_config_file]
```

- **Configuration:** Modify `configs/parameters/pseudo_marketmaking.yaml` to set parameters like timeframes, instruments, and strategy-specific settings.

- **Output:** Results will be saved in the `results/` directory, including performance metrics and logs.

---

## Optimization

To optimize strategy parameters:

1. **Set up optimization configurations:**

   Modify `configs/optimization_config.yaml` to define parameter ranges and optimization criteria.

2. **Run optimization:**

   ```bash
   python run_optimization.py
   ```

- **Output:** The best-performing parameter sets and corresponding performance metrics will be stored in `results/optimization/`.

---

## Out-of-Sample Testing

To evaluate the strategy on unseen data:

1. **Adjust the configuration:**

   Set the `mode` to `out_of_sample` in `configs/backtest_config.yaml`.

2. **Run the backtest:**

   ```bash
   python run.py
   ```

- **Output:** Performance metrics and logs will be saved in `results/out_of_sample/`.

---

## Paper Trading

Simulate live trading using historical data to assess strategy performance in real-time conditions.

```bash
python run_papertrading.py
```

- **Configuration:** Modify `configs/paper_trading_config.yaml` to set parameters like latency, slippage, and execution constraints.

- **Output:** Real-time logs and performance summaries will be available in `results/paper_trading/`.

---

## Results

### In-Sample Backtesting

- **Sharpe Ratio:** 1.85
- **Max Drawdown:** 4.2%
- **Total Return:** 12.5%

### Optimization

- **Best Parameters:**
  - Inventory Risk Aversion (`gamma`): 0.3
  - Order Book Depth (`k`): 1.5

- **Performance:**
  - **Sharpe Ratio:** 2.1
  - **Max Drawdown:** 3.8%
  - **Total Return:** 14.2%

### Out-of-Sample Testing

- **Sharpe Ratio:** 1.9
- **Max Drawdown:** 4.0%
- **Total Return:** 13.0%

### Paper Trading

- **Realized PnL:** $1,250
- **Number of Trades:** 320
- **Win Rate:** 58%

*Note: The above results are illustrative. Actual performance may vary based on market conditions and data quality.*

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository.**
2. **Create a new branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit your changes:**

   ```bash
   git commit -m "Description of your changes"
   ```

4. **Push to your fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a pull request.**

Please ensure that your code adheres to the project's coding standards and includes appropriate tests.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more information and detailed documentation, please refer to the `docs/` directory.
