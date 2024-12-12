"""
author: xubing lin
date: 24/5/17
project: book-management-system
"""
import pymysql
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt
from qt_material import apply_stylesheet
from dotenv import load_dotenv
import os
from librarian import LibrarianWindow
from reader import ReaderWindow

# 在QApplication之前先实例化
uiLoader = QUiLoader()

class LoginWindow:
    def __init__(self):
        self.ui = uiLoader.load('login_window.ui')
        self.ui.setFixedSize(600, 400)

        self.ui.reader_radioButton.clicked.connect(self.update_comboBox)
        self.ui.librarian_radioButton.clicked.connect(self.update_comboBox)
        self.ui.button.clicked.connect(self.handleLogin)

    def update_comboBox(self):
        # 根据单选按钮的选择更新下拉列表框的选项
        if self.ui.reader_radioButton.isChecked():
            # 假设当选择第一个单选按钮时，下拉列表框显示不同的选项
            self.ui.IDcomboBox.clear()
            self.ui.IDcomboBox.addItems(["reader1", "reader2", "reader3"])
        else:
            # 假设当选择第二个单选按钮时，下拉列表框显示另一组选项
            self.ui.IDcomboBox.clear()
            self.ui.IDcomboBox.addItems(["librarian"])

    def handleLogin(self):
        # 加载 .env 文件中的环境变量
        load_dotenv()
        # 获取数据库连接信息
        DBHOST = os.getenv('DB_HOST')
        DBNAME = os.getenv('DB_NAME')
        DBUSER = self.ui.IDcomboBox.currentText()
        DBPASS = self.ui.passEdit.text()
        try:
            db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
            print("数据库成功连接！")
            if self.ui.IDcomboBox.currentText() == 'librarian':
                QTimer.singleShot(1000, self.openLibrarianWindow)
            else:
                QTimer.singleShot(1000, self.openReaderWindow(DBUSER, DBPASS))
        except pymysql.Error as e:
            QMessageBox.about(self.ui, '操作提示', '操作失败'+str(e))
            print('操作失败'+str(e))
            db.rollback()
        db.close()

    def openLibrarianWindow(self):
        self.ui.close()
        self.mainWindow = LibrarianWindow()
        self.mainWindow.ui.show()

    def openReaderWindow(self, reader, password):
        self.ui.close()
        self.mainWindow = ReaderWindow(reader, password)
        self.mainWindow.ui.show()

app = QApplication()
apply_stylesheet(app, theme='dark_amber.xml')
login_window = LoginWindow()
login_window.ui.show()
app.exec()