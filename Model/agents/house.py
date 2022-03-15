# House agent skeleton code.
# from agents.realtor import Realtor
from mesa import Agent
import numpy as np
import random

"""The House object
Date edited: 08/02/2022
Author: Sedar Olmez
Email: solmez@turing.ac.uk

Parameters:
  my-owner            ; the owner who lives in this house
  local-realtors      ; the local realtors
  quality             ; index of quality of this house relative to its neighbours
  for-sale?           ; whether this house is currently for sale
  sale-price          ; the price of this house (either now, or when last sold)
  date-for-sale       ; when the house was put on the market
  my-realtor          ; if for sale, which realtor is selling it
  offered-to          ; which owner has already made an offer for this house
  offer-date          ; date of the offer (in ticks)
  end-of-life         ; time step when this house will be demolished
"""


class House(Agent):

    def __init__(self, house_id, model):
        super().__init__(house_id, model)
        self.house_id = house_id #Each House object has a unique ID.
        self.agent_type = "House"
        self.my_owner = None
        self.local_realtors = []
        self.quality = 0
        self.for_sale = False # == for_sale?
        self.sale_price = 0
        self.date_for_sale = None
        self.my_realtor = None
        self.offered_to = None
        self.offer_date = None
        self.end_of_life = None
        self.occupied = False

    def step(self):
        "IMPORTANT! The agents step goes here! What does it do?"


    def demolish(self, agents_list):
        """
        ;; delete the house, but make sure all references to it are dealt with
        ; if anyone lives here, make them homeless

        to demolish                           ;; house procedure

          if is-owner? my-owner [
            ask my-owner [
              set my-house nobody
              ; cancel mortgage
              set mortgage 0
              set repayment 0
              hide-turtle  ; owner is homeless
              ]
            ]
          ; if this house is on a realtor's record, remove the record
          ask realtors [ unfile-record myself ]
          ; turn the land the house was built on back to grass
          set pcolor 57
          ; record the demolition
          set nDemolished nDemolished + 1
          die
        end
        """
        if(self.get_owner() != None):
            owner = self.get_owner()
            owner.set_my_house(None)
            # cancel mortgage
            owner.set_mortgage(0)
            owner.set_repayment(0)

        #; if this house is on a realtor's record, remove the record
        for realtors in agents_list:
            if(realtors.agent_type == "Realtor"):
                if(self in realtors.get_realtor_houses()):
                    realtors.unfile_record(self)



    def get_house_ID(self):
        return self.house_id
    # Setter method, the local_realtors variable will be assigned the
    # list of realtors in which the house is located in.
    def set_local_realtors(self, realtors):
        self.local_realtors.append(realtors)

    def get_list_of_local_realtors(self):
        return self.local_realtors

    def set_offer_date(self, date):
        self.offer_date = date

    def get_offered_to(self):
        return self.offered_to

    def set_offered_to(self, owner):
        self.offered_to = owner
    #show that this house is for sale.
    def put_on_market(self, step):
        self.for_sale = True
        self.date_for_sale = step

    def is_house_for_sale(self):
        return self.for_sale

    def get_date_for_sale(self):
        return self.date_for_sale

    def set_end_of_life(self, end_of_life):
        self.end_of_life = end_of_life

    def set_for_sale(self, decision):
        self.for_sale = decision

    def get_end_of_life(self):
        return self.end_of_life

    def set_owner(self, owner):
        self.my_owner = owner

    def get_owner(self):
        return self.my_owner

    def set_sale_price(self, new_price):
        self.sale_price = new_price

    def get_sale_price(self):
        return self.sale_price

    def set_quality_index(self, quality_index):
        self.quality = quality_index

    def get_quality(self):
        return self.quality

    def get_for_sale(self):
        return self.for_sale

    def set_realtor_valuation(self, list_of_houses):
        valuations = {}
        #set my-realtor max-one-of local-realtors [ valuation myself ]
        for realtor in self.get_list_of_local_realtors():
            valuations[realtor] = realtor.valuation(self, list_of_houses)

        maximum_val = max(valuations.values())
        maximum_keys = [k for k, v in valuations.items() if v == maximum_val]

        self.my_realtor = random.choice(maximum_keys)

    def set_realtor(self):
        self.my_realtor = random.choice(self.get_list_of_local_realtors())

    def get_my_realtor(self):
        return self.my_realtor

    def price_diff(self, a_house):
        return abs()
