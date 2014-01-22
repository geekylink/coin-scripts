import json
import urllib2
import math
import requests
import time
import hashlib
import hmac

PrivateKey = ""
PublicKey = ""

class Bank:
    coins = {}

    def add_coin(self, ticker, amount):
        self.coins[ticker] = amount

    def get_coin(self, ticker):
        return self.coins[ticker]

class Order:
    def __init__(self, price, vol, order_type = None, date = None, fee = 0):
        self.price = price
        self.volume = vol
        self.order_type = order_type
        self.date = date
        self.fee = fee

    def volume_in_btc(self):
        """ Returns the volume in BTC """
        return float(self.volume)*float(self.price)

class Market:
    """ Stores data related to a market """
    primary_code    = ""
    secondary_code  = ""
    marketid        = -1
    last_trade      = 0
    high_trade      = 0
    low_trade       = 0
    volume          = 0
    sell_orders     = []
    buy_orders      = []
    history         = []
    my_orders       = []

    def total_buys(self):
        """ Returns the total amount of buy orders in bitcoin """
        return self.sum_orders(self.buy_orders)

    def total_sells(self):
        """ Returns the total amount of buy orders in bitcoin """
        return self.sum_orders(self.sell_orders)

    def total_buys_above(self, amount):
        """ Returns the total amount of buy orders above amount in bitcoin """
        total = 0
        for order in self.buy_orders:
            if float(order.price) >= float(amount):
                total += float(order.price)*float(order.volume)
        return total
                
    def total_sells_below(self, amount):
        """ Returns the total amount of buy orders above amount in bitcoin """
        total = 0
        for order in self.sell_orders:
            if float(order.price) <= float(amount):
                total += float(order.price)*float(order.volume)
        return total
                

    def sum_orders(self, orders):
        total = 0
        for order in orders:
            total += float(order.price)*float(order.volume)
        return total

class Cryptsy:
    bank = None
    markets = {} # Sorted by label "primary/secondary"

    def __init__(self):
        self.bank = Bank()

    def update_balance(self):
        """ Updates the balances for each coin """
        resp = self.api_query("getinfo")

        coins = resp["return"]["balances_available"]

        for c in coins:
            if float(coins[c]) > 0.0:
                self.bank.add_coin(c, coins[c])

    def get_bank(self):
        """ Returns this bank object """
        return self.bank

    def update_markets(self):
        """ Updates every market """
        resp = self.api_query("getmarkets")
        markets = resp["return"]

        for m in markets:
            new_market = Market()
            new_market.primary_code = m["primary_currency_code"]
            new_market.secondary_code = m["secondary_currency_code"]
            new_market.marketid = m["marketid"]
            new_market.last_trade = m["last_trade"]
            new_market.high_trade = m["high_trade"]
            new_market.low_trade = m["low_trade"]
            new_market.volume = m["current_volume"]

            self.markets[m["label"]] = new_market

    def update_orders_by_market(self, market):
        """ Gets the current open orders on this market """
        resp = self.api_query("marketorders", {"marketid": market.marketid})

        buy_orders = resp["return"]["buyorders"]
        sell_orders = resp["return"]["sellorders"]

        market.buy_orders = []
        market.sell_orders = []

        for buy in buy_orders:
            order = Order(buy["buyprice"], buy["quantity"])
            market.buy_orders.append(order)

        for sell in sell_orders:
            order = Order(sell["sellprice"], sell["quantity"])
            market.sell_orders.append(order)

        #print "24hr high:\t", market.high_trade, "\tlow:\t", market.low_trade
        #print "Last buy:\t", market.buy_orders[0].price, "\tsell:\t", market.sell_orders[0].price

        #print "Volume (@ask)\tbuy:\t", market.total_buys_above(float(market.buy_orders[0].price)), "\tsell:\t", market.total_sells_below(float(market.sell_orders[0].price))

        #for i in range(0, 15):
        #    print "Volume ", i ,"sato\tbuy:\t", market.total_buys_above(float(market.buy_orders[0].price) - 0.00000001*i), "\tsell:\t", market.total_sells_below(float(market.sell_orders[0].price) + 0.00000001*i)

        #print "Volume (24hr)\tbuy:\t", market.total_buys_above(market.low_trade), "\tsell:\t", market.total_sells_below(market.high_trade)
        #print "Volume (total)\tbuy:\t", market.total_buys(), "\tsell:\t", market.total_sells()

    def update_trade_history(self, market):
        """ Gets the last 1000 trades for this market """
        resp = self.api_query("markettrades", {"marketid": market.marketid})

        market.history = []
        for trade in resp["return"]:
            order = Order(trade["tradeprice"], trade["quantity"], trade["initiate_ordertype"], trade["datetime"]) 
            market.history.append(order)

    def update_my_open_orders(self, market):
        """ Gets our current orders on the market  """
        resp = self.api_query("myorders", {"marketid": market.marketid})

        market.my_orders = []
        for order in resp["return"]:
            o = Order(order["price"], order["quantity"], order["ordertype"], order["created"])
            market.my_orders.append(o)
        
    def place_order(self, market, order_type, price, quantity):
        try:
            resp = self.api_query("createorder", {"marketid": market.marketid, "ordertype": order_type, "quantity": quantity, "price": price})
        except e:
            return False

        return True



    def build_sign(self, args):
        """ Builds an appropriate signed message (sha512) given the parameters """
        res = ""

        for para in args:
            res = res + str(para) + "=" + str(args[para]) + "&"

        res = res[0:len(res)-1] 

        return hmac.new(PrivateKey, res, hashlib.sha512).hexdigest()

    def api_query(self, method, args = {}):
        """ Runs an api function call on cryptsy """
        par = {"nonce": int(time.time()), "method": method}

        # Append additional input args
        for a in args:
            par[a] = args[a]

        sign = self.build_sign(par)
        head = {"Sign": sign, "Key": PublicKey} 
    
        r = requests.post("https://www.cryptsy.com/api", data=par, headers=head)
        data = json.loads(r.text)

        # errors can happen
        if data["success"] != "1":
            raise Exception("API Query failed:" + r.text) 

        return data

