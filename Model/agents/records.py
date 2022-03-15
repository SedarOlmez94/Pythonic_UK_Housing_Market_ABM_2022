from input_params import InputParameters
from mesa import Agent


"""The Record object
Date edited: 08/02/2022
Author: Sedar Olmez
Email: solmez@turing.ac.uk

Parameters:
    the_house - the house that was sold.
    selling_price - the selling price of the house.
    date - the date in which the transaction was made (step).
"""

class Records(Agent):
    def __init__(self, record_id, the_house, selling_price, date, model):
        super().__init__(record_id, model)
        self.record_id = record_id
        self.agent_type = "Record"
        self.the_house = the_house
        self.selling_price = selling_price
        self.date = date


    def get_record_ID(self):
        return self.record_id

    def get_record_house(self):
        return self.the_house

    def get_record_selling_price(self):
        return self.selling_price

    def get_record_date(self):
        return self.date
