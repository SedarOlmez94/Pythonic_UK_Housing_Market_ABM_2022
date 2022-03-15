from mesa import Model
# from agents.house import House
from agents.realtor import Realtor
from agents.house import House
from agents.owner import Owner
from agents.records import Records
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
import pandas as pd
from math import sqrt
from math import sin
import random
from matplotlib import pyplot as plt
import sys


"""
  Starting variables/macroeconomic parameters/main model class
  Date edited: 09/03/22
  Author: Sedar Olmez
  Email: solmez@turing.ac.uk
  Description:
  This project is based on the original UK PwC Housing Market model developed by Prof. Nigel Gilbert.
  The original model was developed in Netlogo, and can be found at the following source:

      Gilbert, N, Hawksworth, J C, and Sweeney, P (2008) 'An Agent-based Model of the UK
      Housing Market'.  University of Surrey http://cress.soc.surrey.ac.uk/housingmarket/ukhm.html

  This updated version of the model was developed in python using the MESA agent-based modelling package
  enhancing the model through a wealth of sophisticated packages in python. Like the original, this model
  was developed for academic research purposes only and should only be used to that capacity.

  This class contains the main MESA model code, the scheduling, data preprocessiong
  and main model code is found in this class. The two main methods is the initialisation for the
  object which is equivelant to "setup" in netlogo and the "step" method.
"""

# Visualisation code -------------------------------------
def count_houses(model):
    counter = 0
    for houses in model.schedule.agents:
        if(houses.agent_type == "House"):
            counter += 1

    return counter

def count_people_seeking_home(model):
    counter = 0
    seeking_a_house = [i for i in model.schedule.agents if i.agent_type=="Owner" and (not i.get_my_house())]

    for owners in seeking_a_house:
        counter += 1

    return counter

def count_empty_houses(model):
    counter = 0

    empty_houses = [i for i in model.schedule.agents if i.agent_type=="House" and (i.get_owner() == None)]

    for houses in empty_houses:
        counter += 1
    return counter


def ve_equity(model):
    counter = 0
    houses = [i for i in model.schedule.agents if i.agent_type=="House" and ((i.get_owner() != None) and (i.get_sale_price() < i.get_owner().get_mortgage()))]

    for house in houses:
        counter += 1
    return counter

def demolished(model):
    return model.nDemolished

def people(model):
    n_people = [i for i in model.schedule.agents if i.agent_type=="Owner"]
    return len(n_people)

def up_shocked(model):
    return 10 * model.nUpShocked

def down_shocked(model):
    return 10 * model.nDownShocked

def median_house_prices_for_sale(model):
    """
    let houses-for-sale houses with [ for-sale?  and sale-price > 0 ]
    let houses-sold records

    ifelse any? houses-for-sale
    [set-current-plot-pen "For sale"
    plot medianPriceOfHousesForSale]
    [ plot 0 ]
    """
    houses_for_sale = [i for i in model.schedule.agents if i.agent_type=="House" and (i.is_house_for_sale() and i.get_sale_price() > 0)]

    if(len(houses_for_sale) > 0):
        return model.medianPriceOfHousesForSale
    else:
        return 0


def median_house_prices_for_sold(model):
    """
      set-current-plot-pen "Sold"
      let medianSellingPriceOfHouses 0
      if any? houses-sold [ set medianSellingPriceOfHouses median [ selling-price ] of houses-sold ]
        plot medianSellingPriceOfHouses
  """
    houses_sold = [i for i in model.schedule.agents if i.agent_type=="Record"]

    medianSellingPriceOfHouses = 0

    if(len(houses_sold) > 0):
        medianSellingPriceOfHouses = np.median([i.get_record_selling_price() for i in houses_sold])

    return medianSellingPriceOfHouses

def gini_index(list):
    sorted_list = sorted(list)
    total = sum(sorted_list)
    items = len(list)
    sum_so_far = 0
    index = 0
    gini = 0

    for i in range(items):
        sum_so_far = sum_so_far + sorted_list[index]
        index += 1
        gini = gini + (index / items) - (sum_so_far / total)

    #only accurate if items is large
    return 2 * (gini / items)

def gini_index_prices(model):
    houses_sold = [i for i in model.schedule.agents if i.agent_type=="Record"]
    if(len(houses_sold) > 0):
        return gini_index([i.get_record_selling_price() for i in houses_sold])


def gini_index_incomes(model):
    owner_incomes = [i.get_income() for i in model.schedule.agents if i.agent_type=="Owner"]
    if(len(owner_incomes) > 0):
        return gini_index(owner_incomes)


def mortgage_repayment_income(model):
    owners = [i for i in model.schedule.agents if i.agent_type=="Owner" and (i.get_repayment() > 0)]

    if(len(owners) > 0):
        repayment = [i.get_repayment() for i in owners]
        income = [i.get_income() for i in owners]
        return model.TicksPerYear * (np.mean(repayment) / np.mean(income))


def median_house_prices(model):
    owners = [i for i in model.schedule.agents if i.agent_type=="Owner"]
    houses_sold = [i for i in model.schedule.agents if i.agent_type=="Record"]

    if(len(houses_sold) > 0 and len(owners) > 0):
        income_of_owners = [i.get_income() for i in owners]
        return median_house_prices_for_sold(model) / np.median(income_of_owners)


def median_time_on_market(model):
    houses_for_sale = [i.get_date_for_sale() for i in model.schedule.agents if i.agent_type=="House" and (i.is_house_for_sale() == True and i.get_sale_price() > 0)]
    return model.current_step - np.median(houses_for_sale)


def transactions(model):
    return model.moves

def interest_rate(model):
    return model.interestPerTick * model.TicksPerYear * 100

def inflation_rate(model):
    return model.Inflation

# Visualisation code ------------------------------------- END

UK_estate_agents = ['Linley&Simpson', 'Hunters', 'Purplebricks']

description = ("Python version of the UK PwC housing market model originally developed by Nigel Gilbert")

class MesaModel(Model):


    def __init__(self, nRealtors,
                        width,
                        height,
                        initialVacancyRate,
                        InterestRate,
                        TicksPerYear,
                        maxHomelessPeriod,
                        min_price_fraction,
                        Inflation,
                        CycleStrength,
                        Affordability,
                        Savings,
                        ExitRate,
                        EntryRate,
                        MeanIncome,
                        Shocked,
                        BuyerSearchLength,
                        RealtorTerritory,
                        Locality,
                        RealtorMemory,
                        PriceDropRate,
                        RealtorOptimism,
                        InitialGeography,
                        Density,
                        HouseConstructionRate,
                        HouseMeanLifetime,
                        MaxLoanToValue,
                        MortgageDuration,
                        StampDuty,
                        scenario,
                        intervention_step):

        self.running = True
        self.nRealtors = nRealtors
        self.initialVacancyRate = initialVacancyRate
        self.InterestRate = InterestRate
        self.TicksPerYear = TicksPerYear
        self.maxHomelessPeriod = maxHomelessPeriod
        self.interestPerTick = self.InterestRate / (self.TicksPerYear * 100)
        self.min_price_fraction = min_price_fraction
        self.Inflation = Inflation
        self.CycleStrength = CycleStrength
        self.Affordability = Affordability
        self.Savings = Savings
        self.ExitRate = ExitRate
        self.EntryRate = EntryRate
        self.MeanIncome = MeanIncome
        self.Shocked = Shocked
        self.BuyerSearchLength = BuyerSearchLength
        self.RealtorTerritory = RealtorTerritory
        self.Locality = Locality
        self.RealtorMemory = RealtorMemory
        self.PriceDropRate = PriceDropRate
        self.RealtorOptimism = RealtorOptimism
        self.InitialGeography = InitialGeography
        self.Density = Density
        self.HouseConstructionRate = HouseConstructionRate
        self.HouseMeanLifetime = HouseMeanLifetime
        self.MaxLoanToValue = MaxLoanToValue
        self.MortgageDuration = MortgageDuration
        self.StampDuty = StampDuty
        # Instantiate a scheduler object
        self.schedule = RandomActivation(self)
        # Create a grid environment
        self.grid = MultiGrid(width, height, torus=True)
        self.total_number_of_agents = 0
        self.current_step = 0
        self.medianPriceOfHousesForSale = 0
        self.nUpShocked = 0
        self.nDownShocked = 0
        self.nDemolished = 0
        self.uniqueIDs = []
        self.moves = 0
        self.scenario = scenario
        self.intervention_step = intervention_step


        # Create and distribute realtor agents.
        for i in range(self.nRealtors):
            a = Realtor(i, np.random.choice(UK_estate_agents), self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            self.total_number_of_agents += 1
            self.uniqueIDs.append(self.total_number_of_agents)


        # Create and distribute houses.
        total_grid_size = self.grid.width * self.grid.height #count patches

        for i in range(int(total_grid_size * self.Density / 100)):
            self.total_number_of_agents = self.get_new_id()
            self.build_house(self.total_number_of_agents)


        #create the owners, one per house
        self.create_owners()


        #; value all empty houses according to average values of local occupied houses
        median_price = self.get_median_house_sale_price()


        """ask houses with [ sale-price = 0 ] [
             let local-houses houses with [distance myself < Locality and sale-price > 0]
             ifelse any? local-houses
               [ set sale-price  median [ sale-price ] of local-houses]
               [ set sale-price  median-price ]
             ]"""

        sale_price_zero_houses = [i for i in self.schedule.agents if i.agent_type == "House" and (i.get_sale_price() == 0)]
        all_other_houses = [i for i in self.schedule.agents if i.agent_type =="House" and (i.get_sale_price() > 0)]
        local_houses = []

        for houses in sale_price_zero_houses:
            for other_houses in all_other_houses:
                    if((int(self.calc_distance(houses.pos, other_houses.pos)) < self.Locality)):
                        local_houses.append(other_houses)


            if(len(local_houses) > 0):
                local_prices = []
                for house in local_houses:
                    local_prices.append(house.get_sale_price())
                houses.set_sale_price(np.median(local_prices))
            else:
                houses.set_sale_price(median_price)

        #set medianPriceOfHousesForSale median [sale-price] of houses
        self.medianPriceOfHousesForSale = self.get_median_house_sale_price()


        # calculate the quality index as a ratio of the house's price to the median price.
        self.calculate_quality_index()


        #; note the average price of a house in each realtor's territory
        self.set_average_house_prices_for_realtors()# HERE--------->


        # create some initial records of sales.
        self.create_records()


        # data to be visualised in the main_visualisation.py class.
        self.datacollector = DataCollector(
            model_reporters={"N Houses": count_houses, "Seeking a Home": count_people_seeking_home,
                            "Empty Houses": count_empty_houses, "In -ve equity":ve_equity,
                            "Demolished":demolished, "N Population":people,
                            "10 x Moving up":up_shocked, "10 x Moving down":down_shocked,
                            "(Median House Prices) For sale":median_house_prices_for_sale, "Sold":median_house_prices_for_sold,
                            "(gini) Prices":gini_index_prices, "Incomes":gini_index_incomes,
                            "Mortgage repayment / income":mortgage_repayment_income,
                            "Median house price / median income": median_house_prices,
                            "Median time on market":median_time_on_market,
                            "N Transactions":transactions, "Interest Rate":interest_rate,
                            "Inflation Rate":inflation_rate}
        )



    def step(self):
        "Advance model by one discrete step"
        self.datacollector.collect(self)
        self.schedule.step()

        n_owners = self.get_number_of_agents("Owner")

        """
        ; add an exogenous cyclical interest rate, if required: varies around mean of
        ; the rate set by slider with a fixed period of 10 years
        ; add an exogenous cyclical interest rate, if required: varies around mean of
          ; the rate set by slider with a fixed period of 10 years

          set interestPerTick InterestRate / ( TicksPerYear * 100 )
          if CycleStrength > 0 [
            set interestPerTick interestPerTick * (1 + (CycleStrength / 100 ) *
                                                    sin ( 36 * ticks / TicksPerYear ))
            ]
        """
        self.interestPerTick = self.InterestRate / (self.TicksPerYear * 100)

        if self.CycleStrength > 0:
            self.interestPerTick = self.interestPerTick * (1 + (self.CycleStrength / 100) *
                                                            sin(36 * self.current_step / self.TicksPerYear))


        """; add inflation to salary, at inflation rate / TicksPerYear
        if Inflation > 0 [
            ask owners [ set income income * (1 + Inflation / ( TicksPerYear * 100 )) ]
        ]
        """
        if self.Inflation > 0:
            for owners in self.schedule.agents:
                if owners.agent_type == "Owner":
                    owners.set_income(owners.get_income() * (1 + self.Inflation / (self.TicksPerYear * 100)))

        # let owner-occupiers owners with [ is-house? my-house ]
        owner_occupiers = self.update_owner_occupiers()

        # ; some have an income shock
        shocked_owners = random.sample(owner_occupiers, int(self.Shocked * len(owner_occupiers) / 100))

        #; either a shock of 20% more income than before
        upshocked_owners = random.sample(shocked_owners, int(len(shocked_owners) / 2))

        self.nUpShocked = 0

        for upshockedOwners in upshocked_owners:
            upshockedOwners.set_income(upshockedOwners.get_income() * 1.2)

        # ; or a shock of 20% less income than before
        downshocked = list(set(shocked_owners) - set(upshocked_owners))
        self.nDownShocked = 0

        for downShockedOwners in downshocked:
            downShockedOwners.set_income(downShockedOwners.get_income() * 0.8)

        for owner in owner_occupiers:
            if(owner.get_my_house().is_house_for_sale() == False):
                my_house = owner.get_my_house()
                """
                ; if they are now spending less than half the Affordability ratio of their
                ; income on their mortgage repayments, they want to move up
                """
                ratio = owner.get_repayment() * self.TicksPerYear / owner.get_income()
                if(ratio < self.Affordability / 200):
                    my_house.put_on_market(self.current_step)
                    self.nUpShocked = self.nUpShocked + 1
                """
                ; if they are now spending more than twice the Affordability ratio of
                ; their income on their mortgage repayments, they want to move down
                """
                if ratio > self.Affordability / 50:
                    my_house.put_on_market(self.current_step)
                    self.nDownShocked = self.nDownShocked + 1

        # ; some owners put their houses on the market and leave town

        owners_house_on_market = random.sample([i for i in self.schedule.agents if i.agent_type =="Owner" and (i.get_my_house() != None)], int(self.ExitRate * n_owners / 100))

        for owners in owners_house_on_market:
            my_house = owners.get_my_house()
            my_house.put_on_market(self.current_step)
            my_house.set_owner(None)
            self.uniqueIDs.remove(owners.get_owner_id())
            self.kill_agents(owners)


        # Some new owners arrive!
        self.make_owners(int(self.EntryRate * n_owners / 100), self.current_step)


        """
        ; note that those without houses are homeless for another period, and remove those who
        ; have given up waiting for a house

        if MaxHomelessPeriod  > 0 [ ; after this number of periods, the homeless emigrate
        ask owners with [ not is-house? my-house ] [
             set homeless homeless + 1
             if homeless > maxHomelessPeriod [ die ]
             ]
          ]
        """
        if(self.maxHomelessPeriod > 0):
             #; after this number of periods, the homeless emigrate
             for agents in self.schedule.agents:
                 if(agents.agent_type == "Owner"):
                     if(not agents.get_my_house()):
                        agents.set_homeless(agents.get_homeless() + 1)
                        if(agents.get_homeless() > self.maxHomelessPeriod):
                            self.uniqueIDs.remove(agents.get_owner_id())
                            self.kill_agents_not_on_grid(agents)


        """
        ; those who are paying mortgages greater than their income, are forced to move out
        ; of the housing market and their house is put up for sale
        """

        for ownerOccupiers in owner_occupiers:
            if((ownerOccupiers.get_my_house().is_house_for_sale() == True) and
                ((ownerOccupiers.get_repayment() * self.TicksPerYear) > ownerOccupiers.get_income()) and (ownerOccupiers.get_owner_id() in self.uniqueIDs)):
                ownerOccupiers.get_my_house().set_owner(None)
                self.uniqueIDs.remove(ownerOccupiers.get_owner_id())
                self.kill_agents(ownerOccupiers)


        #; some new houses are built, and put up for sale
        num_houses = self.get_number_of_agents("House")
        for i in range(int(num_houses * self.HouseConstructionRate / 100)):
            """
            ; ensure that there are vacant patches before building a house
            ; if there are not, no more houses are built
            """
            if(self.grid.exists_empty_cells()):
                self.build_house(self.get_new_id())


        for houses in self.schedule.agents:
            if(houses.agent_type == "House"):
                if(houses.get_quality() == 0):
                    """
                    ; these are the new houses
                    ; calculate quality index as the mean of the qualities of those in the locality
                    ; or set to 1 if there aren't any houses around here
                    """
                    # num for num in inputList if num != 0
                    houses_around_here = [i for i in self.grid.get_neighbors(pos=houses.pos, moore=True, radius=self.Locality) if i.agent_type == "House"]
                    quality_index_of_houses_here = []
                    for house in houses_around_here:
                        quality_index_of_houses_here.append(house.get_quality())

                    if(len(houses_around_here) > 0):
                        houses.set_quality_index(np.mean(quality_index_of_houses_here))
                    else:
                        houses.set_quality_index(1)

                    if(houses.get_quality() > 3):
                        houses.set_quality_index(3)

                    if(houses.get_quality() < 0.3):
                        houses.set_quality_index(0.3)

        """
        ; for houses that are newly for sale, get the sale price, which is the highest
        ; valuation offered by local realtors. (Houses that remain for sale,
        ; not having been sold in the previous round, already have a sale price)

        let houses-for-sale houses with [ for-sale? ]
          if any? houses-for-sale [
            ask houses-for-sale with [ date-for-sale = ticks ] [

              set my-realtor max-one-of local-realtors [ valuation myself ]
              set sale-price [ valuation myself ] of my-realtor

              ]

            ; update the average selling price of houses in each realtor's territory
            ask realtors [
              let my-houses-for-sale houses-for-sale with [ member? myself local-realtors ]
              if any? my-houses-for-sale [ set average-price median [ sale-price ] of my-houses-for-sale ]
              ]

            set medianPriceOfHousesForSale median [sale-price] of houses-for-sale
            ]
        """
        houses_for_sale = [i for i in self.schedule.agents if i.agent_type=="House" and i.is_house_for_sale()]
        list_of_houses = [i for i in self.schedule.agents if i.agent_type=="House"]

        if(len(houses_for_sale) > 0):
            for houses in houses_for_sale:
                if(houses.get_date_for_sale() == self.current_step):
                    houses.set_realtor_valuation(list_of_houses)
                    houses.set_sale_price(houses.get_my_realtor().valuation(houses, list_of_houses))

            #; update the average selling price of houses in each realtor's territory
            _realtors = [i for i in self.schedule.agents if i.agent_type == "Realtor"]
            for realtors in _realtors:
                my_houses_for_sale = [i for i in houses_for_sale if realtors in i.get_list_of_local_realtors()]
                if(len(my_houses_for_sale) > 0):
                    realtors.set_realtor_average_price(my_houses_for_sale)

            self.medianPriceOfHousesForSale = self.get_median_house_sale_price_list(houses_for_sale)


        #  ; buyers (new entrants and those wishing to sell) search for a suitable property to buy
        buyers = [i for i in self.schedule.agents if i.agent_type == "Owner" and (i.get_my_house() == None or i.get_my_house().is_house_for_sale())]

        #;; those with nothing to sell get priority in making an offer; i.e. they go first
        for agents in self.schedule.agents:
            if(agents.agent_type == "Owner"):
                if(agents.get_my_house() == None):
                    agents.make_offer(houses_for_sale, self.current_step)


        #; and now those who do have a house to sell get a chance to make an offer
        for agents in self.schedule.agents:
            if(agents.agent_type == "Owner"):
                if(agents.get_my_house() != None and agents.get_my_house().is_house_for_sale()):
                    agents.make_offer(houses_for_sale, self.current_step)

        """
         ; Check which chains will complete.  A chain of buyers and sellers will complete only
         ;  if the first buyer has nothing to sell, and the last seller has nothing to buy
         ; This means that the first buyer must be a new entrant, and the last house must
         ;  be vacant
        """
        self.moves = 0
        for buyer in buyers:
            if(buyer.get_my_house() == None and buyer.get_made_offer() != None):

                if(buyer.follow_chain()):
                    #; this buyer is the start of a successful chain
                    #; call in the removal firm!
                    buyer.move_house(self, self.current_step, self.get_new_id())


        #; realtors forget any sale records that are too old
        outdated_records_stored = [i for i in self.schedule.agents if i.agent_type =="Record" and (int(i.get_record_date()) < int(self.current_step - self.RealtorMemory))]

        for outdated_records in outdated_records_stored:
            self.uniqueIDs.remove(outdated_records.get_record_ID())
            self.kill_agents_not_on_grid(outdated_records)


        #; remove references to outdated records
        for realtor in self.schedule.agents:
            if(realtor.agent_type == "Realtor"):
                for records in realtor.get_realtor_sales():
                    if(records in outdated_records_stored):
                        realtor.remove_sales_from_list(records)


        # ; cancel any outstanding offer
        for houses in self.schedule.agents:
            if(houses.agent_type == "House"):
                if(houses.get_offered_to() != None):
                    houses.get_offered_to().set_made_offer_on(None)
                    houses.set_offered_to(None)
                    houses.set_offer_date(0)

        """
        ; demolish any house that is either at the end of its life or that is no longer
        ;  worth much
        """
        self.nDemolished = 0

        n_records = self.get_number_of_agents("Record")


        if(n_records > 0):
            minimum_price = self.min_price_fraction * self.medianPriceOfHousesForSale
            for houses in self.schedule.agents:
                if(houses.agent_type == "House" and ((self.current_step > houses.get_end_of_life()) or
                                (houses.get_for_sale() and houses.get_sale_price() < minimum_price))):
                                houses.demolish(self.schedule.agents)
                                #; record the demolition
                                self.nDemolished += 1
                                self.uniqueIDs.remove(houses.get_house_ID())
                                self.kill_agents(houses)


        #; any house that is still for sale has its price reduced
        for houses in self.schedule.agents:
            if (houses.agent_type == "House" and (houses.get_for_sale())):
                houses.set_sale_price(houses.get_sale_price() * (1 - self.PriceDropRate / 100))

        """
        ; owners that have a mortgage have to pay interest and some capital
        ; the mortgage is reduced by the amount of capital repayment
        """
        for owners in self.schedule.agents:
            if(owners.agent_type == "Owner" and (owners.get_my_house() != None and owners.get_mortgage() > 0)):
                owners.set_mortgage(owners.get_mortgage() - (owners.get_repayment() - self.interestPerTick * owners.get_mortgage()))
                #; check if mortgage has now been fully repaid; if so cancel it
                if (owners.get_mortgage() <= 0):
                    owners.set_mortgage(0)
                    owners.set_repayment(0)



        # Keep track of the current scheduler step. current_step = ticks
        self.current_step += 1


        # Shocks to the market at a specific timestep.
        if(self.current_step == int(self.intervention_step)):
            if(self.scenario == "ratefall"):
                print("ratefall!!!")
                self.InterestRate = 10.0
            elif(self.scenario == "ltv"):
                self.MaxLoanToValue = 60
            elif(self.scenario == "influx"):
                self.EntryRate = 10
            elif(self.scenario == "poorentrants"):
                self.MeanIncome = 24000
            elif(self.scenario == "none"):
                print()

        # Stop if no owners or houses left!
        if(self.get_number_of_agents("Owner") <= 0):
            print("Finished: no remaining people!")
            sys.exit()

        if(self.get_number_of_agents("House") <= 0):
            print("Finished: no remaining houses!")
            sys.exit()


    def update_owner_occupiers(self):
        # let owner-occupiers owners with [ is-house? my-house ]
        owner_occupiers = []
        for agents in self.schedule.agents:
            if agents.agent_type == "Owner":
                if(agents.get_my_house() != None):
                    owner_occupiers.append(agents)

        return owner_occupiers


    def get_new_id(self):
        list_of_ids = sorted(self.uniqueIDs)
        self.uniqueIDs.append(max(list_of_ids) + 1)
        return max(list_of_ids) + 1


    def make_owners(self, n, timestep):

        for i in range(n):
            new_owner = Owner(self.total_number_of_agents, None, self)
            self.schedule.add(new_owner)
            #self.grid.place_agent(new_owner, house.pos)
            # new owners are not located anywhere yet.
            new_owner.assign_income(timestep)
            self.total_number_of_agents = self.get_new_id()


    def kill_agents(self, agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)


    def kill_agents_not_on_grid(self, agent):
        self.schedule.remove(agent)


    def create_records(self):
        """
        ; insert fake selling records in the histories of the realtors, so that they have
        ; something to base their step 0 valuations on, and specify an average level of
        ; buyer interest

        ask houses [
             ; insert fake selling records in the histories of the realtors, so that they have
             ; something to base their step 0 valuations on, and specify an average level of
             ; buyer interest
             let the-record nobody
             hatch-records 1 [
               hide-turtle
               set the-house myself
               set selling-price [ sale-price ] of myself
               set the-record self
               ]
             set my-realtor one-of local-realtors
             ask my-realtor [ file-record the-record ]
             ]
        """
        for houses in self.schedule.agents:
            if(houses.agent_type == "House"):
                r = Records(self.total_number_of_agents, houses, houses.get_sale_price(), self.current_step, self)
                self.schedule.add(r)

                houses.set_realtor()
                my_realtor = houses.get_my_realtor()
                my_realtor.file_record(r)
                self.total_number_of_agents = self.get_new_id()


    def get_number_of_agents(self, agentType):
        x = 0
        for agents in self.schedule.agents:
            if agents.agent_type == agentType:
                x += 1

        return x


    def set_average_house_prices_for_realtors(self):
        houses_list = []

        for houses in self.schedule.agents:
            if (houses.agent_type == "House"):
                houses_list.append(houses)

        for realtors in self.schedule.agents:
            if (realtors.agent_type == "Realtor"):
                realtors.set_realtor_average_price(houses_list)


    """
    ask houses [
      ; calculate quality index as ratio of this house's price to the median house price
      set quality sale-price / medianPriceOfHousesForSale
      if quality > 3 [set quality 3] if quality < 0.3 [set quality 0.3]
      ]
      """
    def calculate_quality_index(self):
        for houses in self.schedule.agents:
            if (houses.agent_type == "House"):
                houses.set_quality_index(houses.get_sale_price() / self.medianPriceOfHousesForSale)
                if(houses.get_quality() > 3):
                    houses.set_quality_index(3)
                if(houses.get_quality() < 0.3):
                    houses.set_quality_index(0.3)


    def create_owners(self):
        #create the owners, one per house
        # let occupied-houses n-of ((1 - initialVacancyRate) * count houses) houses
        occupied_houses = []
        number_of_houses = 0
        houses_list = []
        counter = 0

        for agent in self.schedule.agents:
            if(agent.agent_type == "House"):
                number_of_houses += 1
                houses_list.append(agent)

        number_of_houses = int((1 - self.initialVacancyRate) * number_of_houses)

        occupied_houses = random.sample(houses_list, number_of_houses)

        self.total_number_of_agents = self.get_new_id()
        for house in occupied_houses:
            house.set_for_sale(False)

            new_owner = Owner(self.total_number_of_agents, house, self)
            # Add the object to the scheduler
            self.schedule.add(new_owner)
            self.grid.place_agent(new_owner, house.pos)
            house.set_owner(new_owner)

            # assign-income
            new_owner.assign_income(self.current_step)



            #if InitialGeography = "Gradient" [ set income income * ( xcor + ycor + 50) / 50 ]
            if self.InitialGeography == "Gradient":
                new_owner.set_income(new_owner.get_income() * (new_owner.pos.x + new_owner.pos.y + 50) / 50)

            # set mortgage to a multiple of my income.
            new_owner.set_mortgage(new_owner.get_income() * self.Affordability / (self.interestPerTick * self.TicksPerYear * 100))


            #; calculate value of the deposit for this house
            deposit = new_owner.get_mortgage() * (100 / self.MaxLoanToValue - 1)

            #; set value of house to the mortgage + deposit
            owners_house = new_owner.get_my_house()
            owners_house.set_sale_price(new_owner.get_mortgage() + deposit)

            # set the repayment value
            new_owner.set_repayment(new_owner.get_mortgage() * self.interestPerTick /
                                        (1 - (1 + self.interestPerTick) ** (- self.MortgageDuration * self.TicksPerYear)))

            self.total_number_of_agents = self.get_new_id()




    def build_house(self, id): #observer procedure
        #;; add a single house to the town, in a random location

        # Create a house object.
        a = House(id, self)
        # Add the object to the scheduler
        self.schedule.add(a)
        # Place the agent on an empty cell within the grid.
        self.grid.place_agent(a, self.grid.find_empty())


        # get the neighbouring cells in all 8 cardinal directions from origin up to < RealtorTerritory radius
        neighbourhood_cells = self.grid.get_neighbors(a.pos, moore=True, radius=self.RealtorTerritory-1)
        #Get all realtor agents within the RealtorTerritory distance and add them to the houses local_realtors list
        for agent in neighbourhood_cells:
            if(agent.agent_type == "Realtor"):
                a.set_local_realtors(agent)

        # If there are some houses which do not fall within the realtors territory...
        if(len(a.get_list_of_local_realtors()) == 0):
            realtors_distance = {}
            # We add the realtor, euclidean distance key, value pair to a dictionary
            # and select the smallest distance realtor to the house and add this to the local_realtor list.
            for agent in self.schedule.agents:
                if(agent.agent_type == "Realtor"):
                    realtors_distance[agent] = int(self.calc_distance(a.pos, agent.pos))

            a.set_local_realtors(min(realtors_distance, key=realtors_distance.get))

        """
        ; initially empty houses are for sale
        ; note how long this house will last before it falls down and is demolished
        """
        a.put_on_market(self.current_step)

        """
        ; note how long this house will last before it falls down and is demolished
        set end-of-life ticks + int random-exponential ( HouseMeanLifetime * TicksPerYear )
        """

        a.set_end_of_life(self.current_step + int(np.random.exponential(self.HouseMeanLifetime * self.TicksPerYear)))



    def get_visualisation_of_owner_income(self):
        incomes = []
        for agents in self.schedule.agents:
            if(agents.agent_type == "Owner"):
                incomes.append(agents.get_income())

        plt.hist(incomes)
        plt.show()


    def get_visualisation_of_owner_capital(self):
        capital = []
        for agents in self.schedule.agents:
            if(agents.agent_type == "Owner"):
                capital.append(agents.get_capital())

        plt.hist(capital)
        plt.show()

    def get_distribution_of_house_prices_all(self):
        all_houses = [i.get_sale_price() for i in self.schedule.agents if i.agent_type=="House"]

        plt.hist(all_houses)
        plt.show()

    def get_distribution_of_house_prices_for_sale(self):
        all_houses = [i.get_sale_price() for i in self.schedule.agents if i.agent_type=="House" and (i.get_for_sale() == True)]

        plt.hist(all_houses)
        plt.show()


    def get_median_house_sale_price(self):
        list_of_house_prices = []
        for houses in self.schedule.agents:
            if(houses.agent_type == "House"):
                if(houses.get_sale_price() > 0):
                    list_of_house_prices.append(houses.get_sale_price())

        return np.median(list_of_house_prices)


    def get_median_house_sale_price_list(self, houses):
        list_of_house_prices = []
        for houses in houses:
            list_of_house_prices.append(houses.get_sale_price())

        return np.median(list_of_house_prices)



    def debug(self, agent_type):
        # DEBUGGING.
        for agent in self.schedule.agents:
            if(agent.agent_type == agent_type):
                print(agent.get_records())


    # euclidean distance.
    def calc_distance(self, p1, p2):
        return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)
