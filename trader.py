from cryptsy import Bank, Order, Market, Cryptsy
import sys
import curses
from curses import panel

class Window(object):
    window = None
    previous_title_len = 0

    def __init__(self, x, y, width, height):
        self.window = curses.newwin(height, width, y, x)
        self.window.border(0)
        self.window.refresh()
        self.line_no = 1

    def set_title(self, title):
        """ Sets the title for this window and clears the old title """
        height, width = self.window.getmaxyx()

        length = len(title)
        
        self.clear_line(width/2 - self.previous_title_len/2, 0, self.previous_title_len)
        self.window.addstr(0, width/2 - len(title)/2, title)

        self.previous_title_len = length
        self.window.refresh()

    def add_line(self, line):
        """ Adds a line to the window """
        height, width = self.window.getmaxyx()
        self.window.addstr(self.line_no, 2, line[:width-4])
        self.line_no += 1

    def clear_lines(self):
        """ Clears all lines of this window """
        height, width = self.window.getmaxyx()
        fill_string = "".center(width-2)

        for i in range(1, self.line_no):
            self.window.addstr(i, 1, fill_string)

        self.line_no = 1

    def clear_line(self, x, y, width):
        """ Clears line y between characters x to x+width """
        for i in range(0, width):
            self.window.addch(y, x+i, " ")

class BalanceWindow(Window):

    def update(self, c):
        self.set_title("Loading...")
        c.update_balance()
        self.clear_lines()
        self.set_title("Balances")

        b = c.get_bank()

        for coin in b.coins:
            self.add_line(coin + " " + str(b.coins[coin]))

        self.window.refresh()

class MyOrdersWindow(Window):
    
    def update(self, c, market):
        limit = 10
        self.set_title("Loading...")

        c.update_my_open_orders(market)
        self.clear_lines()
        self.set_title(market.primary_code + "/" + market.secondary_code + " ")

        # Display active orders
        limit = min(len(market.my_orders), limit)
        for i in range(0, limit):
            s = market.my_orders[i].order_type + " " + str(market.my_orders[i].date)[14:] + " : " + market.my_orders[i].price + " : " + str(market.my_orders[i].volume_in_btc())[0:7] 
            s = s + " : " + str(market.my_orders[i].volume)[0:10]
            self.add_line(s)

        self.window.refresh()

class HistoryWindow(Window):

    def update(self, c, market):
        limit = 30
        self.set_title("Loading...")

        c.update_trade_history(market)
        self.clear_lines()
        self.set_title(market.primary_code + "/" + market.secondary_code + " ")
    
        # display history
        for i in range(0, limit):
            s = "" + str(market.history[i].date)[14:] + " : " + market.history[i].price + " : " + str(market.history[i].volume_in_btc())[0:7]
            s += " : " + str(market.history[i].volume)
            self.add_line(s)

        self.window.refresh()

class TradeWindow(Window):

    def update(self, c, market):
        limit = 15
        self.set_title("Loading...")
        c.update_orders_by_market(market)
        self.clear_lines()
        self.set_title(market.primary_code + "/" + market.secondary_code + " ")

        # Displays sells
        for i in range(0, limit):
            s = "" + market.sell_orders[limit-i].price + " : " + str(market.sell_orders[limit-i].volume_in_btc())[0:7]
            s += " : " + str(market.sell_orders[limit-i].volume)
            self.add_line(s)

        self.add_line("")

        # Displays buys
        for i in range(0, limit):
            s = "" + market.buy_orders[i].price + " : " + str(market.buy_orders[i].volume_in_btc())[0:7]
            s += " : " + str(market.buy_orders[limit-i].volume)
            self.add_line(s)

        self.window.refresh()

class MyHistoryWindow(Window):

    def update(self, c, market):
        limit = 12
        self.set_title("Loading...")
        c.update_my_history(market)
        self.clear_lines()
        self.set_title("My last trades")

        limit = min(len(market.my_history), limit)
        for i in range(0, limit):
            s = market.my_history[i].order_type + " " + market.my_history[i].price + " : " + str(market.my_history[i].volume_in_btc())[0:7]
            s += " : " + str(market.my_history[i].volume)
            self.add_line(s)

        self.window.refresh()

class TraderApp(object):
    windows = {}

    def __init__(self, stdscr):
        self.screen = stdscr
        curses.curs_set(0)

        self.screen.addstr("Tradesy v0")
        self.screen.refresh()
    
        self.windows["trade"] = TradeWindow(0, 1, 40, 34)
        self.windows["history"] = HistoryWindow(41, 1, 50, 34)
        self.windows["my_orders"] = MyOrdersWindow(91, 1, 50, 10)
        self.windows["balance"] = BalanceWindow(91, 11, 50, 10)
        self.windows["my_history"] = MyHistoryWindow(91, 21, 50, 14)

        #self.panel = panel.new_panel(w2)
        #self.panel.show()
        #self.panel.window().addstr("hey")
        #self.panel.window().refresh()
        
        self.init_markets()

        self.main_loop()
        self.cleanup()

    def init_markets(self):
        self.c = Cryptsy()
        self.c.update_markets()
        self.update()
        self.windows["my_orders"].update(self.c, self.c.markets["DOGE/BTC"])
        self.windows["balance"].update(self.c)
        self.windows["my_history"].update(self.c, self.c.markets["DOGE/BTC"])
        
    def update(self):
        self.windows["trade"].update(self.c, self.c.markets["DOGE/BTC"])
        self.windows["history"].update(self.c, self.c.markets["DOGE/BTC"])

    def main_loop(self):
        """ This loop executes till the program ends """
        mode = "watch"
        strBuild = ""
        strPrice = ""
        strAmount = ""
        col_num = 20

        while True:
            # Refresh all the windows
            for win in self.windows:
                self.windows[win].window.refresh()

            self.screen.addstr(0, 15, "m:" + mode + "   ")
            ch = self.screen.getch()

            if mode == "watch":
                if ch == ord('q'):
                    break
                elif ch == ord('u'):
                    self.update()
                elif ch == ord('o'):
                    self.windows["my_orders"].update(self.c, self.c.markets["DOGE/BTC"])
                    self.windows["balance"].update(self.c)
                    self.windows["my_history"].update(self.c, self.c.markets["DOGE/BTC"])
                elif ch == ord('b'):
                    mode = "Buy"
                    self.screen.addstr(0, 43, "P:")
                elif ch == ord('s'):
                    mode = "Sell"
                    self.screen.addstr(0, 43, "P:")
                elif ch == ord('c'):
                    self.windows["balance"].clear_lines()
            else: # Buy mode
                if ch == ord('q'):
                    self.screen.addstr(0, 43, "                                     ")
                    self.screen.addstr(0, 80, "Canceled order.                                    ")
                    mode = "watch"
                    continue

                elif ch == 8: # Back space
                    if len(strBuild) > 0:
                        strBuild = strBuild[:-1]
                        col_num -= 1
                        self.screen.addch(0, col_num, ch)

                elif ch == ord('\n'):
                    col_num = 45
                    self.screen.addstr(0, col_num, "                       ")
                    if strPrice == "":
                        self.screen.addstr(0, 43, "A:                        ")
                        strPrice = strBuild
                    elif strAmount == "":
                        strAmount = strBuild
                        self.screen.addstr(0, 80, mode + " at " + strPrice + " for " + strAmount + ". Hit enter again to place.")
                    else:
                        res = self.c.place_order(self.c.markets["DOGE/BTC"], mode, strPrice, strAmount)

                        self.screen.addstr(0, 43, "                             ")

                        if res:
                            self.screen.addstr(0, 80, "Order has been placed.                                    ")
                        else:
                            self.screen.addstr(0, 80, "Could not place order at this time.                       ")
                            
                        strPrice = strAmount = ""
                        mode = "watch"
                        self.windows["my_orders"].update(self.c, self.c.markets["DOGE/BTC"])

                    strBuild = ""
                    continue
                    
                strBuild = str(strBuild) + chr(ch)
                self.screen.addstr(0, 45, strBuild)
                col_num += 1
                
                    #self.c.place_order(self.c.markets["DOGE/BTC"], "Buy", 0.00000165, 1000) 

    def cleanup(self):
        pass
        


if __name__ == "__main__":
    curses.wrapper(TraderApp)

#c = Cryptsy()
#c.update_markets()
#c.update_my_open_orders(c.markets["DOGE/BTC"])

#c.update_markets()
#    print_orders(c.markets["LTC/BTC"], 5)

    
