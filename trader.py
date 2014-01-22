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
        
    def update(self):
        self.update_trades_window(self.c.markets["LTC/BTC"], 15)
        

    def main_loop(self):
        """ This loop executes till the program ends """
        while True:
            self.win_trade.refresh()
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
#    print_orders(c.markets["LTC/BTC"], 5)

    
