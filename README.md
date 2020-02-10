# Love-Death-Robots
Robot Killer scrypt

Trade Too Small = 0.0001BTC limit
v2/exchangeRate/list/ = fiat ratio
How to calculate real exchange rate ?

For your needs, you need to check the latest trades where you will also find the price:
file_get_contents($url."trades?market=LTCBTC&limit=1");
Last trade price = Exchange self rate

Limit Price = fee / feeOrganizationPercent * Amount to sell
Spending = Limit Price * Amount to buy

Exchange Fees
NiceHash Exchange has a very simple fee structure with maker and taker fees. Learn more about the difference between taker and maker fees here.
Trade levels are calculated base on your lifetime activity. Once you reach a certain level, you will never go to a higher fee again!
Here is the fee structure:
Trade level |	MAKER FEE |	TAKER FEE
up to 1.000 EUR	0.5%	0.5%
up to 10.000 EUR	0.4%	0.4%
up to 100.000 EUR	0.3%	0.3%
up to 1.000.000 EUR	0.2%	0.2%
up to 10.000.000 EUR	0.1%	0.1%
up to 100.000.000 EUR	0.05%	0.08%
up to 1.000.000.000 EUR	0.04%	0.06%
up to 10.000.000.000 EUR	0.03%	0.05%
up to 100.000.000.000 EUR	0.02%	0.04%
over 100.000.000.000 EUR	0.01%	0.03%

Current exchange rate for given pair:

file_get_contents($url."trades?market=LTCBTC&limit=1");

Is there an API call to get current nicehash fee amount for given organization ID?
How can i calculate current Volume till lower Fee using API?

GET /exchange/api/v2/info/fees/status

https://api2.nicehash.com/exchange/api/v2/info/fees/status

You will get:
makerCoefficient: 0.005
takerCoefficient: 0.005
sum: 71.1

https://api2.nicehash.com/main/api/v2/public/service/fee/info
You will get fee classes:

exchangeMaker: {coin: null,…}
coin: null
intervals: [{start: 0, end: 1000, element: {value: 0.005, type: "PERCENTAGE", sndValue: null, sndType: null}},…]
0: {start: 0, end: 1000, element: {value: 0.005, type: "PERCENTAGE", sndValue: null, sndType: null}}
1: {start: 1000, end: 10000, element: {value: 0.004, type: "PERCENTAGE", sndValue: null, sndType: null}}
2: {start: 10000, end: 100000, element: {value: 0.003, type: "PERCENTAGE", sndValue: null, sndType: null}}
3: {start: 100000, end: 1000000,…}
4: {start: 1000000, end: 10000000,…}
5: {start: 10000000, end: 100000000,…}
6: {start: 100000000, end: 1000000000,…}
7: {start: 1000000000, end: 10000000000,…}
8: {start: 10000000000, end: 100000000000,…}
9: {start: 100000000000, end: null,…}


Calculations in BTC
                    			price 	qty	  sndQty	fee/sell	fee/buy
BTC is first symbol	  		sec	    BTC	  sec	    sec	      BTC
BTC is the second symbol	sec	    pri	  BTC	    BTC	      pri

case of no BTC in pair???


1. Calculate total trades amount
2. Calculate current fee
3. Calculate minimal order
4. Get closing SELL/BUY orders spread
5. Manual minimal trade shift using API
  5.1 Get all my open orders
  5.2 List more than 1 last trade
  5.3 Refresh shift price function
  5.4 Mark my orders with my trade size in my order book
  5.5 calculate percentage of my order related to market size
  5.5.1 Market selector Number and Name
  5.6 My trades summary calculator
  
  5.6 Set limit price boundary automation algo
  
6. Robot pressure
7. 

x. WebSocket subscription

todo:
- Sell check routines
- check currency minimal amount based on endpoint data
- calculate minimal opposite profit based on fees and order sizes

Robot bahaviour:
- always cut minimal amount to be first in line
- has trade boundary limits (hi and lo)
- if there two or more robots at the boundary let them do their job till boundaries
- exchange didn't show automated trades in the exchange interface, it has a big lag or even didn't show orders at the spread edges!!!

Counterspells:
- always check robot market size
- if they fall to minmal trade size - stop and add funds to the last order
- always watch for opposite direction extremums prices and don't cross it if price too bad
- have funds on both sides
- shift robots to get out of market orders and real prices
- double check market sizes on both directions and minimum/maximum price boundaries outside trade edges (spread)
- always check possibility to buy from the other edge if it's not far to reach
- if there are more than two robots, you need just one trade to start them rolling to their boundaries without your help
- let the gap before the edge be more than minimum coin part, since robots on other side can wake up and eat your shift trade
- if robots stops - check if there NN and wait for movements in directions, step sizes and order sizes.


# probably Withstand
NiceHash bot for automatic order management.

Features

Create new orders (including when 2FA is turned on)

Automatically manage orders for:

- price adjustment - keep price as low as possible and sustain wanted speed, but keep price below max specified

- refilling - automatically refill order when it is nearly depleted

- re-creation - automatically create new order if order is removed by the system (timeout or any other reason)

Ability to adjust max price and speed limit for each monitored order

Pool manager to easily define new pools, remove them or use for orders

Console window showing all important events or errors

Custom order handlers
