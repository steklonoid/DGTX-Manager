import random
import sys
import os
import time
import queue
import logging

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import QSettings, pyqtSlot, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from mainWindow import UiMainWindow
from loginWindow import LoginWindow
from wss import Worker, WSSCore
import hashlib
from Crypto.Cipher import AES # pip install pycryptodome
import math
import numpy as np
from threading import Lock


class MainWindow(QMainWindow, UiMainWindow):
    version = '1.0.6'
    settings = QSettings("./config.ini", QSettings.IniFormat)   # файл настроек
    lock = Lock()

    flConnect = False           #   флаг нормального соединения с сайтом
    pilotscodes = {0:'Не авторизован', 1:'Авторизован', 2:'В ракете'}
    rocketscodes = {0: 'Готова к вылету', 1:'С пилотом', 2: 'В полете'}


    def __init__(self):

        super().__init__()
        logging.basicConfig(filename='info.log', level=logging.INFO, format='%(asctime)s %(message)s')

        # создание визуальной формы
        self.setupui(self)
        self.show()

        self.m_pilots = QStandardItemModel()
        self.m_pilots.setColumnCount(4)
        self.m_pilots.setHorizontalHeaderLabels(['ID', 'Имя', 'Статус', 'Баланс'])
        self.t_pilots.setModel(self.m_pilots)
        self.t_pilots.setColumnHidden(0, True)

        self.m_rockets = QStandardItemModel()
        self.m_rockets.setColumnCount(9)
        self.m_rockets.setHorizontalHeaderLabels(['ID', 'Модель', 'Пилот', 'Статус', 'Время в полете', 'Добыто ЛМ', 'Выплат', 'Добыто рынок', 'Ордеров'])
        self.t_rockets.setModel(self.m_rockets)

        self.m_managers = QStandardItemModel()
        self.lt_managers.setModel(self.m_managers)

        self.m_param = QStandardItemModel()
        self.m_param.setColumnCount(2)
        self.m_param.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        self.t_param.setModel(self.m_param)

        self.wsscore = WSSCore(self)
        self.wsscore.daemon = True
        self.wsscore.start()

        self.user = ''

    def closeEvent(self, *args, **kwargs):
        pass

    def userlogined(self, user, psw):
        if self.wsscore.flConnect and not self.wsscore.flAuth:
            self.user = user
            self.wsscore.send_registration(user, psw)

    def change_auth_status(self):
        if self.wsscore.flAuth:
            self.pb_enter.setText('вход выполнен: ' + self.user)
            self.pb_enter.setStyleSheet("color:rgb(64, 192, 64); font: bold 12px;border: none")
        else:
            self.pb_enter.setText('вход не выполнен')
            self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")

    @pyqtSlot()
    def t_pilots_doubleClicked(self):
        index = self.t_pilots.selectedIndexes()[0].siblingAtColumn(0)
        name = self.m_pilots.itemData(index)[Qt.DisplayRole]
        index = self.t_pilots.selectedIndexes()[0].siblingAtColumn(2)
        status = self.m_pilots.itemData(index)[3]
        #    если пилот свободен
        if status == 1:
            #   ищем свободную ракету
            flFreeRocket = False
            for i in range(self.m_rockets.rowCount()):
                rocket_id = self.m_rockets.item(i, 0).data(Qt.DisplayRole)
                rocket_status = self.m_rockets.item(i, 3).data(3)
                if rocket_status == 0:
                    flFreeRocket = True
                    break
            if flFreeRocket:
                self.wsscore.authpilot(name, rocket_id)
            else:
                print('Нет свободных ракет')

    @pyqtSlot()
    def t_races_clicked(self):
        self.m_param.removeRows(0, self.m_param.rowCount())
        index = self.t_races.selectedIndexes()[0].siblingAtColumn(0)
        rocket_id = self.m_races.itemData(index)[Qt.DisplayRole]
        parameters = self.races_data[rocket_id]['parameters']
        rownum = 0
        for k,v in parameters.items():
            self.m_param.appendRow([QStandardItem(), QStandardItem()])
            self.m_param.item(rownum, 0).setData(k, Qt.DisplayRole)
            self.m_param.item(rownum, 1).setData(v, Qt.DisplayRole)
            rownum += 1

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
            self.m_rockets.item(rownum, 4).setData(info['racetime'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 5).setData(info['fundingmined'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 6).setData(info['fundingcount'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 7).setData(info['contractmined'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 8).setData(info['contractcount'], Qt.DisplayRole)

    def cm_rocketdelete(self, rocket_id):
        item = self.m_rockets.findItems(rocket_id, flags=Qt.MatchExactly, column=0)
        if item:
            self.m_rockets.removeRow(item[0].row())

    def cm_pilotinfo(self, pilot_data):
        for k,v in pilot_data.items():
            item = self.m_pilots.findItems(k, flags=Qt.MatchExactly, column=0)
            if not item:
                rownum = self.m_pilots.rowCount()
                self.m_pilots.appendRow([QStandardItem(), QStandardItem(), QStandardItem(), QStandardItem()])
                self.m_pilots.item(rownum, 0).setData(k, Qt.DisplayRole)
                self.m_pilots.item(rownum, 1).setData(v['name'], Qt.DisplayRole)
            else:
                rownum = item[0].row()

            status = v['status']
            self.m_pilots.item(rownum, 2).setData(status, 3)
            self.m_pilots.item(rownum, 2).setData(self.pilotscodes[status], Qt.DisplayRole)
            self.m_pilots.item(rownum, 2).setData(QColor(200 - 15 * status, 200 + 15 * status, 255), Qt.BackgroundColorRole)
            balance = v['balance']
            self.m_pilots.item(rownum, 3).setData(balance, Qt.DisplayRole)


app = QApplication([])
win = MainWindow()
sys.exit(app.exec_())
