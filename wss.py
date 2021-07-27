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
            # print(message)
            message = json.loads(message)
            message_type = message.get('message_type')
            data = message.get('data')
            if message_type == 'cm':
                command = data.get('command')
                if command == 'cm_registration':
                    status = data.get('status')
                    if status == 'ok':
                        self.flAuth = True
                    else:
                        self.flAuth = False
                    self.pc.change_auth_status()
                elif command == 'cm_rocketinfo':
                    rocket_id = data.get('rocket')
                    self.pc.cm_rocketinfo(rocket_id)
                elif command == 'cm_rocketdelete':
                    rocket_id = data.get('rocket')
                    self.pc.cm_rocketdelete(rocket_id)
                elif command == 'cm_pilotinfo':
                    pilot = data.get('pilot')
                    info = data.get('info')
                    self.pc.cm_pilotinfo(pilot, info)
                elif command == 'cm_managersinfo':
                    managers_data = data.get('managers')
                    self.pc.cm_managersinfo(managers_data)
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

    def mc_authpilot(self, name, rocket_id):
        data = {'command': 'mc_authpilot', 'pilot': name, 'rocket': rocket_id}
        self.send_mc(data)

    def mc_setparameters(self):
        data = {'command': 'mc_setparameters'}
        self.send_mc(data)

    def mc_registration(self, user, psw):
        data = {'command': 'mc_registration', 'user': user, 'psw': psw}
        self.send_mc(data)

    def send_mc(self, data):
        str = {'message_type':'mc', 'data':data}
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
