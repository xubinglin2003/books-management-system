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

### （2）读者归还书籍
读者若归还书籍，则borrow表中的相应记录会被删除，在此前触发器After_book_returned将在history表中插入相应的历史借阅记录，在books表中更新已归还图书的状态为“可借阅”
```python
DELIMITER $$
CREATE TRIGGER After_book_returned # 触发器After_book_returned
before delete ON borrow # 在borrow表删除记录之前
FOR EACH ROW
BEGIN
    # 在history表中插入历史借阅记录
	INSERT INTO history VALUES (old.readerid, old.bookid, old.borrow_date);
    # 在books表中更新已归还图书的状态为“可借阅”
	update books set state = '可借阅' where books.bookid = old.bookid;
END$$
DELIMITER ;
```

### （3）每日检查借阅图书是否逾期
读者的当前借阅中有应还日期due_date，建立事务check_overdue_event，每天进行检查，若到了归还日期，则该借阅书籍的状态应更新为“已逾期”。  
若读者当前借阅的书籍中有状态变“已逾期”的，则读者不能借阅新书，建立触发器Update_borrow_state将其状态应更新为“不可借阅”。
```python
# 事物check_overdue_event，每天检查借阅图书是否逾期
SET GLOBAL event_scheduler = ON;
DELIMITER //
CREATE PROCEDURE check_overdue() 
BEGIN
    # 若应还日期等于系统日期，则将其状态更新为“已逾期”
    UPDATE db_library.borrow
    SET state = '已逾期' 
    WHERE due_date = CURDATE() AND state <> '已逾期'; 
END; //
DELIMITER ;
CREATE EVENT check_overdue_event
ON SCHEDULE EVERY 1 DAY  # 每天执行check_overdue()
DO
  CALL check_overdue();
# 触发器Update_borrow_state：如果该读者借阅的图书状态变为已逾期，则该读者不可借阅
DELIMITER $$
CREATE TRIGGER Update_borrow_state
AFTER UPDATE ON borrow # 在borrow表发生更新后
FOR EACH ROW
BEGIN
    # 如果借阅图书的状态更新为“已逾期”，则该读者的状态应更新为“不可借阅”
    IF (new.state = '已逾期') THEN
        UPDATE readers
        SET state = '不可借阅'
        WHERE readerid = new.readerid;
    END IF;
END$$
DELIMITER ;
```

## 4. **数据库测试**
### （1）用户登录界面（最初设想为霍格沃茨图书馆主题）
![image](https://github.com/user-attachments/assets/17d965bf-0cd8-4bb8-8a04-fb53f9110318)
### （2）读者检索、借阅图书界面
以reader1账户登录，查询“类别”为“魔法学”的书籍。  
![image](https://github.com/user-attachments/assets/792310ce-af1d-4a1b-9ecd-f56292178cf3)  
点击“借阅”按钮，由于reader1的状态为“不可借阅”，消息框提示不可借阅图书。  
![image](https://github.com/user-attachments/assets/39014762-528e-4fdb-ae47-d643fe8083f0)  
以reader2账户登录，点击“借阅”按钮，可成功借阅《神奇的魁地奇球》。  
![image](https://github.com/user-attachments/assets/e8484d7a-6211-49fc-bdab-43225d26912f)
### （3）读者个人中心界面
以reader2账户登录，即可看到上文借阅的图书记录，以及借阅历史  
![image](https://github.com/user-attachments/assets/ca05b836-5cb3-4d01-a29e-77335955ac84)  
![image](https://github.com/user-attachments/assets/27c093d6-bc95-4562-97d3-2b8145177b36)  
以reader1账户登录，可查看已逾期图书及对应罚款金额  
![image](https://github.com/user-attachments/assets/933b5f8d-adfe-45e8-96e2-96601e7ffd2c)
### （4）图书管理员图书添加界面
以librarian账户登录，输入新增图书信息，添加成功
![image](https://github.com/user-attachments/assets/6542caf5-fa8e-4e47-bcec-eec93dff3a5c)
### （5）图书管理员图书删改界面
图书管理员先进行图书查询，点击“删除”按钮，消息框二次确认是否删除。  
点击“修改”按钮，则选中了该图书。填写下方“修改信息”，点击“确认修改”，修改成功。
![image](https://github.com/user-attachments/assets/395f8dc6-c23d-4e2c-9f8c-ffebcf1bb753)
![image](https://github.com/user-attachments/assets/7856bd37-6492-42f9-8580-e2510f755c25)
![image](https://github.com/user-attachments/assets/bd8cf02e-f62d-474f-acbb-f70456561a92)
![image](https://github.com/user-attachments/assets/a07b04e0-ac22-4df8-93b5-63aee6c8402c)

