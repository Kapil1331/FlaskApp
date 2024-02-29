
import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS students (name TEXT, addr TEXT, city TEXT, zip TEXT, password TEXT)')
print("Created table successfully!")

import random

# Create table for AC floor 1
conn.execute('CREATE TABLE IF NOT EXISTS acFloor1 (day TEXT, time_slot TEXT, r101 TEXT, r102 TEXT, r103 TEXT, r104 TEXT)')
print("Created table for AC floor 1 successfully!")

# Inserting random data into the acFloor1 table
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
time_slots = ['9am-10am', '10am-11am', '11am-12pm', '12pm-1pm', '1pm-2pm', '2pm-3pm', '3pm-4pm', '4pm-5pm', '5pm-6pm']

for day in days:
    for time_slot in time_slots:
        occupancy_data = [random.choice(['Occupied', 'Vacant']) for _ in range(4)]
        conn.execute(f"INSERT INTO acFloor1 (day, time_slot, r101, r102, r103, r104) VALUES ('{day}', '{time_slot}', '{occupancy_data[0]}', '{occupancy_data[1]}', '{occupancy_data[2]}', '{occupancy_data[3]}')")

# Create table for AC floor 2
conn.execute('CREATE TABLE IF NOT EXISTS acFloor2 (day TEXT, time_slot TEXT, r201 TEXT, r202 TEXT, r203 TEXT, r204 TEXT)')
print("Created table for AC floor 2 successfully!")

# Inserting random data into the acFloor2 table
for day in days:
    for time_slot in time_slots:
        occupancy_data = [random.choice(['Occupied', 'Vacant']) for _ in range(4)]
        conn.execute(f"INSERT INTO acFloor2 (day, time_slot, r201, r202, r203, r204) VALUES ('{day}', '{time_slot}', '{occupancy_data[0]}', '{occupancy_data[1]}', '{occupancy_data[2]}', '{occupancy_data[3]}')")

# Commit the changes
conn.commit()

conn.close()