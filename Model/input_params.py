"""
    Date edited: 09/03/22
    Author: Sedar Olmez
    Email: solmez@turing.ac.uk
    Description:
    Input parameters to the model, these can be changed according to the experiments conducted.
"""
class InputParameters():

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
        self.scenario = "none"
