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
    def __init__(self, price, vol, order_type = None, date = None, order_id = -1, fee = 0):
        self.price = price
        self.volume = vol
        self.order_type = order_type
        self.date = date
        self.order_id = order_id
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
    my_history      = []

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

    def get_bter_ticker(self):
        return self.primary_code.lower() + "_" + self.secondary_code.lower()

class Bter:
    bank = None
    markets = {} # Sorted by label "primary/secondary"

    def __init__(self):
        self.bank = Bank()

    def get_ticker(self, code1, code2):
        return code1.lower() + "_" + code2.lower()

    def update_balance(self):
        """ Updates the balances for each coin """
        response = self.api_query("private/getfunds", True)
        coins = response["available_funds"]
  
        for c in coins:
            if float(coins[c]) > 0.0:
                self.bank.add_coin(c, coins[c])


    def get_bank(self):
        """ Returns this bank object """
        return self.bank

    def update_markets(self):
        """ Updates every market """
        market = Market()
        market.primary_code = "doge"
        market.secondary_code = "btc"
        self.markets["doge_btc"] = market 

    def update_orders(self, response, market):
        """ Gets the current open orders on this market """
        market.buy_orders = []
        market.sell_orders = []

        for bid in response["bids"]:
            order = Order(bid[0], bid[1])
            market.buy_orders.append(order)

        for ask in response["asks"]:
            order = Order(ask[0], ask[1])
            market.sell_orders.insert(0, order)

    def update_orders_by_ticker(self, ticker):
        """ Gets the current open orders on this market """
        resp = self.api_query("depth/" + ticker)
        return self.update_orders(resp, self.markets[ticker])

    def update_orders_by_market(self, market):
        """ Gets the current open orders on this market """
        ticker = market.get_bter_ticker()
        resp = self.api_query("depth/" + ticker) 
        return self.update_orders(resp, market)

    def update_history(self, response, market):
        """ Updates the trade history log """
        market.history = []
        for trade in response["data"]:
            order = Order(trade["price"], trade["amount"], trade["type"], trade["date"]) 
            market.history.insert(0, order)


    def update_history_by_ticker(self, ticker):
        """ Gets the last 1000 trades for this market """
        resp = self.api_query("trade/" + ticker)
        return self.update_history(resp, self.markets[ticker])

    def update_history_by_market(self, market):
        """ Gets the last 1000 trades for this market """
        ticker = market.get_bter_ticker()
        resp = self.api_query("trade/" + ticker)
        return self.update_history(resp, market)
        

    def update_my_open_orders(self):
        """ Gets our current orders on the market  """
        resp = self.api_query("private/orderlist", True)

        orders = resp["orders"]

        for m in self.markets:
            self.markets[m].my_orders = []

        
        for order in orders:
            order_type = "SELL"
            amount = order["buy_amount"]
            ticker = self.get_ticker(order["sell_type"], order["buy_type"])
            # Bter doesn't return the actual price, so we need to compute it
            # TODO: This bit only works with coins that are worth less than 1 btc.
            price1 = float(order["sell_amount"])/float(order["buy_amount"])
            price2 = float(order["buy_amount"])/float(order["sell_amount"])

            if order["sell_type"] == "BTC":
                order_type = "BUY"
                amount = order["sell_amount"]
                ticker = self.get_ticker(order["buy_type"], order["sell_type"])

            price = "0." + str(long(round(min(price1, price2)*1e8))).rjust(8, "0")
            
            o = Order(price, amount, order_type, None, order["id"]) 
            self.markets[ticker].my_orders.append(o)

    def update_my_history(self, market):
        """ Gets the our last trades """
        pass
        
    def place_order(self, ticker, order_type, price, quantity):
        """ Places an order """
        order_type = order_type.upper()
        resp = self.api_query("private/placeorder", True, {"pair": ticker, "type": order_type, "rate": price, "amount": quantity})
        return True

    def cancel_order(self, order_id):
        """ Cancels an order """
        resp = self.api_query("private/cancelorder", True, {"order_id": order_id})

    def build_sign(self, args):
        """ Builds an appropriate signed message (sha512) given the parameters """
        res = ""

        for para in args:
            res = res + str(para) + "=" + str(args[para]) + "&"

        res = res[0:len(res)-1] 

        return hmac.new(PrivateKey, res, hashlib.sha512).hexdigest()

    def api_query(self, path, post = False, args = {}):
        """ Runs an api function call on cryptsy """
        par = {"nonce": int(time.time())}

        # Append additional input args
        for a in args:
            par[a] = args[a]

        sign = self.build_sign(par)
        head = {"SIGN": sign, "KEY": PublicKey} 
    
        r = ""

        if post:
            r = requests.post("http://data.bter.com/api/1/" + path, data=par, headers=head)
        else:
            r = requests.get("http://data.bter.com/api/1/" + path, headers=head)
        data = json.loads(r.text)

        # errors can happen
        #if data["result"] != "true":
        #    raise Exception("API Query failed:" + r.text) 

        return data


