# 创建模式
create schema bms; # books-management system
use bms;

# 创建表
create table books(
bookid int auto_increment primary key,
title varchar(255),
author varchar(255),
category char(20),
state char(10) check (state in ('借阅中', '可借阅'))
);

create table readers(
readerid int auto_increment primary key,
reader_name varchar(255),
reader_password varchar(255),
state char(20) check (state in ('不可借阅', '可借阅'))
);

create table borrow(
readerid int,
bookid int,
borrow_date date,
due_date date,
state char(10) check (state in ('借阅中', '已逾期')),
primary key (readerid, bookid, borrow_date),
constraint fk_readers_borrow foreign key (readerid) references readers(readerid),
constraint fk_books_borrow foreign key (bookid) references books(bookid)
);

create table history(
readerid int,
bookid int,
borrow_date date, 
primary key (readerid, bookid, borrow_date),
constraint fk_readers_history foreign key (readerid) references readers(readerid),
constraint fk_books_history foreign key (bookid) references books(bookid)
);


# 创建事务与触发器

# 事务check_overdue：每天检查是否有图书逾期未还
SET GLOBAL event_scheduler = ON;

DELIMITER //
CREATE PROCEDURE check_overdue()
BEGIN
    -- 假设有一个名为library_books的表，其中包含due_date列
    UPDATE db_library.borrow
    SET state = '已逾期'  -- 假设有一个状态列来标记逾期
    WHERE due_date = CURDATE() AND state <> '已逾期';
END; //
DELIMITER ;

CREATE EVENT check_overdue_event
ON SCHEDULE EVERY 1 DAY  -- 每天执行
DO
  CALL check_overdue();

# 触发器Update_borrow_state：如果该读者借阅的图书状态变为已逾期，则该读者不可借阅
DELIMITER $$
CREATE TRIGGER Update_borrow_state
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    IF (new.state = '已逾期') THEN
        UPDATE readers
        SET state = '不可借阅'
        WHERE readerid = new.readerid;
    END IF;
END$$
DELIMITER ;

# 触发器Insert_borrow：如果读者刚借阅了某书，则该书的状态设为借阅中
DELIMITER $$
CREATE TRIGGER Insert_borrow
AFTER insert ON borrow
FOR EACH ROW
BEGIN
    UPDATE books
    SET state = '借阅中'
    WHERE bookid = NEW.bookid;
END$$
DELIMITER ;

# 触发器Return：如果读者还书了，则borrow中的记录删除，移至history，且将books中书的状态设为可借阅
DELIMITER $$
CREATE TRIGGER After_book_returned
before delete ON borrow 
FOR EACH ROW
BEGIN
	INSERT INTO history VALUES (old.readerid, old.bookid, old.borrow_date);
	update books set state = '可借阅' where books.bookid = old.bookid;
END$$
DELIMITER ;

# 导入books数据
set global local_infile=1;
LOAD DATA LOCAL INFILE 'C:/Users/LJ/Desktop/code/MyCode/books-management-system/books.csv' # 此处请补充本地books.csv路径
INTO TABLE bms.books
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n' 
IGNORE 1 ROWS;

# 插入readers数据
insert into readers (readerid, reader_name, reader_password, state) values
(2001, 'reader1', '111', '可借阅'),
(2002, 'reader2', '222', '可借阅'),
(2003, 'reader3', '333', '可借阅');

# 插入borrow数据
INSERT INTO borrow (readerid, bookid, borrow_date, due_date, state) VALUES
(2001, 1047, '2024-02-15', DATE_ADD('2024-02-15', INTERVAL 30 DAY), '已逾期'),
(2001, 1083, '2024-03-08', DATE_ADD('2024-03-08', INTERVAL 30 DAY), '已逾期'),
(2002, 1010, '2024-01-29', DATE_ADD('2024-01-29', INTERVAL 30 DAY), '已逾期'),
(2003, 1065, '2024-04-23', DATE_ADD('2024-04-23', INTERVAL 30 DAY), '借阅中'),
(2003, 1092, '2024-05-05', DATE_ADD('2024-05-05', INTERVAL 30 DAY), '借阅中');

# 创建和授权用户
create user 'librarian'@'localhost' identified by '123';
grant all privileges on bms.* to 'librarian'@'localhost';

create user 'reader1'@'localhost' identified by '111';
create user 'reader2'@'localhost' identified by '222';
create user 'reader3'@'localhost' identified by '333';
#TODO 用户的授权
