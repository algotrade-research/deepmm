import numpy as np

def sharpe_ratio(returns, risk_free_rate=0.03, periods_per_year=252):
    """
    Calculate the Sharpe ratio of a strategy.
    
    Parameters:
    returns (np.array): The returns of the strategy.
    risk_free_rate (float): The risk-free rate.
    periods_per_year (int): The number of periods per year. Default is 252.
    
    Returns:
    float: The Sharpe ratio of the strategy.
    """
    annual_std = np.sqrt(periods_per_year) * np.std(returns)
    annual_return = periods_per_year*np.mean(returns)  - risk_free_rate

    return annual_return / annual_std if annual_std != 0 else 0




    