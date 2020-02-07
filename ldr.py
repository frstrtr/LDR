import nicehash
import json
from bcolors import bcolors as bc
#from tabulate import tabulate

# import only system from os
from os import system, name

# import sleep to show output for some time period
from time import sleep

# import account related keys for sign operations
from keys import host, organisation_id, secret, key

BTCpairFlag = False  # Pair Flag for BTC is sec = False, pri = True
MIN_BTC_TRADE = 0.0001  # minimal BTC trade size
current_market = 12  # ETHBTC by default
manual_order_size = None # Automatical calculation

# Create public api object
public_api = nicehash.public_api(host, False)

# Create private api object
private_api = nicehash.private_api(host, organisation_id, key, secret, False)


def clear():
    '''define our clear console function'''

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def get_symbol_list():
    ''' Get all curencies symbols as list'''
    currencies = public_api.get_curencies()
    currencies_list = list(currencies['currencies'])
    symbol_list = list()
    for i in currencies_list:
        symbol_list.append(i['symbol'])
    # print (symbol_list) # ['BTC','ETH',etc...]
    return symbol_list


def get_market_list():
    '''Get all markets symbols as list'''
    markets = public_api.get_exchange_markets_info()
    market_list = markets['symbols']
    return market_list


def list_non_zero_balances():
    ''' Get balance for all currencies with funds'''
    currencies = public_api.get_curencies()
    # my_accounts = private_api.get_accounts()
    # print('\nMy accounts:')
    # print(my_accounts)
    # print ('\n')

    # Get balance for address with non-zero balance
    for accounts in currencies['currencies']:

        if private_api.get_accounts_for_currency(accounts['symbol'])['balance'] != '0':
            my_coin_balance = private_api.get_accounts_for_currency(accounts['symbol'])[
                'balance']
            print('My ', accounts['symbol'],
                  ' balance:', my_coin_balance, '\n')


def coin_select():
    '''Scan all available coins and choose one
    returns coin indexed list'''
    current_coin_list = get_symbol_list()
    counter = 0
    for i in current_coin_list:
        print(counter, i)
        counter += 1
    selected_coin = input('Select Coin to manipulate:')
    return selected_coin


def market_select():
    '''Scan all available markets and choose one
    returns market indexed list'''
    # Get all markets
    current_market_list = get_market_list()
    counter = 0
    for i in current_market_list:
        print(counter, i['symbol'])
        counter += 1
    selected_market = input('Select Market to manipulate:')
    return selected_market


def list_my_all_open_orders():
    '''Print all open order on Exchange
    Checks for delisted BSV'''
    # Get my open exchange orders
    exchange_info = public_api.get_exchange_markets_info()
    print('My All Open Orders on Exchange:')
    for i in exchange_info['symbols']:
        if i['symbol'][:3] != 'BSV':  # BSV delisted!!!
            # need to submit status parameter (open) to get all current open orders
            my_exchange_orders = private_api.get_my_exchange_orders(
                i['symbol'], 'open')

            n = None
            try:
                n = my_exchange_orders[0]
                print('\n')
                print(i['symbol'])
            except:
                n = None

            for n in my_exchange_orders:  # n is a dictionary of trade order data
                print(n)


def get_latest_shift_advice(direction='buy'):
    """Refresh latest trade shift advice limit price and minimal amount

    Returns:
        [type] -- [description]
        edge_price - price advice
        edge_amount - amount, calculated to minimal trade size of 0.0001 BTC

    """
    # Refresh exchange info - do we really need it?
    exchange_info = public_api.get_exchange_markets_info()

    # Refresh exchange orderbook
    exchange_orderbook = public_api.get_exchange_orderbook(
        exchange_info['symbols'][int(current_market)]['symbol'], 5)  # number of last trades

    # last trade price, etc.
    # last_trade = public_api.get_exchange_last_trade(exchange_info['symbols'][int(current_market)]['symbol'])
    # last_price = last_trade[0]['price']  # Current (last) trade price

    if direction == 'buy':

        # calculate edge prices
        buy_edge_price = exchange_orderbook['buy'][0][0]
        # buy_edge_amount = exchange_orderbook['buy'][0][1]

        # Display BUY advice

        limit_price = round((buy_edge_price+0.00000001), 8)
        print(bc.OKGREEN+'B U Y advice:')

        # Calculate minimum trade size
        min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)
        print('\nLimit Price:\n'+bc.BOLD)
        print(limit_price, bc.ENDC)

        print(bc.OKGREEN+'\nAmount to BUY:\n'+bc.BOLD)
        print(min_trade_size)
        print(bc.ENDC)

    else:
        sell_edge_price = exchange_orderbook['sell'][0][0]
        # sell_edge_amount = exchange_orderbook['sell'][0][1]

        # Display SELL advice

        limit_price = round((sell_edge_price-0.00000001), 8)
        print(bc.WARNING+'S E L L advice:')

        # Calculate minimum trade size
        min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)

        print('\nLimit Price:\n'+bc.BOLD)
        print(limit_price, bc.ENDC)

        print(bc.WARNING+'\nAmount to SELL:\n'+bc.BOLD)
        print(min_trade_size)
        print(bc.ENDC)

    edge_price = limit_price
    edge_amount = min_trade_size

    return edge_price, edge_amount

def percentage(part, whole):
    return 100 * float(part)/float(whole)


# # #                              M A I N   P R O G R A M                            # # #
'''____________________________________________________________________________________'''


# clear screen
clear()

# EXCHANGE DATA
# Get exchange market info
#print ('\nGet exchange market info:')
exchange_info = public_api.get_exchange_markets_info()
# print(exchange_info)

# # Get my exchnage trades
# #my_exchange_trades = private_api.get_my_exchange_trades(exchange_info['symbols'][6]['symbol']) # LTC/BTC trades
# print('\nGet my exchnage trades')
# total_trades_amount = 0
# for i in exchange_info['symbols']:
#     if i['symbol'][:3] == 'LTC':
#         my_exchange_trades = private_api.get_my_exchange_trades(i['symbol'])
#         print(bc.OKGREEN+i['symbol']+bc.ENDC)
#         sumBTC = 0
#         print (my_exchange_trades)

#         if i['symbol'][:3] == 'BTC':#Check pri/sec pair of currencies
#             print(bc.FAIL+'BTC!!!'+bc.ENDC)
#             BTCpairFlag = True
#         else:
#             BTCpairFlag = False

#         for n in my_exchange_trades:
#             fee = n['fee']
#             price = n['price']
#             print('price:',)
#             print (price)
#             sndQty = n['sndQty']
#             print('sndQty:',)
#             print(sndQty)

#             if BTCpairFlag:# BTC is pri
#                 if n['dir'] == 'SELL':# checking order direction, if SELL then fee is in sec
#                     sumBTC = sndQty/price+fee/price+sumBTC
#                 else:# checking order direction, if BUY then fee is in pri
#                     sumBTC = sumBTC+sndQty/price+fee# calculate fee from exchange rate in BTC
#             else:# BTC is sec
#                 if n['dir'] == 'SELL':# checking order direction, if SELL then fee is in sec
#                     sumBTC = sumBTC+sndQty+fee
#                 else:# checking order direction, if BUY then fee is in pri
#                     sumBTC = sumBTC+sndQty+fee*price# calculate fee from exchange rate in BTC

#         print ('SUM:',sumBTC,"\n")
#         total_trades_amount = total_trades_amount + sumBTC
# print ('\n')
# print(bcolors.OKBLUE+str(total_trades_amount)+bcolors.ENDC)

# Get my fees and trade volume status
# GET /exchange/api/v2/info/fees/status
#print('Get my fees and trade volume status:')
my_fees_volume_status = private_api.get_my_fees()
# print(my_fees_volume_status)

# Get my current maker fee
my_current_maker_fee = my_fees_volume_status['makerCoefficient']
# Get my current taker fee
my_current_maker_fee = my_fees_volume_status['takerCoefficient']

# Get trades for LTC/BTC [6] market
# Calculate current minimal trade volume for given currency
# For your needs, you need to check the latest trades where you will also find the price:
# file_get_contents($url."trades?market=LTCBTC&limit=1");

print('\nLast trade for '+get_market_list()
      [int(current_market)]['symbol']+' market:')
last_trade = public_api.get_exchange_last_trade(
    exchange_info['symbols'][int(current_market)]['symbol'])  # [6] corresponds to ETH/BTC
last_price = last_trade[0]['price']  # Current (last) trade price
last_trade_direction = last_trade[0]['dir']  # BUY or SELL
if last_trade_direction == 'BUY':
    print(bc.OKGREEN)
else:
    print(bc.WARNING)
print(bc.BOLD, last_price, last_trade_direction)
print(bc.ENDC)
# calculate minimal trade size in pri currency

# shifting robots
if (last_trade_direction == 'BUY'):
    print(bc.OKGREEN+'Last Trade was BUY!!!'+bc.ENDC)
    # if last trade was BUY then my price is MORE than last trade price for 0.00000001
    limit_price = last_price+0.00000001
else:
    print(bc.WARNING+'Last Trade was SELL!!!'+bc.ENDC)
    # if last trade was BUY then my price is LESS than last trade price for 0.00000001
    limit_price = last_price-0.00000001

# # Calculate minimum trade size for the last order direction trend
# print(bc.Cyan+bc.BOLD+'')
# min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)
# print('Minimum Trade Size:')
# print(min_trade_size)
# print('My Limit Price:')
# print(limit_price)

print('\n')

while True:

    # BUY/SELL closing orders spread
    # Get exchange orderbook BUY/SELL spread range

    # Refresh exchange info - do we really need it?
    exchange_info = public_api.get_exchange_markets_info()

    #print ('\nGet exchange orderbook:')
    exchange_orderbook = public_api.get_exchange_orderbook(
        exchange_info['symbols'][int(current_market)]['symbol'], 5)  # number of last trades
    last_trade = public_api.get_exchange_last_trade(
        exchange_info['symbols'][int(current_market)]['symbol'])
    last_price = last_trade[0]['price']  # Current (last) trade price

    # print(exchange_orderbook)
    # print(current_market)
    print(bc.BOLD+'\nCurrent Market: ',
          exchange_info['symbols'][int(current_market)]['symbol'], '\n'+bc.ENDC)
    #print ('\n')

    refresh_my_exchange_orders = private_api.get_my_exchange_orders(
        exchange_info['symbols'][int(current_market)]['symbol'], 'open')

    my_order_data = list()
    for my_order in refresh_my_exchange_orders:
        # collect all Market Size, Price pairs in one list
        my_order_data.append([my_order['origQty'], my_order['price']])

    print('Market size\tPrice (BTC)\n')

    for i in reversed(exchange_orderbook['sell']):

        if str(i[0]) in [pair[1] for pair in my_order_data]:

            for pair in my_order_data:
                if pair[1] == str(i[0]):
                    my_order_size = pair[0]

            print("%08.8f" % i[1], '\t', bc.WARNING,
                  "%08.8f" % i[0], my_order_size, bc.ENDC)
        else:
            print("%08.8f" % i[1], '\t', bc.WARNING, "%08.8f" % i[0], bc.ENDC)

    print(bc.DARKGREY+'Last trade price ', "%08.8f" % last_price, bc.ENDC)

    for i in exchange_orderbook['buy']:

        if str(i[0]) in [pair[1] for pair in my_order_data]: # checking if my order price in the edge of the ordrebook

            for pair in my_order_data: # searching for order size corresponded to my order price
                if pair[1] == str(i[0]):
                    my_order_size = pair[0]
            order_to_market_ratio = percentage(my_order_size,i[1])

            print("%08.8f" % i[1], '\t', bc.OKGREEN,
                  "%08.8f" % i[0], my_order_size, "%05.2f" % order_to_market_ratio, '\t%'+bc.ENDC)
        else:
            print("%08.8f" % i[1], '\t', bc.OKGREEN, "%08.8f" % i[0], bc.ENDC)

    print('\n')

    buy_edge_price = exchange_orderbook['buy'][0][0]
    buy_edge_amount = exchange_orderbook['buy'][0][1]
    sell_edge_price = exchange_orderbook['sell'][0][0]
    sell_edge_amount = exchange_orderbook['sell'][0][1]

    # print(bc.BOLD+bc.WARNING+'Sell amount:\t', sell_edge_amount)
    # print(bc.ENDC+bc.WARNING+'Sell price:\t', sell_edge_price)

    # print(bc.DARKGREY+'Exchange Rate:\t', last_price)

    # print(bc.OKGREEN+'Buy price:\t', buy_edge_price)
    # print(bc.OKGREEN+bc.BOLD+'Buy amount:\t', buy_edge_amount)

    # print(bc.ENDC)

    # print(bc.WARNING, sell_edge_amount, '\t', sell_edge_price, bc.ENDC)

    # print(bc.DARKGREY+'Exchange Rate:\t', last_price, bc.ENDC)

    # print(bc.OKGREEN, buy_edge_amount, '\t', buy_edge_price, bc.ENDC)

    sell_or_buy = input(
        'Buy(1) | Sell(2) | Shift BUY Robots(3) | Shift SELL Robots(4) | My Open Orders(5) | Select Market(6) | Select Manual Order Size(7) | Quit(q)? ')

    clear()

    if sell_or_buy == 'q':  # Quit program
        exit()

    if sell_or_buy == '1':  # Display BUY advice

        limit_price = round((buy_edge_price+0.00000001), 8)
        print(bc.OKGREEN+'B U Y advice:')

        # Calculate minimum trade size
        min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)
        print('\nLimit Price:\n'+bc.BOLD)
        print("%08.8f" % limit_price, bc.ENDC)

        print(bc.OKGREEN+'\nAmount to BUY:\n'+bc.BOLD)
        print("%08.8f" % min_trade_size)
        print(bc.ENDC)

    elif sell_or_buy == '2':  # Display SELL advice
        limit_price = round((sell_edge_price-0.00000001), 8)
        print(bc.WARNING+'S E L L advice:')

        # Calculate minimum trade size
        min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)

        print('\nLimit Price:\n'+bc.BOLD)
        print("%08.8f" % limit_price, bc.ENDC)

        print(bc.WARNING+'\nAmount to SELL:\n'+bc.BOLD)
        print("%08.8f" % min_trade_size)
        print(bc.ENDC)

    elif sell_or_buy == '3':  # Making Robot Shifting Orders SELL
        # Do orders
        # Cancel previous exchange order

        # refresh latest trade date and advice calculations
        limit_price, min_trade_size = get_latest_shift_advice('buy')
        if manual_order_size:
            min_trade_size = manual_order_size
        # print (limit_price)
        # print (min_trade_size)

        if 'my_exchange_orders' in globals():  # Check that previous order was created programmatically
            cancelled_order = private_api.cancel_exchange_order(exchange_info['symbols'][int(
                current_market)]['symbol'], my_exchange_orders[0]['orderId'])
            print('Previous Order Cancelled:'+bc.Magenta)
            print("%08.8f" % cancelled_order['origQty'],
                  '\t', "%08.8f" % cancelled_order['price'])
            print(bc.ENDC)

        # # Create minimal sell limit exchange shift order
        new_buy_limit_order = private_api.create_exchange_limit_order(
            exchange_info['symbols'][int(current_market)]['symbol'], 'buy', min_trade_size, limit_price)
        print('Creating new Shift BUY Order:'+bc.Magenta)
        print("%08.8f" % new_buy_limit_order['origQty'],
              '\t', "%08.8f" % new_buy_limit_order['price'])
        print(bc.ENDC)

        # Get my exchange orders to cancel latest one in the begining
        my_exchange_orders = private_api.get_my_exchange_orders(
            exchange_info['symbols'][int(current_market)]['symbol'], 'open')
        # print (my_exchange_orders)
        # print ('\n')

        # wait = input('Hit Enter to continue:') # pause execution till user hit Enter key

    elif sell_or_buy == '4':  # Making Robot Shifting Orders BUY
        pass
        # # Create buy limit exchange order
        # new_sell_limit_order = private_api.create_exchange_limit_order(exchange_info['symbols'][0]['symbol'], 'sell', 10, 0.1)
        # print (new_sell_limit_order)
        # print('\n')

    elif sell_or_buy == '5':  # List all my Open Orders
        list_my_all_open_orders()
    elif sell_or_buy == '6':  # Select coin
        current_market = market_select()
    elif sell_or_buy == '7':  # Select Order size manually
        manual_order_size = input('Enter order size:')
    else:
        exit()

# # Create buy limit exchange order
# new_sell_limit_order = private_api.create_exchange_limit_order(exchange_info['symbols'][0]['symbol'], 'sell', 10, 0.1)
# print (new_sell_limit_order)
# print ('\n')

# # Create sell limit exchange order
# new_buy_limit_order = private_api.create_exchange_limit_order(exchange_info['symbols'][0]['symbol'], 'buy', 0.1, 0.1)
# print (new_buy_limit_order)
# print ('\n')

# # Cancel exchange order
# cancelled_order = private_api.cancel_exchange_order(exchange_info['symbols'][0]['symbol'], my_exchange_orders[0]['orderId'])
# print(cancelled_order)
# print ('\n')
