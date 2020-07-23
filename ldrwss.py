from datetime import datetime
from time import mktime, sleep
import uuid
import hmac
import json
import ast
from hashlib import sha256
# import optparse
import sys
import requests
# # QT
# from PySide2.QtWidgets import QApplication, QLabel, QPushButton
# from PySide2.QtQuick import QQuickView
# from PySide2.QtCore import QUrl, Slot
# import account related keys for sign operations
from keys import host, organisation_id, secret, key
# websocket
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
from bcolors import bcolors as bc

# NiceHash web-socket
# The base endpoint is: wss://exchange-<market>-ws.nicehash.com

# MESSAGES:
""" Subscribe to orderbook channel
{"m":"subscribe.orderbook"}
Unsubscribe to orderbook channel
{"m":"unsubscribe.orderbook"}

Subscribe to trades channel
{"m":"subscribe.trades"}
Unsubscribe to trades channel
{"m":"unsubscribe.trades"}

Subscribe to mytrades channel - stream requires to be signed. Push my trade information; each trade has a unique buyer and seller.
{"m":"subscribe.mytrades"}
Unsubscribe to mytrades channel
{"m":"unsubscribe.mytrades"}

Subscribe to orders channel - stream requires to be signed.
{"m":"subscribe.orders"}
Unsubscribe to orders channel
{"m":"unsubscribe.orders"}

Subscribe to candlesticks channel
{"m":"subscribe.candlesticks", "r": resolution}
Unsubscribe to candlesticks channel
{"m":"unsubscribe.candlesticks"}

Subscribe to trade statistics channel
{"m":"subscribe.statistics"}
Unsubscribe to statistics channel
{"m":"unsubscribe.statistics"} """


class private_api:

    def __init__(self, host, organisation_id, key, secret, verbose=False):
        self.key = key
        self.secret = secret
        self.organisation_id = organisation_id
        self.host = host
        self.verbose = verbose

    # Subscribe to channel
    def wss_request(self):

        # X-Time: 1560162680789 (current UTC time in ms)
        xtime = self.get_epoch_ms_from_now()
        # X-Nonce: 8279fb4e-d9da-43b4-899e-b10a7ce81a80 (generate some random string, for example: UUID.randomUUID().toString(), must be different each time you sign a request)
        xnonce = str(uuid.uuid4())

        # API Key: 787ba136-c1bc-4684-a215-69f8d86a1300 (received when API Key is generated at API Keys)
        message = bytearray(self.key, 'utf-8')
        message += bytearray('\x00', 'utf-8')  # ⊠

        # X-Time: 1560162680789 (current UTC time in ms)
        message += bytearray(str(xtime), 'utf-8')
        message += bytearray('\x00', 'utf-8')  # ⊠

        # X-Nonce: 8279fb4e-d9da-43b4-899e-b10a7ce81a80 (generate some random string, for example: UUID.randomUUID().toString(), must be different each time you sign a request)
        message += bytearray(xnonce, 'utf-8')
        message += bytearray('\x00', 'utf-8')  # ⊠
        message += bytearray('\x00', 'utf-8')  # ⊠

        # X-Organization-Id: cd005e9a-dbc5-430c-a10c-3359c5fa5184
        message += bytearray(self.organisation_id, 'utf-8')
        message += bytearray('\x00', 'utf-8')  # ⊠
        message += bytearray('\x00', 'utf-8')  # ⊠

        # Method: wss
        message += bytearray('wss', 'utf-8')
        message += bytearray('\x00', 'utf-8')  # ⊠

        # Path: my
        message += bytearray('my', 'utf-8')
        message += bytearray('\x00', 'utf-8')  # ⊠

        # Input for signing: 787ba136-c1bc-4684-a215-69f8d86a1300 ⊠ 1560162680789 ⊠ 8279fb4e-d9da-43b4-899e-b10a7ce81a80 ⊠ ⊠ cd005e9a-dbc5-430c-a10c-3359c5fa5184 ⊠ ⊠ wss ⊠ my ⊠

        # Signature is generated via HMAC-SHA256 (input, API_SECRET): e8e360f598c15115c2dc324966fcb24244135d7d9cba0dfb2fde041083f6ea1c
        # !!! input, API_SECRET or API_SECRET, input???
        digest = hmac.new(bytearray(self.secret, 'utf-8'),
                          message, sha256).hexdigest()
        # Create X-Auth: API_KEY:SIGNATURE -> 787ba136-c1bc-4684-a215-69f8d86a1300:e8e360f598c15115c2dc324966fcb24244135d7d9cba0dfb2fde041083f6ea1c
        xauth = self.key + ":" + digest

        # Pass query string parameters:
        # wss://exchange-tzectbtc-ws.nicehash.com/                           URL
        # ?a=787ba136-c1bc-4684-a215-69f8d86a1300                           API_KEY
        # :
        # e8e360f598c15115c2dc324966fcb24244135d7d9cba0dfb2fde041083f6ea1c  SIGNATURE
        # &t=1560162680789                                                  TIME
        # &n=8279fb4e-d9da-43b4-899e-b10a7ce81a80                           NONCE
        # &o=cd005e9a-dbc5-430c-a10c-3359c5fa5184                           ORG-ID

        return xauth, xtime, xnonce, organisation_id

        # Do NOT include a plain text API Secret in any of the parameters of your request. A novice software developer might mistakenly put an API Secret into the second part of X-Auth header value.

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(
            now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)


def on_message(ws, message):
    # main subscription parser
    # Manage OrderBook Stream:
    m_dict = ast.literal_eval(message)
    if m_dict['m'] == 'ob.s':
        # table while we implement windows later
        print ()
        print(bc.BOLD+bc.OKGREEN+'\tBuy'+bc.ENDC+'\t\t\t\t\t' +
              bc.BOLD+bc.WARNING+'Sell'+bc.ENDC)  # header
        
        buy_sell_list = list(zip(reversed(m_dict['b']), reversed(m_dict['s'])))

        for (b, s) in buy_sell_list:
            formatted_output(b, s)

    if m_dict['m'] == 'ob.u':
        print('_______________________________________________________')
        # print(m_dict['b'], m_dict['s']) # debug
        b = m_dict['b']
        s = m_dict['s']
        formatted_output(b, s)
        # print('buy:',b,'sell:',s)  # debug


def formatted_output(b, s):
    # print('buy, sell: ',b,s) # debug
    if len(b) == 2 and len(s) == 2:
        print(bc.OKGREEN, "%08.8f" % b[0], "%08.8f" %
              b[1], bc.ENDC, end='\t\t\t')  # buy pairs
        print(bc.WARNING, "%08.8f" %
              s[0], "%08.8f" % s[1], bc.ENDC)  # sell pairs
    elif len(b) == 0:  # If no Buy data -> print Sell data
        print(bc.WARNING, "%08.8f" %
              s[0][0], "%08.8f" % s[0][1], bc.ENDC)  # sell pairs
    elif len(s) == 0:  # If no Sell data -> print Buy data
        print(bc.OKGREEN, "%08.8f" % b[0][0], "%08.8f" %
              b[0][1], bc.ENDC)  # buy pairs


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        # ws.send('{"m":"subscribe.orderbook"}')
        ws.send('{"m":"subscribe.orderbook"}')
        sleep(1000)  # listening for messages for 10 seconds
        ws.send('{"m":"unsubscribe.orderbook"}')
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    my_wss_xauth = private_api(host, organisation_id, key, secret, False)
    xauth, xtime, xnonce, xorg = my_wss_xauth.wss_request()
    # print(my_wss_xauth)  # debug
    ws = websocket.WebSocketApp("wss://exchange-ethbtc-ws.nicehash.com/?a="+xauth+'&t='+str(xtime)+'&n='+xnonce+'&o='+xorg,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
