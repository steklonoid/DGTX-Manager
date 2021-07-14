from threading import Thread
import websocket
import json
import time


class WSSCore(Thread):
    def __init__(self, pc):
        super(WSSCore, self).__init__()
        self.flClosing = False
        self.pc = pc
        self.flConnect = False
        self.flAuth = False

    def run(self) -> None:
        def on_open(wsapp):
            print('open')
            self.pc.statusbar.showMessage('Соединение с сервером установлено')
            self.flConnect = True

        def on_close(wsapp, close_status_code, close_msg):
            print('close')
            self.flConnect = False
            self.flAuth = False
            self.pc.change_auth_status()

        def on_error(wsapp, error):
            print('error')
            self.pc.statusbar.showMessage('Ошибка соединения с сервером')
            self.flConnect = False
            self.flAuth = False
            self.pc.change_auth_status()
            time.sleep(1)

        def on_message(wssapp, message):
            print(message)
            message = json.loads(message)
            id = message.get('id')
            message_type = message.get('message_type')
            data = message.get('data')
            if message_type == 'registration':
                status = data.get('status')
                if status == 'ok':
                    self.flAuth = True
                else:
                    self.flAuth = False
                self.pc.change_auth_status()
            elif message_type == 'cm':
                command = data.get('command')
                if command == 'getrockets':
                    rockets_data = data.get('rockets')
                    self.pc.cm_getrockets(rockets_data)
                elif command == 'getmanagers':
                    managers_data = data.get('managers')
                    self.pc.cm_getmanagers(managers_data)
                elif command == 'getpilot':
                    pilot_data = data.get('pilot')
                    self.pc.cm_getpilot(pilot_data)
                else:
                    pass
            else:
                pass

        while not self.flClosing:
            try:
                self.pc.statusbar.showMessage('Устанавливаем соединение с сервером')
                self.wsapp = websocket.WebSocketApp("ws://localhost:6789", on_open=on_open,
                                                               on_close=on_close, on_error=on_error, on_message=on_message)
                self.wsapp.run_forever()
            except:
                pass
            finally:
                time.sleep(1)

    def authpilot(self, name, rocket_id):
        data = {'command': 'authpilot', 'pilot': name, 'rocket': rocket_id}
        self.send_mc(data)

    def getinfo(self):
        data = {'command': 'getrockets'}
        self.send_mc(data)
        data = {'command': 'getpilots'}
        self.send_mc(data)
        data = {'command': 'getmanagers'}
        self.send_mc(data)
        data = {'command': 'getraces'}
        self.send_mc(data)

    def setparameters(self):
        data = {'command': 'setparameters', }

    def send_registration(self, user, psw):
        str = {'id': 1, 'message_type': 'registration', 'data': {'typereg': 'manager', 'user': user, 'psw': psw}}
        str = json.dumps(str)
        self.wsapp.send(str)

    def send_mc(self, data):
        str = {'id':10, 'message_type':'mc', 'data':data}
        str = json.dumps(str)
        self.wsapp.send(str)


class Worker(Thread):
    def __init__(self, f, data):
        super(Worker, self).__init__()
        self.f = f
        self.data = data

    def run(self) -> None:
        while True:
            self.f(self.data)
