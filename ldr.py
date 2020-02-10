import nicehash
import json
from bcolors import bcolors as bc
# from tabulate import tabulate
from datetime import datetime

# import only system from os
from os import system, name

# import sleep to show output for some time period
from time import sleep

# import account related keys for sign operations
from keys import host, organisation_id, secret, key

BTCpairFlag = False  # Pair Flag for BTC is sec = False, pri = True
MIN_BTC_TRADE = 0.0001  # minimal BTC trade size
current_market = 12  # ETHBTC by default
current_market_name = 'ETHBTC'
manual_order_size = None  # Automatical calculation

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
    selected_market = input('Select Market: ')
    selected_market_name = current_market_list[int(selected_market)]['symbol']
    return selected_market, selected_market_name


def list_my_all_open_orders():
    '''Print all open order on Exchange
    Checks for delisted BSV'''
    # Get my open exchange orders
    exchange_info = public_api.get_exchange_markets_info()
    print('My All Open Orders on Exchange:\n')
    for i in exchange_info['symbols']:
        if i['symbol'][:3] != 'BSV':  # BSV delisted!!!
            # need to submit status parameter (open) to get all current open orders
            my_exchange_orders = private_api.get_my_exchange_orders(
                i['symbol'], 'open')

            n = None
            try:
                n = my_exchange_orders[0]
                print('\n',i['symbol'])
                # Table header
                print('Submit Time\t\t Last Response Time\t Type\t Dir\t origQty\t origSndQty\t executedQty\t executedSndQty\t price\t\t state')
            except:
                n = None

            for n in my_exchange_orders:  # n is a dictionary of trade order data
                print(convert_time(n['submitTime']), '\t', convert_time(n['lastResponseTime']), '\t', n['type'], '\t', n['side'], '\t',
                      form(n['origQty']), '\t', form(n['origSndQty']), '\t', form(n['executedQty']), '\t', form(n['executedSndQty']), '\t', form(n['price']), '\t', n['state'])



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


def convert_time(time_to_convert):
    """Converts Nicehash Unix-like time stamp to dd-mm-YYYY HH:MM:SS format

    Arguments:
        time_to_convert {[string Nicehash Unix timestamp]} -- [Nicehash Unix-like timestamp]

    Returns:
        [String] -- [date and time dd-mm-YYYY HH:MM:SS]
    """
    return datetime.utcfromtimestamp(int(time_to_convert)/1000000).strftime('%d-%m-%Y %H:%M:%S')


def form(amount):
    return "%08.8f" % float(amount)


def sell_buy_routine():
    global buy_edge_price
    global buy_edge_amount
    global sell_edge_price
    global sell_edge_amount
    global exchange_info
    global limit_price

    exchange_info = public_api.get_exchange_markets_info()
    print('\nLast trade for '+get_market_list()
          [int(current_market)]['symbol']+' market:', end=' ')
    last_trade = public_api.get_exchange_last_trade(
        exchange_info['symbols'][int(current_market)]['symbol'])
    last_price = last_trade[0]['price']  # Current (last) trade price
    last_trade_direction = last_trade[0]['dir']  # BUY or SELL
    if last_trade_direction == 'BUY':
        print(bc.OKGREEN, end=' ')
    else:
        print(bc.WARNING, end=' ')
    print(bc.BOLD, last_price, last_trade_direction, bc.ENDC)
    # calculate minimal trade size in pri currency

    # shifting robots recomendations
    if (last_trade_direction == 'BUY'):
        print(bc.OKGREEN+'\nLast Trade was BUY!!!'+bc.ENDC)
        # if last trade was BUY then my price is MORE than last trade price for 0.00000001
        limit_price = last_price+0.00000001
    else:
        print(bc.WARNING+'\nLast Trade was SELL!!!'+bc.ENDC)
        # if last trade was BUY then my price is LESS than last trade price for 0.00000001
        limit_price = last_price-0.00000001

    # # Calculate minimum trade size for the last order direction trend
    # print(bc.Cyan+bc.BOLD+'')
    # min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)
    # print('Minimum Trade Size:')
    # print(min_trade_size)
    # print('My Limit Price:')
    # print(limit_price)

    # BUY/SELL closing orders spread
    # Get exchange orderbook BUY/SELL spread range

    # Refresh exchange info - do we really need it?
    exchange_info = public_api.get_exchange_markets_info()

    # print ('\nGet exchange orderbook:')
    exchange_orderbook = public_api.get_exchange_orderbook(
        exchange_info['symbols'][int(current_market)]['symbol'], 5)  # number of last trades

    last_trade = public_api.get_exchange_last_trade(
        exchange_info['symbols'][int(current_market)]['symbol'])

    last_price = last_trade[0]['price']  # Current (last) trade price

    # print(exchange_orderbook)
    # print(current_market)
    print(bc.BOLD+'\nCurrent Market: ',
          exchange_info['symbols'][int(current_market)]['symbol'], '\n'+bc.ENDC)
    # print ('\n')

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

        # checking if my order price in the edge of the ordrebook
        if str(i[0]) in [pair[1] for pair in my_order_data]:

            for pair in my_order_data:  # searching for order size corresponded to my order price
                if pair[1] == str(i[0]):
                    my_order_size = pair[0]
            order_to_market_ratio = percentage(my_order_size, i[1])

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


# # #                              M A I N   P R O G R A M                            # # #
'''____________________________________________________________________________________'''


# clear screen
clear()

# EXCHANGE DATA
# Get exchange market info
# print ('\nGet exchange market info:')

# print(exchange_info)
current_market_list = get_market_list()  # get list of all markets


# Get my fees and trade volume status
# GET /exchange/api/v2/info/fees/status
# print('Get my fees and trade volume status:')
my_fees_volume_status = private_api.get_my_fees()
# print(my_fees_volume_status)

# Get my current maker fee
my_current_maker_fee = my_fees_volume_status['makerCoefficient']
# Get my current taker fee
my_current_maker_fee = my_fees_volume_status['takerCoefficient']

while True:

    sell_or_buy = input(
        '\nBuy(1) | Sell(2) | Shift BUY Robots(3) | Shift SELL Robots(4) | My Open Orders(5) | Select Market(6) | Select Manual Order Size(7) | My Trades(8) | Quit(q)? ')

    clear()

    if sell_or_buy == 'q':  # Quit program
        exit()

    if sell_or_buy == '1':  # Display BUY advice

        sell_buy_routine()

        limit_price = round((buy_edge_price+0.00000001), 8)
        print(bc.OKGREEN+'B U Y advice:')

        # Calculate minimum trade size
        min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)
        print('\nLimit Price: '+bc.BOLD+"%08.8f" % limit_price, bc.ENDC)

        print(bc.OKGREEN+'\nAmount to BUY: '+bc.BOLD+"%08.8f" % min_trade_size)
        print(bc.ENDC)

    elif sell_or_buy == '2':  # Display SELL advice
        sell_buy_routine()

        limit_price = round((sell_edge_price-0.00000001), 8)
        print(bc.WARNING+'S E L L advice:')

        # Calculate minimum trade size
        min_trade_size = round(MIN_BTC_TRADE/limit_price, 8)

        print('\nLimit Price: '+bc.BOLD+"%08.8f" % limit_price, bc.ENDC)

        print(bc.WARNING+'Amount to SELL: '+bc.BOLD+"%08.8f" % min_trade_size)
        print(bc.ENDC)

    elif sell_or_buy == '3':  # Making Robot Shifting Orders SELL
        # Do orders
        # Cancel previous exchange order

        # refresh latest trade date and advice calculations
        limit_price, min_trade_size = get_latest_shift_advice('buy')
        if manual_order_size:
            min_trade_size = manual_order_size
        manual_order_size = None  # drop manual order size for automation
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
    elif sell_or_buy == '6':  # Select trade pair
        current_market, current_market_name = market_select()
    elif sell_or_buy == '7':  # Select Order size manually
        manual_order_size = input('Enter order size:')
    elif sell_or_buy == '8':
        # list my trades from history for specified pair
        # current_market = market_select() select or not select here?
        # # Get my exchnage trades

        total_fees_paid = 0  # initialize fee totals calculations
        total_trade_profit_loses = 0

        my_exchange_trades = private_api.get_my_exchange_trades(
            exchange_info['symbols'][int(current_market)]['symbol'], -1)  # -1 for all orders

        print(bc.BOLD+bc.Magenta, 'My Trades on ',
              current_market_name, ' market:\n'+bc.ENDC)

        print(' Date Time\t\t Dir\t Price\t\t qty\t\t sndQty\t\t fee')

        for i in reversed(my_exchange_trades):
            if i['dir'] == 'SELL':
                highlight_color = bc.WARNING
                total_fees_paid += float(i['fee'])  # fee in primary currency
                # (+) if we get BTC
                total_trade_profit_loses += float(i['price'])*float(i['qty'])
            else:  # BUY
                highlight_color = bc.OKGREEN
                # fee in secondary currency
                total_fees_paid += float(i['fee'])*float(i['price'])
                total_trade_profit_loses += - \
                    float(i['price'])*float(i['qty'])  # (-) if we spend BTC

            print(highlight_color, convert_time(i['time']), '\t', i['dir'], '\t',
                  "%08.8f" % i['price'], '\t', "%08.8f" % i['qty'], '\t', "%08.8f" % i['sndQty'], '\t', "%08.8f" % i['fee'], bc.ENDC)

        print(bc.Magenta+bc.BOLD+'\n Total fees paid: ',
              "%08.8f" % total_fees_paid, ' BTC\n\n Total profit(+)/loses(-): ', "%08.8f" % float(total_trade_profit_loses-total_fees_paid), ' BTC'+bc.ENDC)
        # print (my_exchange_trades)
        # print ('\n')
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
