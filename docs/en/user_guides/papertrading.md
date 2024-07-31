# Run papertrading
This section provides instructions on how to run paper trading.
## Prepare account paper trading
### Step 1: Contact for Registration
Please reach out to the algotrade team to initiate the registration process. They will guide you through the steps and provide you with your account credentials.
### Step 2: Configure Account Credentials
Create a file named redis_account.yaml inside the directory configs/usr/. This file will store your account information securely. Here's an example of what the file should look like, replacing the #### placeholders with your actual credentials:
```yaml
host: #### 
port: ####
password: ####
```


## Run paper trading

1. Create a Configuration File: Define the training parameters in a configuration file. An example configuration file can be named `configs/parameters/papertrading.yaml`.

2. Run the Training Script: Execute the following command in your terminal, replacing `[path_to_config_file]` with the actual path to your configuration file:

```bash
python run_papertrading.py -c [path_to_config_file]
##e.g:  python run_papertrading.py -c configs/parameters/papertrading.yaml
```
This command launches the `run_papertrading.py` script with the specified configuration file.

**Note**: This simulation will receive data during Vietnamese trading hours only. If you want to conduct offline paper trading simulations with test data, please create a separate test dataset and run the run.py script as described in the run.md documentation.