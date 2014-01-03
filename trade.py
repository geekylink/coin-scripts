import json

class BaseCoin:
    diff = 0
    ticker = ""
    value = 0

    def __init__(self, ticker):
        self.ticker = ticker

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_diff(self):
        return self.diff

    def get_ticker(self):
        return self.ticker

class DogeCoin(BaseCoin):
    
    def __init__(self):
        BaseCoin.__init__(self, "doge")
        self.value = 0.00044


#d = DogeCoin()
#print d.get_ticker()
#print d.get_value()*145000
