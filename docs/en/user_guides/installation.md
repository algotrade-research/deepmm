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

This project use Python 3.12. Make sure you are using Python 3.12 to create virtual environment.

Run the following to create a virtual environment.
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

## Installing Plutus
The Plutus source code (in zip file) can be downloaded [here](https://drive.google.com/file/d/1O6i_B6EhxJ1EijGl0MHNPhykG21QD1Zz/view?usp=drive_link).

After downloading the source code, Plutus package can be installed by running:
```bash
pip install path/to/the/zip/file/plutus-0.0.1.zip
```

Now the project can be run.


