Content Scrapper for zno.osvita.ua questions
==============================================

## Prerequisites ##

### Install virtualenv and virtualenvwrapper ###

Ubuntu: http://askubuntu.com/questions/244641/how-to-set-up-and-use-a-virtual-python-environment-in-ubuntu

## Installation ##

### Creating the environment ###
Create a virtual python environment for the project. Use Python 3.7.4 version.

#### For virtualenvwrapper ####
```bash
mkvirtualenv zno-simulator
```

#### For virtualenv ####
```bash
virtualenv zno-simulator
source zno-simulator/bin/activate
```

### Clone the code ###
```bash
git clone git@github.com:vasyabigi/zno-simulator.git
```

### Install requirements ###
```bash
cd zno-simulator/content
pip install -r requirements.txt
```
## Running script ##
```bash
cd zno-simulator
python -m zno-parser.main
```
