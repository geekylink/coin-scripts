import math
import json
from coin import Coin

class MiningCalc:
    curr_btc_price = 777.94
    coins = {}

    def getTimePerBlock(self, diff, hashrate):
        target = 0x00000000ffff0000000000000000000000000000000000000000000000000000 / diff
        return math.pow(2,256)/(target*hashrate)

    def calculate(self, diff, reward, period, hashrate):
        """ Calculates the number of coins per period at this hashrate """
        time_per_block = self.getTimePerBlock(diff, hashrate)
        coins = reward/time_per_block * 3600 * 24
   
        return coins

    def calculate_by_coin(self, coin, period, hashrate):
        return self.calculate(coin.diff, coin.reward, period, hashrate)

    def load_coinchoose(self):
        f = open("difficulty", 'r')
        data = json.loads(f.read())
        
        for coin in data:
            # We only care about scrypt
            if coin["algo"] != "scrypt":
                break

            c = Coin(coin["name"], coin["symbol"], coin["price"])
            c.diff = float(coin["difficulty"])
            c.reward = float(coin["reward"])

            self.coins[coin["symbol"]] = c

    def print_values(self):
        print "Num coins: ", len(self.coins)
        for c in self.coins:
            num_coins = m.calculate(float(self.coins[c].diff), float(self.coins[c].reward), 86400, 2500*1000)
            value_btc = num_coins*float(self.coins[c].valueBTC)
            value_usd = value_btc*self.curr_btc_price
            print c, "\t", num_coins, "\t", value_btc, "BTC\t$", value_usd
            


m = MiningCalc()
m.load_coinchoose()
m.print_values()


    #coins = m.calculate(float(coin["difficulty"]), float(coin["reward"]), 86400, 2500*1000)
    #value_btc = coins*float(coin["price"])
    #value_usd = value_btc*m.curr_btc_price    
    #print coin["0"], coins, "\tValues:", value_btc, "BTC\t$", value_usd


diff = 311.139
reward = 500000
price_btc = 0.00000047
period = 86400
hash_rate = 2500*1000

#c = Coin("DogeCoin", "DOGE", 0.00000047) 
#c.diff = diff
#c.reward = reward

