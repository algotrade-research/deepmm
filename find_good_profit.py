import numpy as np


def main():
    log_file_path = "/Users/danhle/algotrade/deepmm/runs/market_making/exp/train/log.txt"
    
    log_file = open(log_file_path, "r")
    lines = log_file.readlines()
    log_file.close()
    num_iters = len(lines) // 114
    best_sharpe = -np.inf
    best_indext = 0
    for i in range(num_iters):
        start = i * 114
        end = start + 114
        iter_lines = lines[start:end]
        last_line = iter_lines[-1]
        sharpe_str = last_line.split("    ")[-1].split("   ")[0].split()[-1]
        sharpe = float(sharpe_str)
        
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_index = i
        # profit = float(iter_lines[-1].split()[-1])
        # if profit > 0:
        #     print(f"iter {i}: {profit}")

    print(f"Best sharpe: {best_sharpe} at iter {best_index}/{num_iters} at {best_index * 114}th iteration")
    # patterns


if __name__ == '__main__':
    main()