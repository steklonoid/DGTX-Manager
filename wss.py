from threading import Thread
import websocket
import json
import time
from PyQt5.QtCore import QThread


class WSSCore(Thread):
    def __init__(self, pc, q):
        super(WSSCore, self).__init__()
        self.flClosing = False
        self.pc = pc
        self.q = q
        self.flConnect = False

    def run(self) -> None:
        def on_open(wsapp):
            print('open')
            self.pc.statusbar.showMessage('Соединение с сервером установлено')
            self.flConnect = True

        def on_close(wsapp, close_status_code, close_msg):
            print('close')
            self.flConnect = False

        def on_error(wsapp, error):
            print('error')
            self.pc.statusbar.showMessage('Ошибка соединения с сервером')
            self.flConnect = False
            time.sleep(1)

        def on_message(wssapp, message):
            # print(message)
            message = json.loads(message)
            message_type = message.get('message_type')
            data = message.get('data')
            if message_type == 'cm':
                self.q.put(data)
            else:
                pass

        while not self.flClosing:
            try:
                self.pc.statusbar.showMessage('Устанавливаем соединение с сервером')
                self.wsapp = websocket.WebSocketApp("ws://185.59.100.235:16789", on_open=on_open,
                                                               on_close=on_close, on_error=on_error, on_message=on_message)
                self.wsapp.run_forever()
            except:
                pass
            finally:
                time.sleep(1)

    def mc_authpilot(self, name, rocket_id):
        data = {'command': 'mc_authpilot', 'pilot': name, 'rocket': rocket_id}
        self.send_mc(data)

    def mc_setparameters(self, rocket_id, parameters):
        data = {'command': 'mc_setparameters', 'rocket':rocket_id, 'parameters':parameters}
        self.send_mc(data)

    def mc_registration(self, user, psw):
        data = {'command': 'mc_registration', 'user': user, 'psw': psw}
        self.send_mc(data)

    def send_mc(self, data):
        str = {'message_type':'mc', 'data':data}
        str = json.dumps(str)
        self.wsapp.send(str)


class Worker(Thread):
    def __init__(self, f, q):
        super(Worker, self).__init__()
        self.f = f
        self.q = q

    def run(self) -> None:
        while True:
            data = self.q.get()
            self.f(data)

