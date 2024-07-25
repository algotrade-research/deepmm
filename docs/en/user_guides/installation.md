# Installation
This section guides you through installing the necessary software to run the pipeline
## Create enviroment
1. Open your terminal or command prompt.
2. Run the following command to create a conda environment based on the specifications in a file named `enviroments.yaml`
```bash
conda env create -f environments.yaml
```
This command will create a new conda environment with all the required dependencies listed in the `enviroments.yaml` file.

Note: You might need to activate the newly created environment before proceeding. Refer to your conda documentation for activation instructions specific to your operating system.


##  Install Additional Packages (if applicable)
In some cases, there might be additional packages required that are not included in the `enviroments.yaml` file. These additional packages are likely specified in a separate file named `requirements.txt`.

If a `requirements.txt` file exists, run the following command to install those additional packages
```bash
pip install -r requirements.txt
```
