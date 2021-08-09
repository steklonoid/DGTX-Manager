from threading import Thread
import websocket
import json
import time


class WSSClient(Thread):
    def __init__(self, q, address):
        super(WSSClient, self).__init__()
        self.q = q
        self.address = address
        self.flConnect = False
        self.flClosing = False

    def run(self) -> None:
        def on_open(wsapp):
            self.flConnect = True
            data = {'command':'on_open'}
            self.q.put(data)

        def on_close(wsapp, close_status_code, close_msg):
            self.flConnect = False

        def on_message(wssapp, message):
            data = json.loads(message)
            self.q.put(data)

        while not self.flClosing:
            try:
                self.wsapp = websocket.WebSocketApp(self.address, on_open=on_open,
                                                               on_close=on_close, on_message=on_message)
                self.wsapp.run_forever()
            except:
                pass
            finally:
                time.sleep(1)

    def send(self, data):
        str = json.dumps(data)
        self.wsapp.send(str)


class FromQToF(Thread):

    def __init__(self, f, q):
        super(FromQToF, self).__init__()
        self.f = f
        self.q = q

    def run(self) -> None:
        while True:
            data = self.q.get()
            self.f(data)