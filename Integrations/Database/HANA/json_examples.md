> Table Creation
```sql
CREATE COLUMN TABLE json_table (
    id INT PRIMARY KEY,
    data CLOB
);
```

> Inserting JSON Data
```sql
INSERT INTO json_table (id, data)
VALUES (1, '{"name": "John Doe", "age": 30, "city": "Berlin"}');
```

> Retrieving JSON Data
```sql
SELECT id, data
FROM json_table
WHERE id = 1;
```

> Updating JSON Data
```sql
UPDATE json_table
SET data = '{"name": "Yogananda Muthaiah", "age": 25, "city": "Munich"}'
WHERE id = 1;
```

> Deleting JSON Data
```sql
DELETE FROM json_table
WHERE id = 1;
```

> Working with JSON Functions
```sql
SELECT JSON_VALUE(data, '$.name') AS name
FROM json_table
WHERE id = 1;
```
