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
    """
    A class representing a record of a house sale in a housing simulation.

    Parameters:
    record_id (int): Unique identifier for the record.
    the_house: The house associated with the record.
    selling_price (float): Selling price of the house in the record.
    date: Date when the sale occurred.
    model: The simulation model this record is part of.

    Attributes:
    record_id (int): Unique identifier for the record.
    agent_type (str): Type of agent, set to "Record".
    the_house: The house associated with the record.
    selling_price (float): Selling price of the house in the record.
    date: Date when the sale occurred.

    Methods:
    get_record_ID():
        Get the unique identifier of the record.

    get_record_house():
        Get the house associated with the record.

    get_record_selling_price():
        Get the selling price of the house in the record.

    get_record_date():
        Get the date when the sale occurred.
    """

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
