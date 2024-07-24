
# DeepMM

 DeepMM (Deep dive Market Making) module is a Python package for backtesting, analysing and optimizing trading strategies. It includes a number of pre-implemented strategies, but it is also possible to create new strategies, as well as to combine them.

# Model we tried

We tried out a variety of different strategies and market making around the midprice:
- Avellaneda-Stoikov Market Making Model. This model allowed us to adjust for inventory and volatility in a much more profitable way. Refer `src/strategy/market_making.py`


# Getting started


For detailed user guides and advanced guides, please refer to our documentation:
* User guides:
    <details>
    <summary>Details</summary>
        <ul>
        <li> <a href='./docs/en/user_guides/installation.md'>Installation</a></li>
        <li> <a href='./docs/en/user_guides/preparing_dataset.md'>Data preparation</a></li>
        <li> <a href='./docs/en/user_guides/run.md'>Run</a></li>
        </ul>
    </details>


We also provide the experiment on [colab](https://colab.research.google.com/drive/1gnMGsCedhIbKEm4xRO7utDPsQAFcxTXm?usp=sharing)


# References
- [Avellaneda M. & Stoikov S. (2006). High Frequency Trading in a Limit Order Book](https://www.researchgate.net/publication/24086205_High_Frequency_Trading_in_a_Limit_Order_Book)