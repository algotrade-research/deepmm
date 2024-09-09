import numpy as np

def maximum_drawdown(returns):
    """
    Calculate the maximum drawdown of a strategy.
    
    Parameters:
    returns (np.array): The returns of the strategy.
    """

    if len(returns) == 0:
        return 0
    cum_returns = np.cumprod(1+returns)

    peak = np.maximum.accumulate(cum_returns)
    trough = np.minimum.accumulate(cum_returns)
    drawdown = (peak - trough) / peak
    max_drawdown = np.max(drawdown)
    return max_drawdown

