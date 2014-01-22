from cryptsy import Bank, Order, Market, Cryptsy
import sys
import curses
from curses import panel

class TraderApp(object):
    def __init__(self, stdscr):
        self.screen = stdscr
        #self.window = self.screen.subwin(0,0)
        #self.window.keypad(1)
        curses.curs_set(0)

        self.screen.addstr("Tradesy v0")
        self.screen.refresh()
    
        self.win_trade = curses.newwin(34, 35, 1, 0)
        self.win_trade.border(0)
        self.win_trade.refresh()

        self.win_history = curses.newwin(34, 45, 1, 40)
        self.win_history.border(0)
        self.win_trade.refresh()

        self.win_orders = curses.newwin(10, 45, 1, 100)
        self.win_orders.border(0)
        self.win_orders.refresh()

        #self.panel = panel.new_panel(w2)
        #self.panel.show()
        #self.panel.window().addstr("hey")
        #self.panel.window().refresh()
        
        self.init_markets()
        self.update()

        self.main_loop()
        self.cleanup()

    def init_markets(self):
        self.c = Cryptsy()
        self.c.update_markets()

    def update_trades_window(self, market, limit):
        """ Updates the trades window """
        self.win_trade.addstr(0, 10, "Loading...")
        self.win_trade.refresh()

        self.c.update_orders_by_market(market)
        self.win_trade.addstr(0, 10, "  " + market.primary_code + "/" + market.secondary_code + "  ")
        line_no = 0

        # Displays sells
        for i in range(0, limit):
            s = "" + market.sell_orders[limit-i].price + " : " + str(market.sell_orders[limit-i].volume_in_btc())
            self.win_trade.addstr(1+line_no, 3, s)
            line_no += 1 
           
        line_no += 1

        # Displays buys
        for i in range(0, limit):
            s = "" + market.buy_orders[i].price + " : " + str(market.buy_orders[i].volume_in_btc())
            self.win_trade.addstr(1+line_no, 3, s)
            line_no += 1 

    def update_history_window(self, market, limit):
        """ Updates the order history window """
         
        self.win_history.addstr(0, 10, "Loading...")
        self.win_history.refresh()

        self.c.update_trade_history(market)
    
        self.win_history.addstr(0, 10, " " + market.primary_code + "/" + market.secondary_code + " ")


        line_no = 2

        # display history
        for i in range(0, limit):
            s = "" + str(market.history[i].date)[14:] + " : " + market.history[i].price + " : " + str(market.history[i].volume_in_btc())
            self.win_history.addstr(line_no, 1, " " + s)
            line_no += 1

    def update_my_orders_window(self, market, limit):
        """ Updates the my orders window """
        self.win_orders.addstr(0, 10, "Loading...")
        self.win_orders.refresh()

        self.c.update_my_open_orders(market)

        self.win_orders.addstr(0, 10, " " + market.primary_code + "/" + market.secondary_code + " ")

        line_no = 2

        # Display orders
        limit = min(len(market.my_orders), limit)
        for i in range(0, limit):
            s = market.my_orders[i].order_type + " " + str(market.my_orders[i].date)[14:] + " : " + market.my_orders[i].price + " : " + str(market.my_orders[i].volume_in_btc()) 
            self.win_orders.addstr(line_no, 1, s)
            line_no += 1
        
    def update(self):
        self.update_trades_window(self.c.markets["DOGE/BTC"], 15)
        self.update_history_window(self.c.markets["DOGE/BTC"], 30)
        self.update_my_orders_window(self.c.markets["DOGE/BTC"], 30)
        

    def main_loop(self):
        """ This loop executes till the program ends """
        while True:
            self.win_trade.refresh()
            self.win_history.refresh()
            self.win_orders.refresh()
            ch = self.screen.getch()

            if ch == ord('q'):
                break
            elif ch == ord('u'):
                self.update()

    def cleanup(self):
        pass
        


if __name__ == "__main__":
    curses.wrapper(TraderApp)

#c = Cryptsy()
#c.update_markets()
#c.update_my_open_orders(c.markets["DOGE/BTC"])

#c.update_markets()
#    print_orders(c.markets["LTC/BTC"], 5)

    
