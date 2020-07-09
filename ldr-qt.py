import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QAction
from PySide2.QtCore import QFile
from PySide2.QtGui import QKeySequence
from PySide2.QtUiTools import QUiLoader
import nicehash
from bcolors import bcolors as bc
from ldr import convert_time, form
from ldr_ui import MainWindow
from ldr_widget import Widget
# from ldr import list_my_all_open_orders # ToDo - need to make this function universal

# import account related keys for sign operations purposes
from keys import host, organisation_id, secret, key


def array_2_table(self, array, qtable):
    qtable.setColumnCount(10)
    qtable.setRowCount(600)
    for row in range(600):
        for column in range(10):
            qtable.setItem(row, column, QTableWidgetItem(
                QString("%1").arg(array[row][column])))


def read_data(orders_dict):  # makes a tuple as pairs of symbol:origQty
    for i in range(0, len(orders_dict)):


        
        if type(orders_dict[i]) == str:
            symbol = orders_dict[i]
            data_field = orders_dict[i+1]['origQty']  # ['origQty'] # debug
            print(symbol, ': ', data_field)  # debug
            return symbol, data_field
        else:
            data_field = orders_dict[i]['origQty']
            print(symbol, ': ', data_field)  # debug
            return symbol, data_field

            # add as first tuple element for my open orders
        # print(i)
        # if type(i) == dict: # str for symbol pairs, dict for order dict data 'Submit Time\t\t Last Response Time\t Type\t Dir\t origQty\t origSndQty\t executedQty\t executedSndQty\t price\t\t state'
        # print(i) # debug


if __name__ == "__main__":

    # options = argparse.ArgumentParser()
    # options.add_argument("-f", "--file", type=str, required=True)
    # args = options.parse_args()
    # data = read_data(args.file)
    # we do not require cl argumanets atm

    # Qt Application
    app = QApplication(sys.argv)

    # Create Nicehash private api object
    private_api = nicehash.private_api(
        host, organisation_id, key, secret, False)

    # Create public api object
    public_api = nicehash.public_api(host, False)

    '''Print all open order on Exchange
    Checks for delisted BSV'''
    # Get my open exchange orders
    exchange_info = public_api.get_exchange_markets_info()

    print('My All Open Orders on Exchange:\n')

    my_open_orders = []
    # {'symbol': 'BTC', 'open_orders': {'Submit Time': '0', 'Last Response Time': '0', 'Type': 'LIMIT', 'Dir': 'SELL', 'origQty': '0', 'origSndQty': '0', 'executedQty': '0', 'executedSndQty': '0', 'price': '0', 'state': 'ENTERED'}}

    for i in exchange_info['symbols']:
        if i['symbol'][:3] != 'BSV':  # BSV delisted!!!
            # need to submit status parameter (open) to get all current open orders
            my_exchange_orders = private_api.get_my_exchange_orders(
                i['symbol'], 'open')

            n = None
            try:
                n = my_exchange_orders[0]
                my_open_orders.append(i['symbol'])
                # print('\n', i['symbol'])
                # Table header
                # print('Submit Time\t\t Last Response Time\t Type\t Dir\t origQty\t origSndQty\t executedQty\t executedSndQty\t price\t\t state')
            except:
                n = None

            for n in my_exchange_orders:  # n is a dictionary of trade order data
                # if n['side'] == 'BUY':
                #     print(bc.OKGREEN, end='')  # Green for BUY
                # else:
                #     print(bc.WARNING, end='')  # Red for SELL

                # print(convert_time(n['submitTime']), '\t', convert_time(n['lastResponseTime']), '\t', n['type'], '\t', n['side'], '\t',
                #   form(n['origQty']), '\t', form(n['origSndQty']), '\t', form(n['executedQty']), '\t', form(n['executedSndQty']), '\t', form(n['price']), '\t', n['state'], bc.ENDC)

                # push data to dictionary
                my_open_orders.append({'Submit Time': convert_time(n['submitTime']), 'Last Response Time': convert_time(n['lastResponseTime']), 'Type': n['type'], 'Dir': n['side'], 'origQty': form(
                    n['origQty']), 'origSndQty': form(n['origSndQty']), 'executedQty': form(n['executedQty']), 'executedSndQty': form(n['executedSndQty']), 'price': form(n['price']), 'state': n['state']})

    for i in my_open_orders:
        if type(i) == chr:
            # add as first tuple element for my open orders
            print(i)
        # if type(i) == dict: # str for symbol pairs, dict for order dict data 'Submit Time\t\t Last Response Time\t Type\t Dir\t origQty\t origSndQty\t executedQty\t executedSndQty\t price\t\t state'
        # print(i) # debug

    # print(bc.ENDC, my_open_orders)

    data = read_data(my_open_orders)

    print(data) # debug

    widget = Widget(data)
    window = MainWindow(widget)
    window.show()

    sys.exit(app.exec_())
