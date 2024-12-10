use db_library;

/*
select borrow.bookid, books.title, borrow.borrow_date, borrow.due_date
from borrow, books
where borrow.state = '已逾期' and borrow.bookid = books.bookid and
borrow.readerid = (select readerid
from readers
where reader_name = 'reader1');
*/

/*
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
*/

/*
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
*/

/*
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
*/


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



