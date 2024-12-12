"""
author: xubing lin
date: 24/12/11
project: book-management-system
"""
import pymysql
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt
from dotenv import load_dotenv
import os

# 在QApplication之前先实例化
uiLoader = QUiLoader()

class LibrarianWindow:
    def __init__(self):
        self.ui = uiLoader.load('librarian_window.ui')

        self.ui.insertButton.clicked.connect(self.handleInsert)
        self.ui.selectButton.clicked.connect(self.handleSelect)

    def createDBConnection(self):
        # 加载 .env 文件中的环境变量
        load_dotenv()
        # 获取数据库连接信息
        DBHOST = os.getenv('DB_HOST')
        DBNAME = os.getenv('DB_NAME')
        DBUSER = 'librarian'
        DBPASS = '123'
        connection = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        return connection

    def handleInsert(self):
        bookid_info = self.ui.bookidEdit.text()
        title_info = self.ui.titleEdit.text()
        author_info = self.ui.authorEdit.text()
        category_info = self.ui.categoryEdit.text()
        state_info = self.ui.state_comboBox.currentText()
        self.db = self.createDBConnection()
        try:
            with self.db.cursor() as cur:
                sql = 'insert into books(bookid, title, author, category, state) value (%s, %s, %s, %s, %s)'
                value = (bookid_info, title_info, author_info, category_info, state_info)
                cur.execute(sql, value)
                pass
            self.db.commit()
            QMessageBox.about(self.ui,'操作提示', '图书新增成功')
        except pymysql.Error as e:
            QMessageBox.about(self.ui,'操作提示', '数据插入失败'+str(e))
            print('操作失败' + str(e))
            self.db.rollback()
        self.db.close()

    def handleSelect(self):
        self.ui.table.clearContents()
        info = self.ui.searchEdit.text()
        method = self.ui.attribute_comboBox.currentText()
        self.db = self.createDBConnection()
        try:
            with self.db.cursor() as cur:
                if method == '编号':
                    sql = 'select * from books where bookid = %s'
                elif method == '书名':
                    sql = 'select * from books where title = %s'
                elif method == '作者':
                    sql = 'select * from books where author = %s'
                elif method == '类别':
                    sql = 'select * from books where category = %s'
                else:
                    sql = 'select * from books where state = %s'
                cur.execute(sql, info)
                results = cur.fetchall()
                pass
            self.db.commit()
        except pymysql.Error as e:
            QMessageBox.about(self.ui,'操作提示', '操作失败'+str(e))
            print('操作失败' + str(e))
            self.db.rollback()
        self.db.close()

        self.ui.table.setRowCount(len(results)) #TODO 必须要添加单元行，否则表格中什么也没有
        j = 0
        for row in results:
            i = 0
            for value in row:
                item = QTableWidgetItem()
                item.setText(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table.setItem(j, i, item)
                i = i + 1
            # 增加借阅按钮
            deleteButton = QPushButton("删除")
            deleteButton.setProperty("rowIndex", j)
            deleteButton.clicked.connect(lambda _, book=results[j]: self.handleDeleteButton(book))
            self.ui.table.setCellWidget(j, 5, deleteButton)
            updateButton = QPushButton("修改")
            updateButton.setProperty("rowIndex", j)
            updateButton.clicked.connect(lambda _, book=results[j]: self.handleUpdateButton(book))
            self.ui.table.setCellWidget(j, 6, updateButton)
            j = j + 1

    def handleDeleteButton(self, book):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("操作提示")
        msg_box.setText(f"是否删除:\n《{book[1]}》")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.exec()
        if msg_box.standardButton(msg_box.clickedButton()) == QMessageBox.Ok:
            self.db = self.createDBConnection()
            try:
                with self.db.cursor() as cur:
                    sql = 'delete from books where bookid = %s'
                    info = book[0]
                    cur.execute(sql, info)
                    pass
                self.db.commit()
                QMessageBox.about(self.ui, '操作提示', '图书删除成功')
            except pymysql.Error as e:
                QMessageBox.about(self.ui, '操作提示', '操作失败'+str(e))
                print('操作失败' + str(e))
                self.db.rollback()
            self.db.close()

    def handleUpdateButton(self, books):
        QMessageBox.about(self.ui, '操作提示', f"已选中:\n《{books[1]}》\n请在“修改编辑”区编辑新内容")
        self.ui.updateNewButton.clicked.connect(lambda _, book=books: self.handleUpdateNewButton(book))

    def handleUpdateNewButton(self, book):
        updateAttribute = self.ui.updateNewcomboBox.currentText()
        updateInfo = self.ui.updateNewEdit.text()
        if updateAttribute == '编号':
            sql = 'update books set bookid = %s where bookid = %s'
        elif updateAttribute == '书名':
            sql = 'update books set title = %s where bookid = %s'
        elif updateAttribute == '作者':
            sql = 'update books set author = %s where bookid = %s'
        elif updateAttribute == '类别':
            sql = 'update books set category = %s where bookid = %s'
        else:
            sql = 'update books set state = %s where bookid = %s'

        self.db = self.createDBConnection()
        try:
            with self.db.cursor() as cur:
                info = (updateInfo, book[0])
                cur.execute(sql, info)
                pass
            self.db.commit()
            QMessageBox.about(self.ui, '操作提示', '修改成功')
        except pymysql.Error as e:
            QMessageBox.about(self.ui, '操作提示', '修改失败' + str(e))
            print('操作失败' + str(e))
            self.db.rollback()
        self.db.close()