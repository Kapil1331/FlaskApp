import sqlite3
import random

conn = sqlite3.connect('database.db')
print("Connected to database successfully")
# Create table for the users database

conn.execute('CREATE TABLE IF NOT EXISTS students (name TEXT, addr TEXT, city TEXT, zip TEXT, password TEXT)')
print("Created table successfully!")

conn.execute('CREATE TABLE IF NOT EXISTS students2 (firstname TEXT, lastname TEXT, email TEXT, password TEXT, mis INTEGER)')
print("Created table2 successfully!")

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


# Create table for Main Auditorium
conn.execute('CREATE TABLE IF NOT EXISTS mainAuditorium (seat_number INTEGER, row_label TEXT, day TEXT, status TEXT)')
print("Created table for Main Auditorium successfully!")

# Define the number of seats and rows in the auditorium
total_seats = 800
total_rows = 25
rows_labels = [chr(ord('a') + i) for i in range(total_rows)]  # ['a', 'b', 'c', ...]

# Inserting random data into the mainAuditorium table
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for day in days:
    for seat_num in range(1, total_seats + 1):
        seat_num_adjusted = (seat_num - 1) % 32 + 1  # Adjust seat number to cycle from 1 to 32
        row_label = rows_labels[(seat_num - 1) // (total_seats // total_rows)]
        status = random.choice(['Occupied', 'Vacant'])
        conn.execute(f"INSERT INTO mainAuditorium (seat_number, row_label, day, status) VALUES ({seat_num_adjusted}, '{row_label}', '{day}', '{status}')")


conn.commit()
conn.close()