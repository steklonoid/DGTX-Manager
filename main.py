import sys
import queue
import logging
import datetime

from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QCursor, QFont
from PyQt5.QtCore import QSettings, pyqtSlot, Qt
from mainWindow import UiMainWindow
from loginWindow import LoginWindow
from wssclient import WSSClient, FromQToF
from threading import Lock
import json


class MainWindow(QMainWindow, UiMainWindow):

    settings = QSettings("./config.ini", QSettings.IniFormat)
    serveraddress = settings.value('serveraddress')
    serverport = settings.value('serverport')

    version = '1.2.1'
    lock = Lock()

    flConnect = False           #   флаг нормального соединения с сайтом
    pilotscodes = {0:'Отдыхает', 1:'Готов к вылету', 2:'Неверны ключ'}

    flAuth = False

    pilots_parameters = {}
    current_pilot = None
    current_row = None
    last_row = None

    parameters = {}

    def __init__(self):

        super().__init__()
        logging.basicConfig(filename='info.log', level=logging.INFO, format='%(asctime)s %(message)s')

        # создание визуальной формы
        self.setupui(self)
        self.show()

        self.m_managers = QStandardItemModel()
        self.lv_managers.setModel(self.m_managers)

        self.m_pilots = QStandardItemModel()
        self.m_pilots.setColumnCount(4)
        self.m_pilots.setHorizontalHeaderLabels(['ID', 'Имя', 'Статус', 'Баланс'])

        self.m_rockets = QStandardItemModel()
        self.m_rockets.setColumnCount(11)
        self.m_rockets.setHorizontalHeaderLabels(['Логин', 'Статус1', 'Статус2', 'Пилот', 'Баланс', 'Параметры', 'Время в полете', 'Добыто', 'Выплат', 'Добыто ордера', 'Ордеров'])
        self.t_rockets.setModel(self.m_rockets)

        self.m_marketinfo = QStandardItemModel()
        self.m_marketinfo.setColumnCount(2)
        self.m_marketinfo.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_marketinfo.setModel(self.m_marketinfo)

        self.m_parameters_temapates = QStandardItemModel()
        self.m_parameters_temapates.setColumnCount(2)
        self.m_parameters_temapates.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_parameters_temapates.setModel(self.m_parameters_temapates)
        dpt = self.settings.value("default_parameters_template", "")
        if dpt:
            self.parameters = json.loads(dpt)
        self.fillparameterstemplate(self.parameters)

        self.m_parameters = QStandardItemModel()
        self.m_parameters.setColumnCount(2)
        self.m_parameters.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_parameters.setModel(self.m_parameters)

        #   ------------------------------------------------------------------------

        corereceiveq = queue.Queue()
        serveraddress = 'ws://' + self.serveraddress + ':' + self.serverport
        self.wsscore = WSSClient(corereceiveq, serveraddress)
        self.wsscore.daemon = True
        self.wsscore.start()

        self.corereceiver = FromQToF(self.receivemessagefromcore, corereceiveq)
        self.corereceiver.daemon = True
        self.corereceiver.start()

        self.coresendq = queue.Queue()
        self.coresender = FromQToF(self.wsscore.send, self.coresendq)
        self.coresender.daemon = True
        self.coresender.start()

        #   ------------------------------------------------------------------------

        self.user = ''

    def closeEvent(self, *args, **kwargs):
        pass

    def userlogined(self, user, psw):
        if self.wsscore.flConnect and not self.flAuth:
            self.user = user
            data = {'command':'mc_registration', 'user':user, 'psw':psw}
            self.coresendq.put(data)

    def fillparameterstemplate(self, parameters):
        self.m_parameters_temapates.removeRows(0, self.m_parameters_temapates.rowCount())
        rownum = 0
        for k, v in parameters.items():
            self.m_parameters_temapates.appendRow([QStandardItem(), QStandardItem()])
            self.m_parameters_temapates.item(rownum, 0).setData(k, Qt.DisplayRole)
            self.m_parameters_temapates.item(rownum, 1).setData(v, Qt.DisplayRole)
            rownum += 1

    def change_auth_status(self):
        if self.flAuth:
            self.pb_enter.setText('вход выполнен: ' + self.user)
            self.pb_enter.setStyleSheet("color:rgb(64, 192, 64); font: bold 12px;border: none")
        else:
            self.pb_enter.setText('вход не выполнен')
            self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")

    def receivemessagefromcore(self, data):
        command = data.get('command')
        if command == 'cm_registration':
            status = data.get('status')
            if status == 'ok':
                self.flAuth = True
            else:
                self.flAuth = False
            self.change_auth_status()
        elif command == 'cm_pilotinfo':
            pilot = data.get('pilot')
            name = data.get('name')
            authstate = data.get('authstate')
            info = data.get('info')
            parameters = data.get('parameters')
            self.cm_pilotinfo(pilot, name, authstate, info, parameters)
        elif command == 'cm_managersinfo':
            managers_data = data.get('managers')
            self.cm_managersinfo(managers_data)
        else:
            pass

    def showrocketparameters(self):
        parameters = self.pilots_parameters.get(self.current_pilot)
        # if parameters:
        #     self.m_parameters.removeRows(0, self.m_parameters.rowCount())
        #     rownum = 0
        #     for k, v in parameters.items():
        #         self.m_parameters.appendRow([QStandardItem(), QStandardItem()])
        #         self.m_parameters.item(rownum, 0).setData(k, Qt.DisplayRole)
        #         self.m_parameters.item(rownum, 1).setData(v, Qt.DisplayRole)
        #         rownum += 1
        #
        # if self.m_parameters.rowCount() > 0:
        #     i1 = self.m_parameters.item(0, 0).index()
        #     i2 = self.m_parameters.item(self.m_parameters.rowCount() - 1, 1).index()
        #     self.t_parameters.dataChanged(i1, i2)
        #
        # if self.last_rocket_row:
        #     for column in range(0, self.m_rockets.columnCount()):
        #         self.m_rockets.item(self.last_rocket_row, column).setFont(QFont("Helvetica", 10, QFont.Normal))
        #
        # for column in range(0, self.m_rockets.columnCount()):
        #     self.m_rockets.item(self.current_rocket_row, column).setFont(QFont("Helvetica", 10, QFont.Bold))

    @pyqtSlot()
    def t_rockets_clicked(self):
        index = self.t_rockets.selectedIndexes()[0].siblingAtColumn(0)
        # self.last_rocket_row = self.current_rocket_row
        # self.current_rocket_row = index.row()
        # self.showrocketparameters()

    @pyqtSlot()
    def t_parameters_temapates_customContextMenuRequested(self):

        def customContextMenuTriggered(itemNumber):
            if itemNumber == 1:
                filename = QFileDialog().getOpenFileName(self, "Файл шаблонов параметров", "", "tmpr files (*.tmpr)")[0]
                if filename:
                    file = open(filename, "r")
                    parameters = json.loads(file.readline())
                    self.fillparameterstemplate(parameters)
                    file.close()
            elif itemNumber == 2:
                filename = QFileDialog().getSaveFileName(self, "Файл шаблонов параметров", "", "tmpr files (*.tmpr)")[0]
                if filename:
                    file = open(filename, "w")
                    parameters = {}
                    for rownum in range(0, self.m_parameters_temapates.rowCount()):
                        parameters[self.m_parameters_temapates.item(rownum, 0).data(Qt.DisplayRole)] = self.m_parameters_temapates.item(rownum, 1).data(Qt.DisplayRole)
                    str = json.dumps(parameters)
                    file.write(str)
                    file.close()
            elif itemNumber == 3:
                parameters = {}
                for rownum in range(0, self.m_parameters.rowCount()):
                    parameters[self.m_parameters.item(rownum, 0).data(Qt.DisplayRole)] = self.m_parameters.item(rownum, 1).data(Qt.DisplayRole)
                self.fillparameterstemplate(parameters)
            elif itemNumber == 4:
                parameters = {}
                for rownum in range(0, self.m_parameters_temapates.rowCount()):
                    parameters[self.m_parameters_temapates.item(rownum, 0).data(
                        Qt.DisplayRole)] = self.m_parameters_temapates.item(rownum, 1).data(Qt.DisplayRole)
                self.wsscore.mc_setparameters(self.current_rocket_id, parameters)

        menu = QMenu()
        menu.addAction(self.tr("Загрузить шаблон")).triggered.connect(lambda: customContextMenuTriggered(1))
        menu.addAction(self.tr("Сохранить шаблон")).triggered.connect(lambda: customContextMenuTriggered(2))
        menu.addAction(self.tr("Из параметров")).triggered.connect(lambda: customContextMenuTriggered(3))
        menu.addAction(self.tr("Применить шаблон")).triggered.connect(lambda: customContextMenuTriggered(4))
        menu.exec_(QCursor.pos())

    @pyqtSlot()
    def buttonLogin_clicked(self):
        rw = LoginWindow()
        rw.userlogined.connect(lambda: self.userlogined(rw.user, rw.psw))
        rw.setupUi()
        rw.exec_()

    def cm_managersinfo(self, managers_data):
        self.m_managers.removeRows(0, self.m_managers.rowCount())
        rownum = 0
        for manager in managers_data:
            self.m_managers.appendRow([QStandardItem()])
            self.m_managers.item(rownum, 0).setData(manager, Qt.DisplayRole)
            rownum += 1

    def cm_pilotinfo(self, pilot, name, authstate, info, parameters):
        item = self.m_rockets.findItems(pilot, flags=Qt.MatchExactly, column=0)
        if not item:
            rownum = self.m_rockets.rowCount()
            #                           ['Логин',        'Статус1',      'Статус2',          'Пилот',       'Баланс',       'Параметры',    'Время в полете', 'Добыто',          'Выплат',  'Добыто ордера',    'Ордеров']
            self.m_rockets.appendRow([QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem()])
            self.m_rockets.item(rownum, 0).setData(pilot, Qt.DisplayRole)
        else:
            rownum = item[0].row()
        if authstate:
            self.m_rockets.item(rownum, 2).setData(authstate, 3)
            self.m_rockets.item(rownum, 2).setData(self.pilotscodes[authstate], Qt.DisplayRole)
            self.m_rockets.item(rownum, 2).setData(QColor(200 - 15 * authstate, 200 + 15 * authstate, 255), Qt.BackgroundColorRole)
        if name:
            self.m_rockets.item(rownum, 3).setData(name, Qt.DisplayRole)
        if info:
            self.m_rockets.item(rownum, 4).setData(info['balance'], Qt.DisplayRole)
            racetime = str(datetime.timedelta(seconds=round(info['racetime'])))
            self.m_rockets.item(rownum, 6).setData(racetime, Qt.DisplayRole)
            self.m_rockets.item(rownum, 7).setData(info['fundingmined'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 8).setData(info['fundingcount'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 9).setData(info['contractmined'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 10).setData(info['contractcount'], Qt.DisplayRole)
        if parameters:
            self.pilots_parameters[pilot] = parameters
            strparameters = parameters['symbol'][0:3]
            for i in range(5):
                strparameters += ' ' + str(parameters['dist' + str(i + 1)])
            self.m_rockets.item(rownum, 5).setData(strparameters, Qt.DisplayRole)

        i1 = self.m_rockets.item(rownum, 2).index()
        i2 = self.m_rockets.item(rownum, 3).index()
        self.t_rockets.dataChanged(i1, i2)


app = QApplication([])
win = MainWindow()
sys.exit(app.exec_())
