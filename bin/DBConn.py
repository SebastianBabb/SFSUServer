#!/usr/bin/python2

import configparser
import psycopg2  as pg # Allen, run on server: sudo apt-get install python-psycopg2

class DBConn:
    def __init__(self):
        # Parse config
#        config_file = configparser.ConfigParser()
#        config_file.read("db.ini")

#        database_section = config_file['sfsudroid-database']

#        hostname = database_section['Hostname']
#        database = database_section['Database']
#        username = database_section['Username']
#        password = database_section['Password']

        hostname = 'localhost'
        database = 'sfsudroid'
        username = 'sfsudroid'
        password = 'sfsuuser'

        # Connect to the database.
        try:
            self.db_connection = pg.connect(host=hostname, database=database,
                                       user=username, password=password)
            self.cursor = self.db_connection.cursor()

        except pg.DatabaseError as err:
            print "Error: ", err

    # Executes a query and returns a list of lists (rows).
    def query(self, sql):
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            return rows
        except pg.DatabaseError as err:
            print "Error: ", err
        
    # Executes insert/update sql.  Return true if succesful.
    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            if(self.db_connection):
                self.db_connection.commit()
                return True
            else:
                return False
        except pg.DatabaseError as err:
            print "Error: ", err

    # def copy(self, table, data):
        # # Implement me.


    # Close the database.  Returns true if succesful.
    def conn_close(self):
        if self.db_connection:
            return self.db_connection.close()

    # Ensure that the db was close on destruction.
    def __del__(self):
        self.conn_close()

# Example usage
def main():
        # Create an instace of the handler.
        db = DBConn()
        # Create a table.
        if db.insert("DROP TABLE IF EXISTS DBConnTest; CREATE TABLE DBConnTest(id SERIAL PRIMARY KEY, name VARCHAR, age INTEGER)"):
            print("User table created.")
        else:
            print("Error creating table.")

        # Insert a new record.
        if(db.insert("INSERT INTO DBConnTest( name, age) VALUES ('Andie', 3)")): 
            print("Record inserted.")
        else:
            print("Error inserting record.")

        # Query the database.
        rows = db.query("SELECT * FROM Users") 

        # Print query results as a un unprocessed list.
        for row in rows:
                print(row)

if __name__ == "__main__":
    main()
