import random
import sys
import os
import time
import queue
import logging

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtCore import QSettings, pyqtSlot, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from mainWindow import UiMainWindow
from wss import WSThread, Worker, Senderq, WSSClient
import hashlib
from Crypto.Cipher import AES # pip install pycryptodome
import math
import numpy as np
from threading import Lock

# = order type
AUTO = 0
MANUAL = 1
OUTSIDE = 2
# = order status
OPENING = 0
ACTIVE = 1
CLOSING = 2

MAXORDERDIST = 5
NUMTICKS = 16
# NUMTICKSHISTORY = 108000



class MainWindow(QMainWindow, UiMainWindow):
    settings = QSettings("./config.ini", QSettings.IniFormat)   # файл настроек
    lock = Lock()

    symbol = 'BTCUSD-PERP'

    spotPx = 0                  #   текущая spot-цена
    lastSpotPx = 0

    listTick = np.zeros((NUMTICKS, 3), dtype=float)          #   массив последних тиков
    tickCounter = 0             #   счетчик тиков

    flConnect = False           #   флаг нормального соединения с сайтом

    def __init__(self):

        super().__init__()
        logging.basicConfig(filename='info.log', level=logging.INFO, format='%(asctime)s %(message)s')

        # создание визуальной формы
        self.setupui(self)
        self.show()

        self.m_pilots = QStandardItemModel()
        self.m_pilots.setColumnCount(2)
        self.m_pilots.setHorizontalHeaderLabels(['Имя', 'Статус'])
        self.t_pilots.setModel(self.m_pilots)

        self.m_rockets = QStandardItemModel()
        self.m_rockets.setColumnCount(3)
        self.m_rockets.setHorizontalHeaderLabels(['ID', 'Модель', 'Статус'])
        self.t_rockets.setModel(self.m_rockets)

        self.wssserver = WSSClient()
        self.wssserver.daemon = True
        self.wssserver.start()

        # self.sendq = queue.Queue()
        #
        # self.dxthread = WSThread(self)
        # self.dxthread.daemon = True
        # self.dxthread.start()
        #
        # self.senderq = Senderq(self.sendq, self.dxthread)
        # self.senderq.daemon = True
        # self.senderq.start()
        # #
        # self.listf = {'orderbook_1':{'q':queue.LifoQueue(), 'f':self.message_orderbook_1},
        #               'index':{'q':queue.LifoQueue(), 'f':self.message_index}}
        # self.listp = []
        # for ch in self.listf.keys():
        #     p = Worker(self.listf[ch]['q'], self.listf[ch]['f'])
        #     self.listp.append(p)
        #     p.daemon = True
        #     p.start()
        #
        # self.intimer = InTimer(self)
        # self.intimer.daemon = True
        # self.intimer.start()
        #
        # self.animator = Animator(self)
        # self.animator.daemon = True
        # self.animator.start()
        #
        # self.analizator = Analizator(self.midvol)
        # self.analizator.daemon = True
        # self.analizator.start()

    def closeEvent(self, *args, **kwargs):
        pass
        # self.dxthread.flClosing = True
        # self.dxthread.wsapp.close()
        # while self.dxthread.is_alive():
        #     pass

    @pyqtSlot()
    def button1_clicked(self):
        str = {'id': 3, 'message_type': 'manager_command', 'params': {'command': 'getlistrockets'}}
        self.wssserver.senddata(str)
        str = {'id': 3, 'message_type': 'manager_command', 'params': {'command': 'getlistpilots'}}
        self.wssserver.senddata(str)
        str = {'id': 3, 'message_type': 'manager_command', 'params': {'command': 'getlistmanagers'}}
        self.wssserver.senddata(str)

    def midvol(self):
        # self.lock.acquire()
        if self.tickCounter > NUMTICKS:
            self.lock.acquire()
            ar = np.array(self.listTick)
            self.lock.release()
            val = round(np.mean(ar, axis=0)[2], 2)
            npvar = round(np.var(ar, axis=0)[1], 3)
            self.l_midvol.setText(str(val))
            self.l_midvar.setText(str(npvar))
        # self.lock.release()

    # ========== обработчики сообщений ===========
    # ==== публичные сообщения
    def message_orderbook_1(self, data):
        self.lock.acquire()

        self.lock.release()

    def message_index(self, data):
        self.lock.acquire()
        self.tickCounter += 1
        self.lock.release()

app = QApplication([])
win = MainWindow()
sys.exit(app.exec_())
