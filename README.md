
# DeepMM

 DeepMM (Deep dive Market Making) module is a Python package for backtesting, analysing and optimizing trading strategies. It includes a number of pre-implemented strategies, but it is also possible to create new strategies, as well as to combine them.

# Model we tried

We tried out a variety of different strategies and market making around the midprice:
- Avellaneda-Stoikov Market Making Model. This model allowed us to adjust for inventory and volatility in a much more profitable way. Refer `src/strategy/market_making.py`


# How to Run the models

## Install Enviroments
You'll need install enviroments by file `requirements.txt`
```bash
pip install -r requirements.txt
```
## Data Preparation

Preparing dataset through query data from database.
```bash
python download_data_from_db.py
```
## Run models
Create an example configs like `configs/parameters/pseudo_marketmaking` then run:
```bash
python run.py -c [path_to_config_file]
```

# References
- [Avellaneda M. & Stoikov S. (2006). High Frequency Trading in a Limit Order Book](https://www.researchgate.net/publication/24086205_High_Frequency_Trading_in_a_Limit_Order_Book)