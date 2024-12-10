use db_library;

/*
create table books(
bookid int auto_increment primary key,
title varchar(255),
author varchar(255),
category char(20));

alter table books
add column state char(10) check (state in ('借阅中', '可借阅'))；
*/


/*
create table readers(
readerid int auto_increment primary key,
reader_name varchar(255),
reader_password varchar(255));

alter table readers
add column state char(20) check (state in ('不可借阅', '可借阅'));

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
*/

insert into borrow values(2001, 1047, '2024-02-15', DATE_ADD('2024-02-15', INTERVAL 30 DAY), '已逾期');
insert into borrow values(2001, 1083, '2024-03-08', DATE_ADD('2024-03-08', INTERVAL 30 DAY), '已逾期');
insert into borrow values(2002, 1010, '2024-01-29', DATE_ADD('2024-01-29', INTERVAL 30 DAY), '已逾期');
insert into borrow values(2003, 1065, '2024-04-23', DATE_ADD('2024-04-23', INTERVAL 30 DAY), '借阅中');
insert into borrow values(2003, 1092, '2024-05-05', DATE_ADD('2024-05-05', INTERVAL 30 DAY), '借阅中');

/*
create table history(
readerid int,
bookid int,
borrow_date date, 
primary key (readerid, bookid, borrow_date),
constraint fk_readers_history foreign key (readerid) references readers(readerid),
constraint fk_books_history foreign key (bookid) references books(bookid)
);
*/



