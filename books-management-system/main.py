"""
author: xubing lin
date: 24/5/17
project: database
"""
import pymysql
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt
from qt_material import apply_stylesheet

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
        DBHOST = 'localhost'
        DBUSER = self.ui.IDcomboBox.currentText()
        DBPASS = self.ui.passEdit.text()
        DBNAME = 'db_library'
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

class LibrarianWindow:
    def __init__(self):
        self.ui = uiLoader.load('librarian_window.ui')

        self.ui.insertButton.clicked.connect(self.handleInsert)
        self.ui.selectButton.clicked.connect(self.handleSelect)

    def createDBConnection(self):
        DBHOST = 'localhost'
        DBUSER = 'librarian'
        DBPASS = 'dut'
        DBNAME = 'db_library'
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


class ReaderWindow():
    def __init__(self, reader, password):
        self.reader_name = reader
        self.reader_password = password
        # 使用librarian登录一次数据库，以获取readerid
        DBHOST = 'localhost'
        DBUSER = 'librarian'
        DBPASS = 'dut'
        DBNAME = 'db_library'
        try:
            db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
            print("数据库成功连接！")
            cur = db.cursor()
            sql = 'select readerid, state from readers where reader_name = %s'
            cur.execute(sql, self.reader_name)
            results = cur.fetchall()
        except pymysql.Error as e:
            QMessageBox.about(self.ui,'操作提示', '操作失败'+str(e))
            print('操作失败' + str(e))
            db.rollback()
        db.close()
        self.readerid = results[0][0]
        self.state = results[0][1]

        self.ui = uiLoader.load('reader_window.ui')
        self.ui.readerLabel.setText(self.reader_name)
        self.ui.selectButton.clicked.connect(self.handleSelect)
        self.ui.borrowButton.clicked.connect(self.handleBorrow)
        self.ui.fineButton.clicked.connect(self.handleFine)
        self.ui.historyButton.clicked.connect(self.handleHistory)

    def createDBConnection(self):
        DBHOST = 'localhost'
        DBUSER = self.reader_name
        DBPASS = self.reader_password
        DBNAME = 'db_library'
        connection = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
        return connection

    def handleSelect(self):
        self.ui.table.clearContents()
        info = self.ui.searchEdit.text()
        method = self.ui.comboBox.currentText()
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

        self.ui.table.setRowCount(len(results))  # TODO 必须要添加单元行，否则表格中什么也没有
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
            button = QPushButton("借阅")
            button.setProperty("rowIndex", j)
            button.clicked.connect(lambda _, book=results[j]: self.handleBorrowButton(book))
            if row[4] == "可借阅":
                self.ui.table.setCellWidget(j, 5, button)
            j = j + 1

    def handleBorrowButton(self, book):
        if self.state == '不可借阅':
            QMessageBox.about(self.ui, '操作提示', '当前您的状态为不可借阅')
            return
        msg_box = QMessageBox()
        msg_box.setWindowTitle("操作提示")
        msg_box.setText(f"借阅:\n《{book[1]}》")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.exec()

        if msg_box.standardButton(msg_box.clickedButton()) == QMessageBox.Ok:
            self.db = self.createDBConnection()
            try:
                with self.db.cursor() as cur:
                    sql = '''
                    insert into borrow values(
                    %s, %s, curdate(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), '借阅中')
                    '''
                    info = (self.readerid, book[0])
                    cur.execute(sql, info)
                    pass
                self.db.commit()
                QMessageBox.about(self.ui,'操作提示', '借阅成功')
            except pymysql.Error as e:
                QMessageBox.about(self.ui,'操作提示', '操作失败'+str(e))
                print('操作失败' + str(e))
                self.db.rollback()
            self.db.close()

    def handleBorrow(self):
        self.db = self.createDBConnection()
        try:
            with self.db.cursor() as cur:
                sql = """
                SELECT borrow.bookid, books.title, borrow.borrow_date, borrow.due_date, borrow.state
                FROM borrow, books
                WHERE borrow.bookid = books.bookid AND borrow.readerid = %s;
                """
                info = self.readerid
                cur.execute(sql, info)
                results = cur.fetchall()
                pass
            self.db.commit()
        except pymysql.Error as e:
            QMessageBox.about(self.ui,'操作提示', '操作失败'+str(e))
            print('操作失败' + str(e))
            self.db.rollback()
        self.db.close()

        self.ui.table_2.setRowCount(len(results))  # TODO 必须要添加单元行，否则表格中什么也没有
        j = 0
        for row in results:
            i = 0
            for value in row:
                item = QTableWidgetItem()
                item.setText(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_2.setItem(j, i, item)
                i = i + 1
            j = j + 1

    def handleFine(self):
        self.ui.table_2.setHorizontalHeaderItem(4, QTableWidgetItem('罚款金额'))
        self.ui.fineLabel.setText("注意：图书逾期费为0.1元/册/天")
        self.db = self.createDBConnection()
        try:
            with self.db.cursor() as cur:
                sql = """
                select borrow.bookid, books.title, borrow.borrow_date, borrow.due_date
                from borrow, books
                where borrow.state = '已逾期' and borrow.bookid = books.bookid and borrow.readerid = %s;
                """
                info = self.readerid
                cur.execute(sql, info)
                results = cur.fetchall()
                pass
            self.db.commit()
        except pymysql.Error as e:
            QMessageBox.about(self.ui,'操作提示', '操作失败'+str(e))
            print('操作失败' + str(e))
            self.db.rollback()
        self.db.close()

        self.ui.table_2.setRowCount(len(results))  # TODO 必须要添加单元行，否则表格中什么也没有
        j = 0
        sum = 0
        for row in results:
            i = 0
            for value in row:
                item = QTableWidgetItem()
                item.setText(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_2.setItem(j, i, item)
                i = i + 1
            # 计算罚款
            current_date = datetime.now().date()
            due_date = row[3]
            fine = round(((current_date - due_date).days) * 0.1, 1) # 罚款金额精确到小数点后1位
            sum = sum + fine
            item = QTableWidgetItem()
            item.setText(str(fine))
            item.setTextAlignment(Qt.AlignCenter)
            self.ui.table_2.setItem(j, i, item)
            j = j + 1

        self.ui.fineSumLabel.setText(f"总计逾期费: {sum:.1f}元")

    def handleHistory(self):
        self.ui.table_2.clearContents()
        self.db = self.createDBConnection()
        try:
            with self.db.cursor() as cur:
                sql = '''
                select history.bookid, title, borrow_date 
                from history, books 
                where history.readerid = %s and history.bookid = books.bookid;
                       '''
                info = self.readerid
                cur.execute(sql, info)
                results = cur.fetchall()
                pass
            self.db.commit()
        except pymysql.Error as e:
            QMessageBox.about(self.ui,'操作提示', '操作失败'+str(e))
            print('操作失败' + str(e))
            self.db.rollback()
        self.db.close()

        self.ui.table_2.setRowCount(len(results))  # TODO 必须要添加单元行，否则表格中什么也没有
        j = 0
        for row in results:
            i = 0
            for value in row:
                item = QTableWidgetItem()
                item.setText(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.table_2.setItem(j, i, item)
                i = i + 1
            j = j + 1


app = QApplication()
apply_stylesheet(app, theme='dark_amber.xml')
login_window = LoginWindow()
login_window.ui.show()
app.exec()