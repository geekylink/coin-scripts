
class Coin:
    diff        = None
    code        = ""
    name        = ""
    reward      = 0
    amount      = 0
    valueBTC    = 0    
    valueUSD    = 0
    amount      = 0

    def __init__(self, name, code, valueBTC):
        self.code = code
        self.name = name
        self.valueBTC = valueBTC

    def set_value_BTC(self, value):
        self.valueBTC = value

    def get_value_BTC(self):
        return self.valueBTC

    def get_ticker(self):
        return self.code

    def get_name(self):
        return self.name
