import random
import sys
import os
import time
import queue
import logging

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSettings, pyqtSlot, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from mainWindow import UiMainWindow
from loginWindow import LoginWindow
from wss import Worker, WSSClient
import hashlib
from Crypto.Cipher import AES # pip install pycryptodome
import math
import numpy as np
from threading import Lock


class MainWindow(QMainWindow, UiMainWindow):
    version = '1.0.2'
    settings = QSettings("./config.ini", QSettings.IniFormat)   # файл настроек
    lock = Lock()

    flConnect = False           #   флаг нормального соединения с сайтом
    pilotscodes = {0:'На базе', 1:'Вылет разрешен', 2:'В полете'}
    rocketscodes = {0: 'Готова к вылету', 1: 'В полете'}


    def __init__(self):

        super().__init__()
        logging.basicConfig(filename='info.log', level=logging.INFO, format='%(asctime)s %(message)s')

        # создание визуальной формы
        self.setupui(self)
        self.show()

        self.m_pilots = QStandardItemModel()
        self.m_pilots.setColumnCount(3)
        self.m_pilots.setHorizontalHeaderLabels(['ID', 'Имя', 'Статус'])
        self.t_pilots.setModel(self.m_pilots)

        self.m_rockets = QStandardItemModel()
        self.m_rockets.setColumnCount(3)
        self.m_rockets.setHorizontalHeaderLabels(['ID', 'Модель', 'Статус'])
        self.t_rockets.setModel(self.m_rockets)

        self.m_managers = QStandardItemModel()
        self.m_managers.setColumnCount(1)
        self.m_managers.setHorizontalHeaderLabels(['Имя'])
        self.t_managers.setModel(self.m_managers)

        self.m_races = QStandardItemModel()
        self.m_races.setColumnCount(3)
        self.m_races.setHorizontalHeaderLabels(['Пилот', 'Ракета', 'Статус'])
        self.t_races.setModel(self.m_races)

        self.wssclient = WSSClient(self)
        self.wssclient.daemon = True
        self.wssclient.start()

        self.user = ''

    def closeEvent(self, *args, **kwargs):
        pass

    def userlogined(self, user, psw):
        if self.wssclient.flConnect and not self.wssclient.flAuth:
            self.user = user
            str = {'id':1, 'message_type':'registration', 'data':{'typereg':'manager', 'user':user, 'psw':psw}}
            self.wssclient.senddata(str)

    def change_auth_status(self):
        if self.wssclient.flAuth:
            self.pb_enter.setText('вход выполнен: ' + self.user)
            self.pb_enter.setStyleSheet("color:rgb(64, 192, 64); font: bold 12px;border: none")
            self.getinfo()
        else:
            self.pb_enter.setText('вход не выполнен')
            self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")

    def getinfo(self):
        str = {'id':2, 'message_type':'mc', 'data':{'command':'getrockets'}}
        self.wssclient.senddata(str)
        str = {'id': 3, 'message_type': 'mc', 'data': {'command': 'getpilots'}}
        self.wssclient.senddata(str)
        str = {'id': 4, 'message_type': 'mc', 'data': {'command': 'getmanagers'}}
        self.wssclient.senddata(str)
        # str = {'id': 5, 'message_type': 'mc', 'data': {'command': 'getraces'}}
        # self.wssclient.senddata(str)

    @pyqtSlot()
    def t_pilots_doubleClicked(self):
        index = self.t_pilots.selectedIndexes()[0].siblingAtColumn(0)
        name = self.m_pilots.itemData(index)[Qt.DisplayRole]
        index = self.t_pilots.selectedIndexes()[0].siblingAtColumn(2)
        status = self.m_pilots.itemData(index)[3]
        #    если пилот свободен
        if status == 0:
            #   ищем свободную ракету
            flFreeRocket = False
            for i in range(self.m_rockets.rowCount()):
                rocket_id = self.m_rockets.item(i, 0).data(Qt.DisplayRole)
                rocket_status = self.m_rockets.item(i, 2).data(3)
                if rocket_status == 0:
                    flFreeRocket = True
                    break
            if flFreeRocket:
                str = {'id': 5, 'message_type': 'mc', 'data': {'command': 'authpilot', 'pilot':name, 'rocket':rocket_id}}
                print(str)
                self.wssclient.senddata(str)
            else:
                print('Нет свободных ракет')

    @pyqtSlot()
    def buttonLogin_clicked(self):
        rw = LoginWindow()
        rw.userlogined.connect(lambda: self.userlogined(rw.user, rw.psw))
        rw.setupUi()
        rw.exec_()

    def cm_getrockets(self, rockets_data):
        self.m_rockets.removeRows(0, self.m_rockets.rowCount())
        rownum = 0
        for k,v in rockets_data.items():
            self.m_rockets.appendRow([QStandardItem(), QStandardItem(), QStandardItem()])
            self.m_rockets.item(rownum, 0).setData(k, Qt.DisplayRole)
            self.m_rockets.item(rownum, 1).setData(v['version'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 2).setData(v['status'], 3)
            self.m_rockets.item(rownum, 2).setData(self.rocketscodes[v['status']], Qt.DisplayRole)
            rownum += 1

    def cm_getmanagers(self, managers_data):
        self.m_managers.removeRows(0, self.m_managers.rowCount())
        rownum = 0
        for manager in managers_data:
            self.m_managers.appendRow([QStandardItem()])
            self.m_managers.item(rownum, 0).setData(manager, Qt.DisplayRole)
            rownum += 1

    def cm_getpilots(self, pilots_data):
        self.m_pilots.removeRows(0, self.m_pilots.rowCount())
        rownum = 0
        for k,v in pilots_data.items():
            self.m_pilots.appendRow([QStandardItem(), QStandardItem(), QStandardItem()])
            self.m_pilots.item(rownum, 0).setData(k, Qt.DisplayRole)
            self.m_pilots.item(rownum, 1).setData(v['name'], Qt.DisplayRole)
            self.m_pilots.item(rownum, 2).setData(v['status'], 3)
            self.m_pilots.item(rownum, 2).setData(self.pilotscodes[v['status']], Qt.DisplayRole)
            rownum += 1



    def getraces(self, data):
        pass

app = QApplication([])
win = MainWindow()
sys.exit(app.exec_())
