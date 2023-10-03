# Person agent skeleton code.
from mesa import Agent
import numpy as np
from math import sqrt

# np.random.seed(0)

"""The Realtor object
Date edited: 08/02/2022
Author: Sedar Olmez
Email: solmez@turing.ac.uk

Parameters:
    company - the organisation that owns this realtor.
    my_houses - the houses in this realtor's terroritory.
    sales - the last few house sales that was made by this realtor.
    average_price - the average price of a house in the realtor's territory.
"""


class Realtor(Agent):
    """
    A class representing a realtor agent in a housing simulation.

    Parameters:
    realtor_id (int): Unique identifier for the realtor.
    company: The real estate company the realtor is associated with.
    model: The simulation model this realtor is part of.

    Attributes:
    realtor_id (int): Unique identifier for the realtor.
    agent_type (str): Type of agent, set to "Realtor".
    company: The real estate company the realtor is associated with.
    my_houses (list): List of houses associated with the realtor.
    sales (list): List of sales records made by the realtor.
    average_price (float): Average sale price of the realtor's houses.

    Methods:
    step():
        Perform a step in the simulation for the realtor agent.

    get_realtor_id():
        Get the unique identifier of the realtor.

    get_realtor_company():
        Get the real estate company associated with the realtor.

    get_realtor_houses():
        Get the list of houses associated with the realtor.

    get_realtor_sales():
        Get the list of sales records made by the realtor.

    remove_sales_from_list(sale):
        Remove a sale record from the realtor's sales list.

    get_realtor_average_price():
        Get the average sale price of the realtor's houses.

    set_realtor_average_price(houses):
        Set the average sale price of the realtor's houses.

    file_record(record):
        Add a sales record to the realtor's sales list.

    unfile_record(house):
        Remove sales records associated with a specific house.

    get_records():
        Get the list of sales records made by the realtor.

    move():
        Move the realtor to a new position.

    valuation(property, houses):
        Calculate the valuation of a property based on local sales records.

    stamp_duty_land_tax(cost):
        Calculate stamp duty land tax based on the cost of a property.

    calc_distance(p1, p2):
        Calculate the Euclidean distance between two points.
    """

    def __init__(self, realtor_id, company, model):
        super().__init__(realtor_id, model)

        self.realtor_id = realtor_id
        self.agent_type = "Realtor"
        self.company = company
        self.my_houses = []
        self.sales = []
        self.average_price = 0

    def step(self):
        "IMPORTANT! The realtor agents step goes here! What does it do?"

    def get_realtor_id(self):
        return self.realtor_id

    def get_realtor_company(self):
        return self.company

    def get_realtor_houses(self):
        return self.my_houses

    def get_realtor_sales(self):
        return self.sales

    def remove_sales_from_list(self, sale):
        self.sales.remove(sale)

    def get_realtor_average_price(self):
        return self.average_price

    def set_realtor_average_price(self, houses):
        sale_prices_of_my_houses = []

        for house in houses:
            if self in house.get_list_of_local_realtors():
                self.my_houses.append(house)

        for houses in self.my_houses:
            sale_prices_of_my_houses.append(houses.get_sale_price())

        self.average_price = np.median(sale_prices_of_my_houses)

    # to file-record [ the-record ]         ;; realtor procedure
    #   ; push this sales record onto the list of those I keep
    #   set sales fput the-record sales
    # end
    def file_record(self, record):
        self.sales.append(record)

    # ; delete any record that mentions the house
    def unfile_record(self, house):
        for records_ in self.get_records():
            if records_.get_record_house() == house:
                self.sales.remove(records_)

    def get_records(self):
        return self.sales

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def valuation(self, property, houses):
        """
        ;; A realtor values a property by looking in its records for sales
        ;; that it has made of houses in the locality to use as a guide to the
        ;; value of this property.
        ;; The value of the property is then:
        ;;   the median of the selling prices of these local houses,
        ;;   multiplied by this house's quality index
        ;;   multiplied by an optimism factor
        ;;   multiplied by a normalisation factor.
        ;; If the realtor has no sales in the locality, it bases the price on the
        ;;  median price of all the sale prices of local houses, or if there are
        ;;  none of those either, on the avergae price of all houses in the
        ;;  realtor's territory.
        """
        multiplier = property.get_quality() * (1 + self.model.RealtorOptimism / 100) * 1
        local_sales = []

        for records in self.get_records():
            if records.get_record_house().pos != None and (
                int(self.calc_distance(property.pos, records.get_record_house().pos))
                < self.model.Locality
            ):
                local_sales.append(records)

        old_price = property.get_sale_price()

        new_price = 0

        if len(local_sales) > 0:
            sale_prices = []
            for sales in local_sales:
                sale_prices.append(sales.get_record_selling_price())

            new_price = np.median(sale_prices)
        else:
            local_houses = [
                i
                for i in houses
                if self.calc_distance(i.pos, self.pos) <= self.model.Locality
            ]
            sale_prices_n = []
            for local_h in local_houses:
                sale_prices_n.append(local_h.get_sale_price())

            if len(local_houses) > 0:
                new_price = np.median(sale_prices_n)
            else:
                new_price = self.get_realtor_average_price()

        # ; if this is a new valuation, return it
        if old_price < 5000:
            return multiplier * new_price
        # otherwise prevent wild changes in price
        ratio = new_price / old_price
        threshold = 2

        if ratio > threshold:
            new_price = threshold * old_price
        else:
            if ratio < 1 / threshold:
                new_price = old_price / threshold

        return multiplier * new_price

    def stamp_duty_land_tax(self, cost):
        if self.model.StampDuty:
            if cost > 500000:
                return 0.04 * cost
            if cost > 250000:
                return 0.02 * cost
            if cost > 150000:
                return 0.01 * cost
        return 0

    def calc_distance(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
