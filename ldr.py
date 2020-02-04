import nicehash
import json

# import only system from os 
from os import system, name 
  
# import sleep to show output for some time period 
from time import sleep 

BTCpairFlag = False # Pair Flag for BTC is sec = False, pri = True
MIN_BTC_TRADE = 0.0001# minimal BTC trade size

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[32m'
    WARNING = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DARKGREY = "\033[90m"

# define our clear function 
def clear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

#clear screen
clear()

# For testing purposes use api-test.nicehash.com. Register here: https://test.nicehash.com
# When ready, uncomment line bellow, to run your script on production environment
# host = 'https://api2.nicehash.com'
# How to create key, secret and where to get organisation id please check:
# Production - https://www.nicehash.com
# organisation_id = 'Enter your organisation id'
# key = 'Enter your api key'
# secret = 'Enter your secret for api key'


# # # Test - https://test.nicehash.com
host = 'https://api-test.nicehash.com'
# # organisation_id = '286fcf65-d44e-4cdf-81f2-4790c0cbed04'
organisation_id = 'cdce8059-ab50-49b2-a66c-f1862ac4e8db'
# # key = '6b957253-bcb9-4b83-b431-4f28ab783a6f'
key = '5ec54745-1005-4296-a833-e701b6ffc22b'
# # secret = 'ac09da0c-0b41-49ba-be6f-4698f9c184a67c6a834f-5bfe-5389-ba6f-d9ada9a86c03'
secret = '70b1a01b-97fa-417b-9dc9-349524ef642b551e8c82-c73d-4c26-be06-f9304b4169ba'

# Create public api object
public_api = nicehash.public_api(host, True)

# Get all markets
markets = public_api.get_markets()
# print(markets)

# Get all curencies
currencies = public_api.get_curencies()
#currencies = ['BTC','ETH','BCH','LTC','USDT']
#print(currencies)

# Create private api object
private_api = nicehash.private_api(host, organisation_id, key, secret, True)

# Get balance for all currencies
my_accounts = private_api.get_accounts()
# print('\nMy accounts:')
# print(my_accounts)
# print ('\n')

# Get balance for BTC address
print('\nGet balance for BTC address:')
my_btc_account = private_api.get_accounts_for_currency(currencies['currencies'][0]['symbol'])
#my_btc_account = private_api.get_accounts_for_currency('BTC')
#print(my_btc_account)
#print('\n')

### EXCHANGE DATA
# Get exchange market info
#print ('\nGet exchange market info:')
exchange_info = public_api.get_exchange_markets_info()
#print(exchange_info)

# Get my exchnage trades
#my_exchange_trades = private_api.get_my_exchange_trades(exchange_info['symbols'][6]['symbol']) # LTC/BTC trades
print('\nGet my exchnage trades')
total_trades_amount = 0
for i in exchange_info['symbols']:
    if i['symbol'][:3] == 'BSV':
        my_exchange_trades = private_api.get_my_exchange_trades(i['symbol'])
        print(bcolors.OKGREEN+i['symbol']+bcolors.ENDC)
        sumBTC = 0
        print (my_exchange_trades)
        
        if i['symbol'][:3] == 'BTC':#Check pri/sec pair of currencies
            print(bcolors.FAIL+'BTC!!!'+bcolors.ENDC)
            BTCpairFlag = True
        else:
            BTCpairFlag = False
        
        for n in my_exchange_trades:
            fee = n['fee']
            price = n['price']
            print('price:',)
            print (price)
            sndQty = n['sndQty']
            print('sndQty:',)
            print(sndQty)
            
            if BTCpairFlag:# BTC is pri
                if n['dir'] == 'SELL':# checking order direction, if SELL then fee is in sec
                    sumBTC = sndQty/price+fee/price+sumBTC
                else:# checking order direction, if BUY then fee is in pri
                    sumBTC = sumBTC+sndQty/price+fee# calculate fee from exchange rate in BTC
            else:# BTC is sec
                if n['dir'] == 'SELL':# checking order direction, if SELL then fee is in sec
                    sumBTC = sumBTC+sndQty+fee
                else:# checking order direction, if BUY then fee is in pri
                    sumBTC = sumBTC+sndQty+fee*price# calculate fee from exchange rate in BTC

        print ('SUM:',sumBTC,"\n")
        total_trades_amount = total_trades_amount + sumBTC
# print ('\n')
# print(bcolors.OKBLUE+str(total_trades_amount)+bcolors.ENDC)

# Get my exchange orders
# for i in exchange_info['symbols']:
#     print ('\nGet my exchange orders for:'+i['symbol'])
#     my_exchange_orders = private_api.get_my_exchange_orders(i['symbol'])# need to submit status parameter (open) to get all current open orders
#     print (my_exchange_orders)
# print ('\n')

# Get my fees and trade volume status
# GET /exchange/api/v2/info/fees/status
#print('Get my fees and trade volume status:')
my_fees_volume_status = private_api.get_my_fees()
#print(my_fees_volume_status)

# Get my current maker fee
my_current_maker_fee = my_fees_volume_status['makerCoefficient']
# Get my current taker fee
my_current_maker_fee = my_fees_volume_status['takerCoefficient']

# Get trades for LTC/BTC [6] market
# Calculate current minimal trade volume for given currency
# For your needs, you need to check the latest trades where you will also find the price:
# file_get_contents($url."trades?market=LTCBTC&limit=1");

print ('\nGet trades for first market:')
last_trade = public_api.get_exchange_last_trade(exchange_info['symbols'][6]['symbol']) # [6] corresponds to LTC/BTC
current_price = last_trade[0]['price']# Current (last) trade price
trade_direction = last_trade[0]['dir']# BUY or SELL
if trade_direction == 'BUY':
    print(bcolors.OKGREEN)
else:
    print(bcolors.WARNING)
print (current_price, trade_direction)
print(bcolors.ENDC)
#calculate minimal trade size in pri currency

#shifting robots
if (trade_direction == 'BUY'):
    print(bcolors.HEADER+'Last Trade was BUY!!!'+bcolors.ENDC)
    limit_price = current_price+0.00000001# if last trade was BUY then my price is MORE than last trade price for 0.00000001
else:
    print(bcolors.HEADER+'Last Trade was SELL!!!'+bcolors.ENDC)
    limit_price = current_price-0.00000001# if last trade was BUY then my price is LESS than last trade price for 0.00000001

#Calculate minimum trade size
min_trade_size = MIN_BTC_TRADE/limit_price
print('Minimum Trade Size:')
print(min_trade_size)
print('My Limit Price:')
print(limit_price)




while True:
    
    # BUY/SELL closing orders spread
    # Get exchange orderbook

    print ('\nGet exchange orderbook:')
    exchange_orderbook = public_api.get_exchange_orderbook(exchange_info['symbols'][6]['symbol'], 1)
    #print (exchange_orderbook)
    #print ('\n')

    buy_edge_price = exchange_orderbook['buy'][0][0]
    buy_edge_amount = exchange_orderbook['buy'][0][1]
    sell_edge_price = exchange_orderbook['sell'][0][0]
    sell_edge_amount = exchange_orderbook['sell'][0][1]
    print(bcolors.OKGREEN+'Buy amount:\t',buy_edge_amount)
    print('Buy price:\t',buy_edge_price)
    print(bcolors.DARKGREY+'Exchange Rate:\t',current_price)
    print(bcolors.WARNING+'Sell price:\t',sell_edge_price)
    print('Sell amount:\t',sell_edge_amount)
    print(bcolors.ENDC)

    sell_or_buy=input('Sell(0) or Buy(1)?')
    clear()

    if sell_or_buy == '0':
        limit_price = buy_edge_price-0.00000001
        print(bcolors.WARNING)
    else:
        print(bcolors.OKGREEN)
        limit_price = buy_edge_price+0.00000001

    #Calculate minimum trade size
    min_trade_size = MIN_BTC_TRADE/limit_price
    print('Minimum Trade Size:\n')
    print(min_trade_size)
    print('\nAmount to SELL (My Limit Price):\n')
    print(limit_price)
    print(bcolors.ENDC)
   
