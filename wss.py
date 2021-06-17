from threading import Thread
import websocket
import json
import time
import logging


class WSSClient(Thread):
    def __init__(self, pc):
        super(WSSClient, self).__init__()
        self.flClosing = False
        self.pc = pc

    def run(self) -> None:
        def on_open(wsapp):
            print('open')
            str = {'id':2, 'message_type':'registration', 'params':{'typereg':'manager'}}
            self.senddata(str)

        def on_close(wsapp, close_status_code, close_msg):
            print('close')

        def on_error(wsapp, error):
            print('error')

        def on_message(wssapp, message):
            message = json.loads(message)
            message_type = message.get('message_type')
            data = message.get('data')
            if message_type == 'getrocketslist':
                self.pc.getrocketslist(data)
            elif message_type == 'getpilotslist':
                self.pc.getpilotslist(data)
            elif message_type == 'getraceslist':
                self.pc.getraceslist(data)
            else:
                pass


        while not self.flClosing:
            try:
                self.wsapp = websocket.WebSocketApp("ws://localhost:6789", on_open=on_open,
                                                               on_close=on_close, on_error=on_error, on_message=on_message)
                self.wsapp.run_forever()
            except:
                pass
            finally:
                time.sleep(1)

    def senddata(self, data):
        data = json.dumps(data)
        self.wsapp.send(data)


class Worker(Thread):
    def __init__(self, f, data):
        super(Worker, self).__init__()
        self.f = f
        self.data = data

    def run(self) -> None:
        while True:
            self.f(self.data)
