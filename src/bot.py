from cryptsy import Bank, Order, Market, Cryptsy

class Trades(object):
    sell_price = 0
    buy_price = 0


class Bot(object):
    market = None
    exchanges = {}

    def __init__(self, exchanges = {}):
        self.exchanges = exchanges

    def update_balances(self):
        """ Updates balances on each exchange """
        for ex in self.exchanges:
            ex.update_balance()

    def set_market(self, market):
        self.market = market

    def update(self):
        self.ex.update_orders_by_market(self.market)
        self.ex.update_trade_history(self.market)
        
    def logic(self):
        """ Main bot loop """
        self.bank = self.ex.get_bank()
        btc = self.bank.coins["BTC"]

        while True:
            pass

    def buy(self, price, amount):
        res = self.c.place_order(self.market, "Buy", price, amount)
        
    def sell(self, price, amount):
        res = self.c.place_order(self.market, "Sell", price, amount)
         

if __name__ == "__main__":
    ex = Cryptsy()
    ex2 = Bter()
    bot = Bot({"cryptsy": ex, "bter": ex2})
    bot.logic()

