#!/usr/bin/env python2

from DBConn import DBConn

# Create a db handler.
db = DBConn();

if(db):
    # Query the database.
    cols, rows = db.query("SELECT DISTINCT course_name FROM \"Courses\" ORDER BY course_name ASC") 
else:
    print("Connected to database")


#Print query results as a un unprocessed list.
if(rows):
    for row in list(rows):
        print(row)

if(db.conn_close()):
    print("Database was not closed")
else:
    print("Database is closed")
