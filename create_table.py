
import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS students (name TEXT, addr TEXT, city TEXT, zip TEXT, password TEXT)')
print("Created table successfully!")

conn.execute('CREATE TABLE IF NOT EXISTS acFloor1 (r101 TEXT, r102 TEXT, r103 TEXT, r104 TEXT)')
print("Created table successfully!")

conn.execute('CREATE TABLE IF NOT EXISTS acFloor2 (r201 TEXT, r202 TEXT, r203 TEXT, r204 TEXT)')
print("Created table successfully!")

conn.close()