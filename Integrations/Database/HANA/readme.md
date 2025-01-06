> Finding index and primary keys of tables

```sql
SELECT IFNULL(CONSTRAINT,'NUNIQUE'),
INDEX_NAME,COLUMN_NAME 
FROM INDEX_COLUMNS WHERE SCHEMA_NAME = '%s'
AND TABLE_NAME = '%s' 
ORDER BY INDEX_OID,POSITION
```

> Frequently used Tables
```sql
select * from TABLES; 
select * from M_TABLES;
select * from M_CS_TABLES;
select * from M_RS_TABLES;
select * from TABLE_COLUMNS;
select * from M_CS_ALL_COLUMNS;
select * from M_TEMPORARY_TABLES;
```

> Show details of users that have been logged-in
```sql
select * from "SYS"."USERS"
where "LAST_SUCCESSFUL_CONNECT" is not null
order by 9 desc;
```

> To get all Libraries
```sql
select to_char(definition) from public.libraries 
where schema_name='EXT';
```

> To get a complete list of error codes and their descriptions
```sql
SELECT * FROM M_ERROR_CODES ORDER BY CODE ASC;
```


> To get all DDL
```
call get_object_definition('<SCHEMA>','<TABLENAME>');
```

```sql
ALTER TABLE schema.table ADD PRIMARY KEY (column1,column2)
Check SQL PLAN Cache
select * from M_SQL_PLAN_CACHE
Check invalid custom DB views
select * from "SYS"."VIEWS"
where schema_name not like 'SAP%' and is_valid = 'FALSE';
Check inactive custom DB objects
select * from "_SYS_REPO"."INACTIVE_OBJECT"
where "PACKAGE_ID" not like 'sap%';
```

> Check which SAP language settings are being used by current user
 
```sql
select session_context('LOCALE_SAP'),
session_context('LOCALE') 
from dummy;## Search executed SQL statements, 
e.g. to find out who deleted a table
select * from "SYS"."M_EXECUTED_STATEMENTS" 
where "STATEMENT_STRING" LIKE 'DROP TABLE%';
```

> Show custom settings within global.ini and indexserver.ini
```sql
select * from "SYS"."M_INIFILE_CONTENTS"
where ("LAYER_NAME" = 'SYSTEM' or "HOST" <> ") 
and ("FILE_NAME" = 'global.ini' 
or "FILE_NAME" = 'indexserver.ini');
```

> Show assigned user roles
```sql
select * from "SYS"."GRANTED_ROLES"
where "GRANTEE_TYPE" = 'USER';
```

> Show assigned repository privileges 
```sql
select * from "SYS"."GRANTED_PRIVILEGES"
where object_type = 'REPO';
```

> Show objects owned by non-system users
```sql
select * from "SYS"."OWNERSHIP"
where owner_name not like 'SAP%' and owner_name not like '%SYS%'
order by 1,2;
```

> Show Corresponding Tables referring to which Schema
 
```sql
SELECT BASE_SCHEMA_NAME, BASE_OBJECT_NAME,DEPENDENT_SCHEMA_NAME,
DEPENDENT_OBJECT_NAME,DEPENDENT_OBJECT_TYPE
FROM "SYS"."OBJECT_DEPENDENCIES"
WHERE BASE_SCHEMA_NAME = 'TCMP' /* <== Schema Name */
AND BASE_OBJECT_NAME = 'CS_SALESORDER' /* <== Table Name */
``` 

> Analyze expensive statement trace
```sql
select
to_varchar("STATEMENT_START_TIME",'DD.MM.YYYY') "EXEC_DATE",
to_varchar("STATEMENT_START_TIME",'HH24:MI:SS') "EXEC_TIME",
to_int("DURATION_MICROSEC"/1000000) "DURATION_S",
to_decimal("MEMORY_SIZE"/1073741824,10,1) "MEM_GB",
"RECORDS",
"DB_USER",
"APP_USER",
"APPLICATION_NAME",
"STATEMENT_STRING",
length("STATEMENT_STRING") "SQL_LENGTH",
OCCURRENCES_REGEXPR('JOIN' FLAG 'i' IN "STATEMENT_STRING") "JOIN",
OCCURRENCES_REGEXPR('CASE' FLAG 'i' IN "STATEMENT_STRING") "DISTINCT",
"ERROR_TEXT",
"PARAMETERS"
from "SYS"."M_EXPENSIVE_STATEMENTS"
where "OPERATION" in 
('INSERT','SELECT','AGGREGATED_EXECUTION') –exclude background activity
and "RECORDS" > 0
and to_varchar("STATEMENT_START_TIME", 'YYYYMMDD') = current_date
and to_int(to_varchar("STATEMENT_START_TIME",'HH24′)) 
between 8 and 17 –business hours
order by 3 desc;
```

```sql
select * from M_PREPARED_STATEMENTS; 
select * from M_ACTIVE_STATEMENTS;
select * from M_EXPENSIVE_STATEMENTS;
```

> RECLAIM Storage Space
```sql
ALTER SYSTEM RECLAIM DATAVOLUME 105 DEFRAGMENT.
```

> Most Common Functions used in Implementation
```sql
CREATE TABLE "ZTABLE"
(
  "MANDT" NVARCHAR(000003) DEFAULT '000' NOT NULL,
  "RELID" NVARCHAR(000002) DEFAULT ' ' NOT NULL,
  "FIELD1" NVARCHAR(000010) DEFAULT '0' NOT NULL,
  "FIELD2" NVARCHAR(000010) DEFAULT '0' NOT NULL,
  PRIMARY KEY ("MANDT", "RELID")
);
```
 
```sql
SELECT SESSION_USER "session user" FROM DUMMY;
SELECT TO_DATE('2010-01-12', 'YYYY-MM-DD') "to date" 
FROM DUMMY;
SELECT TRIM ('a' FROM 'aaa123456789aa') "trim both" FROM DUMMY;
SELECT CURRENT_DATE "current date" FROM DUMMY;
SELECT ISOWEEK (TO_DATE('2011-05-30', 'YYYY-MM-DD')) "isoweek" FROM DUMMY;
SELECT DAYS_BETWEEN (TO_DATE ('2009-12-05', 'YYYY-MM-DD'), TO_DATE('2010-01-05', 'YYYY-MM-DD')) "days between" FROM DUMMY;
SELECT UPPER ('Ant') "uppercase" FROM DUMMY; 
SELECT CONCAT ('C', 'at') "concat" FROM DUMMY; 
SELECT FLOOR (14.5) "floor" FROM DUMMY; 
SELECT TO_DECIMAL(7654321.888888, 10, 3) "to decimal" FROM DUMMY; 
SELECT REPLACE ('DOWNGRADE DOWNWARD','DOWN', 'UP') "replace" FROM DUMMY;
SELECT RTRIM ('endabAabbabab','ab') "rtrim" FROM DUMMY;
SELECT RIGHT('HI0123456789', 20) "right" FROM DUMMY;
SELECT DAYNAME ('2011-05-30') "dayname" FROM DUMMY;
SELECT WEEK ('2017-01-02') FROM DUMMY; SELECT LENGTH ('length in char') "length" FROM DUMMY; 
SELECT SUBSTRING ('1234567890',4,2) "substring" FROM DUMMY; 
SELECT WEEKDAY (TO_DATE ('2010-12-31', 'YYYY-MM-DD')) "week day" FROM DUMMY; 
SELECT TO_VARCHAR (TO_DATE('2009-12-31'), 'YYYY/MM/DD') "to varchar" FROM DUMMY; 
SELECT YEARS_BETWEEN(TO_DATE('2001-01-01'), TO_DATE('2003-03-14')) "years_between" FROM DUMMY; 
SELECT YEAR (TO_DATE ('2011-05-30', 'YYYY-MM-DD')) "year" FROM DUMMY; 
SELECT MONTH ('2011-05-30') "month" FROM DUMMY; SELECT NOW () "now" FROM DUMMY;
SELECT LAST_DAY (TO_DATE('2010-01-04', 'YYYY-MM-DD')) "last day" FROM DUMMY;
SELECT EXTRACT (YEAR FROM TO_DATE ('2010-01-04', 'YYYY-MM-DD')) "extract" FROM DUMMY;
SELECT DAYOFYEAR ('2021-05-30') "dayofyear" FROM DUMMY;
``` 


```sql
SELECT LANGUAGE(CONTENT) FROM TABLE;
SELECT IFNULL (NULL, 'same') "ifnull" FROM DUMMY;
``` 

```sql
SELECT ProdName, Type, Sales,
RANK() OVER ( PARTITION BY ProdName ORDER BY Sales DESC ) AS Rank
FROM ProductSales
ORDER BY ProdName, Type;
``` 

```sql
SET SCHEMA "EXT"; 
CREATE TABLE MY_DATES (FCID NVARCHAR(2), STARTDATE DATE, ENDDATE DATE); 
INSERT INTO MY_DATES VALUES ('01', '2014-01-01', '2014-02-14'); 
INSERT INTO MY_DATES VALUES ('01', '2014-04-01', '2014-05-14'); 
INSERT INTO MY_DATES VALUES ('01', '2014-07-01', '2014-08-05'); 
INSERT INTO MY_DATES VALUES ('01', '2014-10-01', '2014-10-30'); 
SELECT WORKDAYS_BETWEEN(FCID, STARTDATE, ENDDATE) "production duration" 
FROM MY_DATES;
``` 

```sql
SELECT JSON_VALUE('{"item1":10}', '$.item1') AS "value" FROM DUMMY;
SELECT * FROM
XMLTABLE('/doc/item' PASSING
'<doc>
<item><id>10</id><name>Box</name></item>
<item><id>20</id><name>Jar</name></item>
</doc>'
COLUMNS 
ID INT PATH 'id', 
NAME VARCHAR(20) PATH 'name'
) as XTABLE;
CREATE FUNCTION func_add_mul(x Double, y Double) 
RETURNS result_add Double, result_mul Double 
LANGUAGE SQLSCRIPT READS SQL DATA AS
BEGIN
result_add := :x + :y;
result_mul := :x * :y;
END;
```

