# 基于Pyside6+Pymysql的图书管理系统
## 1. **系统功能需求**
设计一个简单的图书系统，拥有用户登录界面、管理员Librarian界面和读者Reader界面。
读者可进行图书的查询和借阅，能够查看自己当前借阅的图书、是否有逾期未还的图书以及借阅历史，若读者有逾期未还的图书，则不可借阅新书。
管理员可进行图书的入库、出库、查询和修改。

## 2. **数据库设计**
### (1) ER图设计
![wps1](https://github.com/user-attachments/assets/f456dd8d-6b8a-43dd-901b-4911ed754ad1)

### (2) 数据库逻辑结构设计
Table: books（图书表）

| 属性名      | 数据类型         | 完整性约束                           |
| -------- | ------------ | ------------------------------- |
| bookid   | int          | AI PK                           |
| title    | varchar(255) |                                 |
| author   | varchar(255) |                                 |
| category | char(20)     |                                 |
| state    | char(10)     | check (state in ('借阅中', '可借阅')) |

Table: readers（读者表）

| 属性名             | 数据类型         | 完整性约束                           |
| --------------- | ------------ | ------------------------------- |
| readerid        | int          | AI PK                           |
| reader_name     | varchar(255) | NN                              |
| reader_password | varchar(255) |                                 |
| state           | char(20)     | check (state in ('不可借阅', '可借阅') |

Table: borrow（当前借阅表）

| 属性名         | 数据类型     | 完整性约束                          |
| ----------- | -------- | ------------------------------ |
| readerid    | int      | PK, FK readers(readerid)       |
| bookid      | int      | PK, FK books(bookid)           |
| borrow_date | date     | PK                             |
| due_date    | date     |                                |
| state       | char(10) | check (state in ('借阅中', '已逾期') |

Table: history（历史借阅表）

| 属性名         | 数据类型 | 完整性约束                    |
| ----------- | ---- | ------------------------ |
| readerid    | int  | PK, FK readers(readerid) |
| bookid      | int  | PK, FK books(bookid)     |
| borrow_date | date | PK                       |

## 3. **详细设计与实现**
### （1）读者借阅书籍
读者根据属性，输入查询内容，查询相关书籍。

若读者状态为“可借阅”，则点击上述查询结果，即可借阅。

借阅成功后，将在borrow表插入一条新记录，在此后触发器Insert_borrow将设置被借阅书籍的状态为“借阅中”。

将设置被借阅书籍的状态为“借阅中”。
```python
DELIMITER $$
CREATE TRIGGER Insert_borrow #触发器Insert_borrow
AFTER insert ON borrow # 在borrow表插入新记录后
FOR EACH ROW
BEGIN
    UPDATE books
    SET state = '借阅中'
    WHERE bookid = NEW.bookid; # 将books表中该图书的状态设为“借阅中”
END$$
DELIMITER ;
```
