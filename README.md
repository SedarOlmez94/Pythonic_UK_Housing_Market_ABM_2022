# PwC UK Housing Market Agent-Based Model in Python 2022
This repository contains an updated python version of the UK Housing Market Agent-Based Model originally designed and developed in Netlogo by Nigel Gilbert, John C. Hawksworth and Paul A. Swinney.


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


To run the model, type the following command:
```console
(MESA_env) foo@bar:~$ python main_visualisation.py <grid_x> <grid_y> <intervention> <intervention_timestep>
```


Where the parameters within **<>** are the following:
- <grid_x> the number of cells on the x-axis, must be an integer i.e., 60
- <grid_y> the number of cells on the y-axis, must be an integer i.e., 60
- <intervention> the intervention to occur, could be one of **"ratefall", "ltv", "influx", "poorentrants"** or **"none"** must be in quotation marks. Refer to the original paper[^1], to know what each intervention does.
- <intervention_timestep> the model timestep (tick) at which the intervention should be triggered, must be an integer i.e., 200


# Footnotes
[^1]: ```@inproceedings{inproceedings,
author = {Gilbert, Nigel and Hawksworth, John and Swinney, Paul},
year = {2009},
month = {01},
pages = {30-35},
title = {An Agent-Based Model of the English Housing Market.}
}```







