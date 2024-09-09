# Installation
This section guides you through installing the necessary software to run the pipeline
## Clone the GitHub repo
The GitHub repo can be cloned by running
```bash
git clone git@github.com:algotrade-research/deepmm.git
```
Please make sure you have the correct credentials/privilege to run that command.

Or download the zip file through the repo main page: `https://github.com/algotrade-research/deepmm`

## Create a virtual environment
After cloning or downloading the source code, go to the source root, open a terminal or a command prompt, then run the following to create a virtual environment.
### By using venv
```bash
python -m venv .venv
```
where `.venv` is the folder contain the virtual environment. Refer to this [tutorial](https://docs.python.org/3/library/venv.html) for more information.

Then activate the environment by running:
```bash
source .venv/bin/activate
```

Then install the packages by `pip` through the `requirements.txt` file by running:
```bash
pip install -r requirements.txt
```

Now the project can be run.

### Or by using Anaconda
You can also use Anaconda to create a virtual environment. Refer to the steps below.
Run the following command to create a conda environment based on the specifications in a file named `enviroments.yaml`
```bash
conda env create -f environments.yaml
```

This command will create a new conda environment with all the required dependencies listed in the `enviroments.yaml` file.
Note: You might need to activate the newly created environment before proceeding. Refer to your conda documentation for activation instructions specific to your operating system.
####  Install Additional Packages (if applicable)
In some cases, there might be additional packages required that are not included in the `enviroments.yaml` file. These additional packages are likely specified in a separate file named `requirements.txt`.

If a `requirements.txt` file exists, run the following command to install those additional packages

