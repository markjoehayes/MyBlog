import sqlite3

# open a connection between python script and database.db to create it
connection = sqlite3.connect('database.db')

# open the schema.sql to read what is inside it
with open('schema.sql') as f:
    connection.executescript(f.read())

# make the cursor to execute what inside the schema in database
cur = connection.cursor()

connection.commit()   # commits the changes to the db
connection.close()    # closes the connection
