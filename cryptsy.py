import json
import urllib2
import math

class Coin:
    diff        = None
    code        = ""
    name        = ""
    amount      = 0
    valueBTC    = 0    
    valueUSD    = 0
    amount      = 0

    def __init__(self, name, code, value):
        self.code = code
        self.name = name
        self.valueBTC = value

    def set_value_BTC(self, value):
        self.valueBTC = value

    def get_value_BTC(self):
        return self.valueBTC

    def get_ticker(self):
        return self.code

    def get_name(self):
        return self.name

class Bank:
    coins = {}
    total = 0

    def __init__(self):
        pass

    def get_total_in_btc(self):
        total = 0
        for c in self.coins:
            val = float(self.get_btc_value(c))
            amount = float(self.get_amount(c))
            total += val*amount

        return total

    def get_total_in_USD(self):
        pass

    def get_btc_value(self, code):
        return self.coins[code].valueBTC
   
    def get_amount(self, code):
        return self.coins[code].amount

    def add_coins(self, code, amount):
        self.coins[code].amount += amount

    def add_new_coin(self, code, coin):
        assert code not in self.coins
        self.coins[code] = coin

    def has_coin(self, code):
        return code in self.coins
            
class Cryptsy:
    data = "" 

    def load_from_file(self, filename):
        """ Loads the data for this exchange from a file """
        f = open(filename, 'r')
        self.data = json.loads(f.read())

        return self.is_success()

    def load(self):
        """ Loads from online """
        # Only one line
        for line in urllib2.urlopen("http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=132"):
            self.data = json.loads(line)
            break

        return self.is_success()

    def is_success(self):
        """ Returns True if the data is successfully loaded """ 
        return self.data["success"] == 1

    def add_all_coins(self, bank):
        coins = self.get_trade_for("BTC")
        for coin in coins:
            bank.add_new_coin(coin, Coin("$", coin, self.get_last_btc_value(coin)))

    def get_last_btc_value(self, code):
        s = code + "/BTC"
        return self.get_last_trade_price(s)

    def get_last_trade_price(self, ticker):
        """ Gets the last trade price  """

        markets = self.data["return"]["markets"]

        for market in markets:
            if market == ticker:
                return markets[ticker]["lasttradeprice"]

        return None

    def get_trade_for(self, code):
        """ Returns all coins that can be traded for this one """
        codes = []
        markets = self.data["return"]["markets"]

        for market in markets:
            m = markets[market]

            if m["primarycode"] == code:
                codes.append(m["secondarycode"])
            elif m["secondarycode"] == code:
                codes.append(m["primarycode"])

        return codes

b = Bank()
c = Cryptsy()
c.load_from_file("dummy2")
c.add_all_coins(b)

print b.get_btc_value("DOGE")
b.add_coins("DOGE", 164000)
print b.get_amount("DOGE")

print b.get_total_in_btc(), "BTC"

#for coin in b.coins:
    #print b.coins[coin].code, b.coins[coin].valueBTC
#c.load()
#print c.get_last_trade_price("DOGE/BTC") 
#print c.get_trade_for("DOGE")
