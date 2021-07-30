import sys
import queue
import logging

from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QCursor, QFont
from PyQt5.QtCore import QSettings, pyqtSlot, Qt
from mainWindow import UiMainWindow
from loginWindow import LoginWindow
from wss import Worker, WSSCore
from threading import Lock
import json


class MainWindow(QMainWindow, UiMainWindow):
    version = '1.0.7'
    settings = QSettings("./config.ini", QSettings.IniFormat)   # файл настроек
    lock = Lock()

    flConnect = False           #   флаг нормального соединения с сайтом
    pilotscodes = {0:'Не авторизован', 1:'Авторизован', 2:'В ракете'}
    rocketscodes = {0: 'Готова к вылету', 1:'С пилотом', 2: 'В полете'}

    flAuth = False

    rockets_parameters = {}
    current_rocket_id = 0
    current_rocket_row = None
    last_rocket_row = None

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
        self.t_pilots.setModel(self.m_pilots)
        self.t_pilots.setColumnHidden(0, True)

        self.m_rockets = QStandardItemModel()
        self.m_rockets.setColumnCount(9)
        self.m_rockets.setHorizontalHeaderLabels(['ID', 'Модель', 'Пилот', 'Статус', 'Время в полете', 'Добыто ЛМ', 'Выплат', 'Добыто рынок', 'Ордеров'])
        self.t_rockets.setModel(self.m_rockets)

        self.m_marketinfo = QStandardItemModel()
        self.m_marketinfo.setColumnCount(2)
        self.m_marketinfo.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_marketinfo.setModel(self.m_marketinfo)

        self.m_parameters_temapates = QStandardItemModel()
        self.m_parameters_temapates.setColumnCount(2)
        self.m_parameters_temapates.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_parameters_temapates.setModel(self.m_parameters_temapates)
        self.parameters = json.loads(self.settings.value("default_parameters_template", ""))
        self.fillparameterstemplate(self.parameters)

        self.m_parameters = QStandardItemModel()
        self.m_parameters.setColumnCount(2)
        self.m_parameters.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_parameters.setModel(self.m_parameters)

        q = queue.Queue()

        self.wsscore = WSSCore(self, q)
        self.wsscore.daemon = True
        self.wsscore.start()

        self.worker = Worker(self.updatetv, q)
        self.worker.daemon = True
        self.worker.start()

        self.user = ''

    def closeEvent(self, *args, **kwargs):
        pass

    def userlogined(self, user, psw):
        if self.wsscore.flConnect and not self.flAuth:
            self.user = user
            self.wsscore.mc_registration(user, psw)

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

    def updatetv(self, data):
        command = data.get('command')
        if command == 'cm_registration':
            status = data.get('status')
            if status == 'ok':
                self.flAuth = True
            else:
                self.flAuth = False
            self.change_auth_status()
        elif command == 'cm_rocketinfo':
            print(data)
            rocket = data.get('rocket')
            self.cm_rocketinfo(rocket)
        elif command == 'cm_rocketdelete':
            rocket_id = data.get('rocket')
            self.cm_rocketdelete(rocket_id)
        elif command == 'cm_pilotinfo':
            pilot = data.get('pilot')
            info = data.get('info')
            self.cm_pilotinfo(pilot, info)
        elif command == 'cm_managersinfo':
            managers_data = data.get('managers')
            self.cm_managersinfo(managers_data)
        else:
            pass

    def showrocketparameters(self):
        parameters = self.rockets_parameters.get(self.current_rocket_id)
        if parameters:
            self.m_parameters.removeRows(0, self.m_parameters.rowCount())
            rownum = 0
            for k, v in parameters.items():
                self.m_parameters.appendRow([QStandardItem(), QStandardItem()])
                self.m_parameters.item(rownum, 0).setData(k, Qt.DisplayRole)
                self.m_parameters.item(rownum, 1).setData(v, Qt.DisplayRole)
                rownum += 1

        if self.m_parameters.rowCount() > 0:
            i1 = self.m_parameters.item(0, 0).index()
            i2 = self.m_parameters.item(self.m_parameters.rowCount() - 1, 1).index()
            self.t_parameters.dataChanged(i1, i2)

        if self.last_rocket_row:
            for column in range(0, self.m_rockets.columnCount()):
                self.m_rockets.item(self.last_rocket_row, column).setFont(QFont("Helvetica", 10, QFont.Normal))

        for column in range(0, self.m_rockets.columnCount()):
            self.m_rockets.item(self.current_rocket_row, column).setFont(QFont("Helvetica", 12, QFont.Bold))

    @pyqtSlot()
    def t_pilots_doubleClicked(self):
        index = self.t_pilots.selectedIndexes()[0].siblingAtColumn(0)
        name = self.m_pilots.itemData(index)[Qt.DisplayRole]
        index = self.t_pilots.selectedIndexes()[0].siblingAtColumn(2)
        status = self.m_pilots.itemData(index)[3]
        #    если пилот свободен
        if status == 1:
            #   ищем свободную ракету
            rocket_id = 0
            for i in range(self.m_rockets.rowCount()):
                rocket_status = self.m_rockets.item(i, 3).data(3)
                if rocket_status == 0:
                    rocket_id = self.m_rockets.item(i, 0).data(Qt.DisplayRole)
                    break
            if rocket_id != 0:
                self.current_rocket_id = rocket_id
                self.current_rocket_row = i
                self.showrocketparameters()
                self.wsscore.mc_authpilot(name, rocket_id)
            else:
                print('Нет свободных ракет')

    @pyqtSlot()
    def t_rockets_clicked(self):
        index = self.t_rockets.selectedIndexes()[0].siblingAtColumn(0)
        self.current_rocket_id = self.m_rockets.item(index.row(), 0).data(Qt.DisplayRole)
        self.current_rocket_row = index.row()
        self.showrocketparameters()

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

    def cm_rocketinfo(self, rocket_data):
        for k,v in rocket_data.items():
            item = self.m_rockets.findItems(k, flags=Qt.MatchExactly, column=0)
            if not item:
                rownum = self.m_rockets.rowCount()
                self.m_rockets.appendRow([QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem()])
                self.m_rockets.item(rownum, 0).setData(k, Qt.DisplayRole)
                self.m_rockets.item(rownum, 1).setData(v['version'], Qt.DisplayRole)
            else:
                rownum = item[0].row()

            self.m_rockets.item(rownum, 2).setData(v['pilot'], Qt.DisplayRole)
            status = v['status']
            self.m_rockets.item(rownum, 3).setData(status, 3)
            self.m_rockets.item(rownum, 3).setData(self.rocketscodes[status], Qt.DisplayRole)
            self.m_rockets.item(rownum, 3).setData(QColor(200 - 15 * status, 200 + 15 * status, 255), Qt.BackgroundColorRole)
            info = v['info']
            if info:
                self.m_rockets.item(rownum, 4).setData(info['racetime'], Qt.DisplayRole)
                self.m_rockets.item(rownum, 5).setData(info['fundingmined'], Qt.DisplayRole)
                self.m_rockets.item(rownum, 6).setData(info['fundingcount'], Qt.DisplayRole)
                self.m_rockets.item(rownum, 7).setData(info['contractmined'], Qt.DisplayRole)
                self.m_rockets.item(rownum, 8).setData(info['contractcount'], Qt.DisplayRole)
            parameters = v['parameters']
            if parameters:
                self.rockets_parameters[k] = parameters
            if self.current_rocket_id == 0:
                self.current_rocket_id = k
                self.current_rocket_row = rownum
            self.showrocketparameters()

            i1 = self.m_rockets.item(rownum, 2).index()
            i2 = self.m_rockets.item(rownum, 8).index()
            self.t_rockets.dataChanged(i1, i2)

    def cm_rocketdelete(self, rocket_id):
        item = self.m_rockets.findItems(rocket_id, flags=Qt.MatchExactly, column=0)
        if item:
            self.m_rockets.removeRow(item[0].row())
            if self.m_rockets.rowCount() > 0:
                self.showrocketparameters()
            else:
                self.current_rocket_id = 0
                self.m_parameters.removeRows(0, self.m_parameters.rowCount())

    def cm_pilotinfo(self, pilot, pilot_info):
        item = self.m_pilots.findItems(pilot, flags=Qt.MatchExactly, column=0)
        if not item:
            rownum = self.m_pilots.rowCount()
            self.m_pilots.appendRow([QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem()])
            self.m_pilots.item(rownum, 0).setData(pilot, Qt.DisplayRole)
            self.m_pilots.item(rownum, 1).setData(pilot_info['name'], Qt.DisplayRole)
        else:
            rownum = item[0].row()

        status = pilot_info['status']
        self.m_pilots.item(rownum, 2).setData(status, 3)
        self.m_pilots.item(rownum, 2).setData(self.pilotscodes[status], Qt.DisplayRole)
        self.m_pilots.item(rownum, 2).setData(QColor(200 - 15 * status, 200 + 15 * status, 255), Qt.BackgroundColorRole)
        balance = pilot_info['balance']
        self.m_pilots.item(rownum, 3).setData(balance, Qt.DisplayRole)

        i1 = self.m_pilots.item(rownum, 2).index()
        i2 = self.m_pilots.item(rownum, 3).index()
        self.t_pilots.dataChanged(i1, i2)


app = QApplication([])
win = MainWindow()
sys.exit(app.exec_())
