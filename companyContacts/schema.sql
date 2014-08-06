DROP TABLE IF EXISTS Company;
create table Company (
  CompanyID integer primary key autoincrement,
  Name text not null,
  ContactName text not null,
  ContactEmail text not null,
  ContactPhoneNumber text,
  Description text
);

DROP TABLE IF EXISTS Events;
create table Events (
	EventID integer primary key autoincrement,
	CompanyKey integer,
	Name text,
	Year number
);