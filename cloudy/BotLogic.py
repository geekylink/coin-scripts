currentBuy = 0
currentSell = 0
currentBuyVol = 0
currentSellVol = 0

LastBought = 0
LastSold = 0

Factor = 0

c = Cryptsy()
c.update_markets()

while (true)
	time.sleep(30.0)
	c.update_orders_by_market(c.markets["DOGE/BTC"])
	update()


def update()
	currentBuy = c.markets["DOGE/BTC"].buy_orders[0].price
	currentSell = c.markets["DOGE/BTC"].sell_orders[0].price
	currentBuyVol = c.markets["DOGE/BTC"].total_buys_above(float(buy)))
	currentSellVol = c.markets["DOGE/BTC"].total_sells_below(float(sell)))
	checkNumbers()


def checkNumbers()
	decision = 0
	if (math.fabs(currentBuy - currentSell) > 2) {
		decision--
	}
	if (math.fabs(currentBuy - currentSell) < 2) {
		decision++
	}
	if (currentBuyVol > currentSellVol) {
		decision--
	}
	if (currentBuyVol < currentSellVol) {
		decision++
	}
	if (currentSell > LastBought) {
		decision--
	}
	if (currentBuy > LastSell) {
		decision++
	}
	decision = decision + Factor
	Decide(decision)


def Decide(num) 
	if (num > 0) {
		Factor = 0
		Buy(CurrentBuy)
	}
	if (num < 0) {
		Factor = 0
		Sell(CurrentSell)
	}
	if (num == 0) {
		Factor++
	}
