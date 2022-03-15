from environment.mesa_model import MesaModel
import matplotlib.pyplot as plt
from input_params import InputParameters


"""
Date edited: 09/03/22
Author: Sedar Olmez
Email: solmez@turing.ac.uk
Description:
    This class was used for debugging, you can run the model via steps to test
    the model behaviour.
"""


#-----------------------------------------MAIN--------------------------------------------------------
# Size of GRID environment.
GRID_SIZE_X = 61 # Original size of model. 121
GRID_SIZE_Y = 61

# Import the InputParameters template object containing macroeconomic global parameters.
input_par = InputParameters()

# Create the model object with parameters from the InputParameters object.
model = MesaModel(input_par.nRealtors,
                    GRID_SIZE_X,
                    GRID_SIZE_Y,
                    input_par.initialVacancyRate,
                    input_par.InterestRate,
                    input_par.TicksPerYear,
                    input_par.maxHomelessPeriod,
                    input_par.min_price_fraction,
                    input_par.Inflation,
                    input_par.CycleStrength,
                    input_par.Affordability,
                    input_par.Savings,
                    input_par.ExitRate,
                    input_par.EntryRate,
                    input_par.MeanIncome,
                    input_par.Shocked,
                    input_par.BuyerSearchLength,
                    input_par.RealtorTerritory,
                    input_par.Locality,
                    input_par.RealtorMemory,
                    input_par.PriceDropRate,
                    input_par.RealtorOptimism,
                    input_par.InitialGeography,
                    input_par.Density,
                    input_par.HouseConstructionRate,
                    input_par.HouseMeanLifetime,
                    input_par.MaxLoanToValue,
                    input_par.MortgageDuration,
                    input_par.StampDuty,
                    input_par.scenario)


# Do one step of the model.
for i in range(60):
    model.step()






# get_distribution_of_earnings_plot(100, 1)
