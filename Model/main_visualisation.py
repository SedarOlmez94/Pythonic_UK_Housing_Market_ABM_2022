from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import (
    CanvasGrid,
    ChartModule,
    BarChartModule,
    PieChartModule,
)
from environment.mesa_model import *
from input_params import InputParameters
from mesa.visualization.ModularVisualization import VisualizationElement
import numpy as np
import sys
import getopt

"""
Date edited: 09/03/22
Author: Sedar Olmez
Email: solmez@turing.ac.uk
Description:
    This class contains the main front-end visualisation for the MESA ModularVisualization server.
    running this class using 'python main_visualisation.py' in terminal should launch your
    default web-browser and allow you to observe the model run visually including the graphs.
"""

# Set the size of the grid by x, y axes.
GRID_SIZE_X = int(sys.argv[1])
GRID_SIZE_Y = int(sys.argv[2])

#Create a visual depiction of an agent type in the environment grid.
# r: radius size if 1 then matches the size of the grid cell.
# Layer: the layer on which the agent is on, if two agents.layer = 0 then
# these agents will overlap one another.
# Don't touch agent_portrayal!
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 1}

    if agent.agent_type == "Realtor":
            portrayal["Color"] = "red"
            portrayal["Layer"] = 2
            portrayal["Shape"] = "circle"
            portrayal["r"] = 0.6

    if agent.agent_type == "House":
            portrayal["Color"] = "black"
            portrayal["Layer"] = 0
            portrayal["Shape"] = "circle"
            portrayal["r"] = 1

            # The colour of the house changes depending on price, the more expensive
            # an house is, the darker it is and vice-versa.
            if (agent.get_sale_price() < 1000000 and agent.get_sale_price() > 500000):
                portrayal["Color"] = "#21618C"
            elif(agent.get_sale_price() < 500000 and agent.get_sale_price() > 200000):
                portrayal["Color"] = "#2874A6"
            elif(agent.get_sale_price() < 200000 and agent.get_sale_price() > 100000):
                portrayal["Color"] = "#2E86C1"
            elif(agent.get_sale_price() < 100000 and agent.get_sale_price() > 80000):
                portrayal["Color"] = "#3498DB"
            elif(agent.get_sale_price() < 80000 and agent.get_sale_price() > 60000):
                portrayal["Color"] = "#5DADE2"
            elif(agent.get_sale_price() < 60000 and agent.get_sale_price() > 40000):
                portrayal["Color"] = "#85C1E9"
            elif(agent.get_sale_price() < 40000 and agent.get_sale_price() > 0):
                portrayal["Color"] = "#AED6F1"

    if agent.agent_type == "Owner":
            portrayal['Shape'] = "circle"
            portrayal['r'] = 0.2
            portrayal["Color"] = "yellow"
            portrayal["Layer"] = 1


    return portrayal


input_parameters = InputParameters()


#We create the environment GRID system (width, height, pixelsx, pixelsy)
grid = CanvasGrid(agent_portrayal, GRID_SIZE_X, GRID_SIZE_Y, 500, 500)


# Visualisations-------------------------------------------------
chart_houses = ChartModule([{"Label": "N Houses",
                      "Color": "Blue"}, {"Label": "Seeking a Home", "Color":"Red"},
                      {"Label": "Empty Houses", "Color":"Green"},
                      {"Label": "In -ve equity", "Color":"Black"},
                      {"Label": "Demolished", "Color":"Purple"}],
                    data_collector_name='datacollector')

people_charts = ChartModule([{"Label": "N Population", "Color":"Red"},
                            {"Label":"10 x Moving up","Color":"Blue"},
                            {"Label":"10 x Moving down", "Color":"Black"}])

median_house_prices = ChartModule([{"Label": "(Median House Prices) For sale", "Color":"Red"},
                                    {"Label": "Sold","Color":"Blue"}
])

gini_index = ChartModule([{"Label": "(gini) Prices", "Color":"Red"},
                            {"Label":"Incomes", "Color":"Blue"}
])

mortgage_repayment = ChartModule([{"Label":"Mortgage repayment / income", "Color":"Red"}])

median_house_price = ChartModule([{"Label":"Median house price / median income", "Color":"Red"}])

median_time_on_market = ChartModule([{"Label":"Median time on market", "Color":"Red"}])

transactions = ChartModule([{"Label":"N Transactions", "Color":"Red"}])

rates = ChartModule([{"Label":"Interest Rate", "Color":"Red"},
                    {"Label":"Inflation Rate", "Color":"Blue"}])

# Visualisations-------------------------------------------------END

#histogram = HistogramModule(list(range(1000000)), 200, 500)

#[grid, chart_houses, people_charts, median_house_prices, gini_index, mortgage_repayment, median_house_price, median_time_on_market, transactions, rates]

# We create the ModularServer object which populates the web-browser that launches with the model and graphs.
server = ModularServer(MesaModel, [grid, chart_houses, people_charts, median_house_prices, gini_index, mortgage_repayment, median_house_price, median_time_on_market, transactions, rates], "Housing Market",
                        {"nRealtors":input_parameters.nRealtors, "width":GRID_SIZE_X,
                        "height":GRID_SIZE_Y,
                         "initialVacancyRate":input_parameters.initialVacancyRate,
                         "InterestRate":input_parameters.InterestRate,
                         "TicksPerYear":input_parameters.TicksPerYear,
                         "maxHomelessPeriod":input_parameters.maxHomelessPeriod,
                         "min_price_fraction":input_parameters.min_price_fraction,
                         "Inflation":input_parameters.Inflation,
                         "CycleStrength":input_parameters.CycleStrength,
                         "Affordability":input_parameters.Affordability,
                         "Savings":input_parameters.Savings,
                         "ExitRate":input_parameters.ExitRate,
                         "EntryRate":input_parameters.EntryRate,
                         "MeanIncome":input_parameters.MeanIncome,
                         "Shocked":input_parameters.Shocked,
                         "BuyerSearchLength":input_parameters.BuyerSearchLength,
                         "RealtorTerritory":input_parameters.RealtorTerritory,
                         "Locality":input_parameters.Locality,
                         "RealtorMemory":input_parameters.RealtorMemory,
                         "PriceDropRate":input_parameters.PriceDropRate,
                         "RealtorOptimism":input_parameters.RealtorOptimism,
                         "InitialGeography":input_parameters.InitialGeography,
                         "Density":input_parameters.Density,
                         "HouseConstructionRate":input_parameters.HouseConstructionRate,
                         "HouseMeanLifetime":input_parameters.HouseMeanLifetime,
                         "MaxLoanToValue":input_parameters.MaxLoanToValue,
                         "MortgageDuration":input_parameters.MortgageDuration,
                         "StampDuty":input_parameters.StampDuty,
                         "scenario":sys.argv[3],
                         "intervention_step":sys.argv[4]})


server.port = 8524


server.launch()
