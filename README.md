# PwC UK Housing Market Agent-Based Model in Python 2022
Agent-based models built in the late 90's early 2000s were subject to constrained programming frameworks, lacked extensibility, and are exclusively accessible by social-simulation practitioners who were the early pioneers of the most well-known ABM framework Netlogo. Many years later, a lot has changed. New programming methodologies, the rise of machine learning, data science and reproducibility frameworks have become the norm. These new methods have allowed social-simulation researchers to diversify their research, making their models more accessible reproducible and, by utilising advanced machine learning packages, uncover new insights from their models.

We propose a "remake" of the original and widely-adopted PwC UK Housing Market Agent-Based Model developed in the early 2000s by Nigel Gilbert, John C. Hawksworth and Paul A. Swinney[^1]. This new model version was developed in Python using the package MESA[^2], allowing users to utilise advanced machine learning/data science packages provided by Python's extensive collection of modern tools.

# Licence
Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg


## Instructions


### Installation
The following programming language and packages were used in the planning, development and running  stages of the model. These packages or a subsequent version will need to be installed before the model can be run locally.


1. **Python** version 3.9.7: https://www.python.org/downloads/release/python-397/
2. **Anaconda** version 4.11.0: https://www.anaconda.com/products/individual


### Install Conda Environment
A conda environmeny **.yml** file can be found in the **/model/MESA_env.yml** subdirectory. This contains the setup including python packages used to run the model. Once python and anaconda have been installed, do the following:


1. Navigate to the cloned repository directory **../Pythonic_UK_Housing_Market_ABM_2022/Model/** using terminal in OSX/Linux or command prompt using windows.
2. Type the following and hit enter:
```console
foo@bar:~$ conda env create --file MESA_env.yml
```


### Running The Model
Once the conda environment has successfully installed, you must activate the environment before you can run the model. Do this by running the following command in the directory **../Pythonic_UK_Housing_Market_ABM_2022/Model/**:
```console
foo@bar:~$ conda activate MESA_env
```


or


```console
foo@bar:~$ source activate MESA_env
```


To run the model, type the following command:
```console
(MESA_env) foo@bar:~$ python main_visualisation.py <grid_x> <grid_y> <intervention> <intervention_timestep>
```


Where the parameters within **<>** are the following:
- < grid_x >  The number of cells on the x-axis, must be an integer i.e., 60
- < grid_y >  The number of cells on the y-axis, must be an integer i.e., 60
- < intervention >  The intervention to occur, could be one of **"ratefall", "ltv", "influx", "poorentrants"** or **"none"** must be in quotation marks. Refer to the original paper[^1], to know what each intervention does.
- < intervention_timestep >  The model timestep (tick) at which the intervention should be triggered, must be an integer i.e., 200


Example:
```console
(MESA_env) foo@bar:~$ python main_visualisation.py 60 60 "ratefall" 100
```


# Important Python Scripts
To adapt the macroeconomic parameters, access the **../Pythonic_UK_Housing_Market_ABM_2022/Model/input_params.py** before running your experiments and make any changes to the parameter values, these include:
```python
def __init__(self):
        self.initialVacancyRate = 0.05
        self.nRealtors = 6
        self.InterestRate = 7.0
        self.TicksPerYear = 4
        self.maxHomelessPeriod = 5
        self.interestPerTick = self.InterestRate / (self.TicksPerYear * 100)
        self.min_price_fraction = 0.1
        self.Inflation = 0.0 # %
        self.CycleStrength = 0 # %
        self.Affordability = 25 # %
        self.Savings = 50 # %
        self.ExitRate = 2 # %
        self.EntryRate = 5 # %
        self.MeanIncome = 30000 #pa
        self.Shocked = 23 # %
        self.BuyerSearchLength = 12
        self.RealtorTerritory = 30 # originally 30
        self.Locality = 3
        self.RealtorMemory = 10 # steps
        self.PriceDropRate = 3 # %
        self.RealtorOptimism = 3 # %
        self.InitialGeography = "Random"
        self.Density = 70 # %
        self.HouseConstructionRate = 0.30 # %
        self.HouseMeanLifetime = 101
        self.MaxLoanToValue = 97 # %
        self.MortgageDuration = 25
        self.StampDuty = True # bool
```


# Footnotes
[^1]: ```Gilbert, N, Hawksworth, J C, and Sweeney, P (2008) 'An Agent-based Model of the UK Housing Market'. University of Surrey http://cress.soc.surrey.ac.uk/housingmarket/index.html```
[^2]: ```MESA: https://mesa.readthedocs.io/en/latest/overview.html```







