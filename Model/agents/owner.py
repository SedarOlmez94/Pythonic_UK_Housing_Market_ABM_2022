from mesa import Agent
# from input_params import InputParameters
from agents.records import Records
import numpy as np
import random
from operator import attrgetter

"""The Owner object
Date edited: 08/02/2022
Author: Sedar Olmez
Email: solmez@turing.ac.uk

Parameters:
    my_house - the house which this owner owns.
    income - this owner's current income.
    mortgage - value of mortgage: decreases as it is paid off.
    capital - capital accumulated by this owner for selling their house.
    repayment - owner's mortgage repayment amount, at each tick.
    date_of_purchase - when the owner's house was bought.
    made_offer_on - the house this owner wants to buy.
    homeless - count of the number of periods that this owner has been without a house.
"""

class Owner(Agent):

    def __init__(self, owner_id, my_house, model):
        super().__init__(owner_id, model)
        self.owner_id = owner_id
        self.my_house = my_house
        self.agent_type = "Owner"
        self.income = 0
        self.mortgage = 0
        self.repayment = 0
        self.capital = 0
        self.date_of_purchase = None
        self.made_offer_on = None
        self.homeless = 0
        # self.global_parameters = InputParameters()

    def step(self):
        "Step function for the owner agent, what does it do when it is activated?"

    def assign_income(self, current_timestep):
        ALPHA = 1.3 #shape parameter
        LAMBDA = 1 / 20000 #scale parameter
        MEANINCOME = self.model.MeanIncome
        INFLATION = self.model.Inflation
        TICKSPERYEAR = self.model.TicksPerYear
        SAVINGS = self.model.Savings

        while(self.income < MEANINCOME / 2):
            self.set_income((MEANINCOME * LAMBDA / ALPHA) * (np.random.gamma(shape = ALPHA, scale=ALPHA/LAMBDA)) * (1 + (INFLATION / (TICKSPERYEAR * 100))) ** current_timestep)

        self.set_capital(self.income * SAVINGS / 100)

    def make_offer(self, houses_for_sale, ticks):
        """
        ;;  Search for properties that:
         ;;    is for sale
         ;;    is not already under offer
         ;;    costs no more than my budget
         ;;    is not the house I am already occupying
         ;;  but look at only buyer-search-length number of properties
         ;;  and make an offer on the most expensive of these.
         ;;  My budget is the sum of:
         ;;   the value of the mortgage I can get on the new house = affordability * income / interest rate
         ;;   plus the (projected) sale price of my current house
         ;;   minus the amount I need to pay back to the lender for my current mortgage,
         ;;   plus the amount of accumulated capital I have
         ;;   minus any stamp duty payable
         ;;  But I must have a sufficiently large cash deposit available
         ;;  The realtor notes the interest shown in each of the houses in this subset
        """

        new_mortgage = self.get_income() * self.model.Affordability / (self.model.interestPerTick * self.model.TicksPerYear * 100)
        budget = new_mortgage - self.stamp_duty_land_tax(new_mortgage)

        deposit = self.get_capital()
        #if is-house? my-house [ set deposit deposit + ([ sale-price ] of my-house - mortgage) ]
        if(self.get_my_house() != None):
            deposit = deposit + (self.get_my_house().get_sale_price() - self.get_mortgage())

        upperbound = budget + deposit
        if(self.model.MaxLoanToValue < 100):
            values = []
            values.append(budget + deposit)
            values.append(deposit / (1 - self.model.MaxLoanToValue / 100))
            upperbound = min(values)

        """
        ; if I am in negative equity, I cannot afford to buy a house and
        ;  will have to remain where I am
        """
        if(upperbound < 0):
            self.get_my_house().set_for_sale(False)
            return

        lowerbound = upperbound * 0.7
        current_house = self.get_my_house()
        interesting_house = [i for i in houses_for_sale if (not i.get_offered_to()) and
                                                            (i.get_sale_price() <= upperbound) and
                                                            (i.get_sale_price() > lowerbound) and
                                                            (i != current_house)]

        """
        ; if there are more interesting houses than the buyer's search length,
        ;   select that number at random
        """
        if(len(interesting_house) > self.model.BuyerSearchLength):
            interesting_house = random.sample(interesting_house, self.model.BuyerSearchLength)

        if(len(interesting_house) > 0):
            #;select the best that has not already had an offer on it
            property = max(interesting_house, key=attrgetter('sale_price'))
            #; if I have found a suitable property, place an offer for it
            if(property != None):
                property.set_offered_to(self)
                property.set_offer_date(ticks)

                self.made_offer_on = property


    def move_house(self, model, ticks, record_id):
        """
        ;; move me to the house I am buying
        ;; then move the seller to their new house etc.
        """
        new_house = self.get_made_offer()

        if(new_house == None):
            return

        seller = new_house.get_owner()

        if(seller != None):
            #; seller gets selling price to pay off mortgage or add to capital
            profit = new_house.get_sale_price() - seller.get_mortgage()
            seller.set_mortgage(0)

            if(profit > 0):
                #; seller has made a profit, which is kept as capital
                seller.set_capital(seller.get_capital() + profit)

        new_house.set_owner(self)

        duty = self.stamp_duty_land_tax(new_house.get_sale_price())

        if(new_house.get_sale_price() > self.get_capital()):
            """
            (income * Affordability /
                                        ( interestPerTick * ticksPerYear * 100 ))
            """
            list_ = []
            list_.append((self.get_income() * self.model.Affordability / (self.model.interestPerTick * self.model.TicksPerYear * 100)))
            list_.append(new_house.get_sale_price() * self.model.MaxLoanToValue / 100)
            #; if the owner can't pay for the house in cash, s/he has to have a mortgage
            #; borrow as much as possible, given owner's income and value of house
            self.set_mortgage(np.min(list_))
            #; pay rest from capital
            self.set_capital(self.get_capital() - int(new_house.get_sale_price() - self.get_mortgage()) - duty)

            self.set_repayment(self.get_mortgage() * self.model.interestPerTick / (1 - ( 1 + self.model.interestPerTick) ** ( - self.model.MortgageDuration * self.model.TicksPerYear)))
        else:
            #; or if cash buyer, don't need mortgage and use capital
            self.set_mortgage(0)
            self.set_repayment(0)
            self.set_capital(self.get_capital() - new_house.get_sale_price() - duty)

        if(self.get_capital() < 0):
            self.set_capital(0)


        model.grid.place_agent(self, new_house.pos)

        self.set_homeless(0)

        self.set_my_house(new_house)

        self.set_date_of_purchase(ticks)

        new_house.set_for_sale(False)
        new_house.set_offered_to(None)

        self.set_made_offer_on(None)

        #;; update realtor's history with this sale price
        record = Records(record_id, new_house, new_house.get_sale_price(), ticks, model)
        model.schedule.add(record)
        new_house.get_my_realtor().file_record(record)

        model.moves += 1

        if(seller != None):
            seller.move_house(model, ticks, model.get_new_id())



    def follow_chain(self):
        """
        ;; Find the end of the chain which has my house as a link:
        ;;   find the house I have made an offer for (If none, this chain fails; Stop)
        ;;   find the current owner of that house (If none, this is a successful chain; Stop )
        ;;   find the house they made an offer for ...
        ;; continue until the seller of that house is the first buyer.
        ;;   This is a successful chain; Stop
        """
        if(self.get_made_offer() == None):
            return False

        seller = self.get_made_offer().get_owner()

        if(seller == None):
            return True

        if(self == seller):
            return True

        return seller.follow_chain()


    def get_made_offer(self):
        return self.made_offer_on

    def set_made_offer_on(self, offer):
        self.made_offer_on = offer

    def set_homeless(self, value):
        self.homeless = value

    def get_homeless(self):
        return self.homeless

    def set_income(self, new_income):
        self.income = new_income

    def get_capital(self):
        return self.capital

    def set_capital(self, capital_n):
        self.capital = capital_n

    def get_income(self):
        return self.income

    def set_date_of_purchase(self, date):
        self.date_of_purchase = date

    def set_mortgage(self, new_mortgage):
        self.mortgage = new_mortgage

    def get_mortgage(self):
        return self.mortgage

    def get_my_house(self):
        return self.my_house

    def set_my_house(self, house):
        self.my_house = house

    def get_owner_id(self):
        return self.owner_id

    def set_repayment(self, new_repayment):
        self.repayment = new_repayment

    def get_repayment(self):
        return self.repayment

    def stamp_duty_land_tax(self, cost):
        if (self.model.StampDuty):
            if(cost > 500000):
                return 0.04 * cost
            if(cost > 250000):
                return 0.02 * cost
            if(cost > 150000):
                return 0.01 * cost
        return 0
