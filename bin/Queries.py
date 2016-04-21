#!/usr/bin/env python2

from DBConn import DBConn

# Create a db handler.
db = DBConn();

if(db):
    # Query the database.
    rows = db.query("SELECT * FROM \"Department\"") 
else:
    print("Connected to database")


#Print query results as a un unprocessed list.
if(rows):
    for row in rows:
        print(row)

if(db.conn_close()):
    print("Database was not closed")
else:
    print("Database is closed")
