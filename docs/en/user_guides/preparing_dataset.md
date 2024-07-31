# Getting Your Data Ready for deepmm
This document explains how to prepare the data you'll use with deepmm.

## Data Format
deepmm works with data formatted like this:

```
datetime,price,tickersymbol
```
Here's what each column means:

- datetime: The timestamp for each piece of data.
- price: The price of the asset at that timestamp.
- tickersymbol: The symbol for the asset (e.g., VN30F2304).
## Downloading Data from algotrade public datasets
A comprehensive dataset, meticulously curated by algotrade experts, is available for download though [link](https://drive.google.com/drive/folders/1ZJzFUcxd5mdt8MA9r7lhx3MY1zw1uqdY?usp=sharing). This dataset contains a vast quantity of data points specifically designed to serve as a benchmark for scientific experimentation.

## Downloading Data from the algotrade database (if applicable)
To gain access to the algotrade database, please contact us.
<h4>Step 1: Setting Up Database Access</h4>

To download data from the algotrade database, you'll need to create a file to store your login credentials. Create a file named db_account.yaml inside the directory `configs/usr/`. Here's an example of what the file should look like:
```yaml
host: ####      # Replace with host ip of algotrade
port: ####      # Replace with actual port
database: ####  # Replace with actual database of algotrade
user: ####      # Replace with actual username
pass: ####      # Replace with your actual password
```

Important: Make sure to replace #### with your actual information. Keep this file secure as it contains your database login information.

<h4>Step 2: Downloading the Data</h4>

Once you've set up your credentials, you can download the data using the script download_data_from_db.py. Just run the following command in your terminal:

```bash
python download_data_from_db.py
```

This script will download the data you need from the algotrade database and prepare it for use with deepmm.