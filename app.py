
from flask import Flask
from flask import render_template
from flask import request
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3


app = Flask(__name__)

admin_id = 'cap'
admin_password = '1234'
# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route to form used to add a new student to the database
@app.route("/register")
def enternew():
    return render_template("student.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=['POST', 'GET'])
def authenticate():
    if request.method == 'POST':
        # Retrieve form data
        firstname = request.form['username1']
        lastname = request.form['username2']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students2 WHERE firstname=? AND lastname=?', (firstname,lastname))
        user = cursor.fetchone()

        if(user):            
            # Check if the username and password match a record in the database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students2 WHERE firstname=? AND lastname=? AND password=?', (firstname,lastname,password))
            userandpass = cursor.fetchone()

            if(firstname == 'cap' and lastname == 'T' and password == admin_password):
                return render_template('adminlogin.html')            
            else:
                if userandpass:
                    # Successful authentication, redirect to selectvenue.html
                    print("Successful authentication")
                    conn.close()
                    return render_template('selectvenue.html')
                else:
                    # Authentication failed, render login.html with an error message
                    print("Authentication failed")
                    conn.close()
                    return render_template("login.html", error="Incorrect password. Please try again.")
        
        else:
            conn.close()
            return render_template("student.html", error="The user dose not exist. Please register")
        
    else:
            return render_template("login.html")


# Route to add a new record (INSERT) student data to the database
@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            firstname = request.form['username1']
            lastname = request.form['username2']
            email = request.form['email']
            password = request.form['password']
            cpassword = request.form['cpassword']
            # print(firstname)
            # print(lastname)
            # print(email)
            # print(password)
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students2 (firstname, lastname, email, password) VALUES (?,?,?,?)", (firstname, lastname, email, password))

                con.commit()
                msg = "You have successfully created an account. Please proceed to login."
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('login.html',msg=msg)

# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    # Connect to the SQLite3 datatabase and 
    # SELECT rowid and all Rows from the students table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    return render_template("list.html",rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form 
@app.route("/edit", methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id = request.form['id']
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM students WHERE rowid = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template("edit.html",rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST','GET'])
def editrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['rowid']
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            zip = request.form['zip']

            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE students SET name='"+nm+"', addr='"+addr+"', city='"+city+"', zip='"+zip+"' WHERE rowid="+rowid)

                con.commit()
                msg = "Record successfully edited in the database"
        except:
            con.rollback()
            msg = "Error in the Edit: UPDATE students SET name="+nm+", addr="+addr+", city="+city+", zip="+zip+" WHERE rowid="+rowid

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route used to DELETE a specific record in the database    
@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM students WHERE rowid="+rowid)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            return render_template('result.html',msg=msg)

@app.route("/redirect", methods=['POST','GET'])
def redirect():
    return render_template('adminlogin.html')
    
@app.route("/redirectvenue", methods=['POST','GET'])
def redirectvenue():
    current_day = datetime.now().strftime('%A') 
    selected_venue = request.args.get('venue')
    if selected_venue == 'Auditorium':
        return render_template('auditorium.html',current_day=current_day, get_auditorium_seat_availability = get_auditorium_seat_availability)
    elif selected_venue == 'parking_slot':
        return render_template('parking_slot.html')
    elif selected_venue == 'AC_building_1':
        return render_template('acfloor1.html', current_day=current_day, get_room_availability=get_room_availability, floor=1)
    elif selected_venue == 'AC_building_2':
        return render_template('acfloor2.html', current_day=current_day, get_room_availability=get_room_availability, floor=2)
    else: 
        return render_template('selectvenue.html')  

def get_room_availability(room_id, current_day, time_slot, floor):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    table_name = f'acFloor{floor}'
    
    query = f"SELECT {room_id} FROM {table_name} WHERE day = ? AND time_slot = ? AND {room_id} IS NOT NULL"
    cursor.execute(query, (current_day, time_slot))
    
    result = cursor.fetchone()
    
    if result:
        availability = result[0]
        return availability
    else:
        return None  # Return None if no availability is found

def get_auditorium_seat_availability(seat_number, row_label, current_day):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    row_label = chr(ord('a') + row_label - 1) # converts numbers to alphabets
    # seat_number = seat_number + 32 * (ord(row_label.lower()) - ord('a')) 

    query = "SELECT status FROM mainAuditorium WHERE seat_number = ? AND row_label = ? AND day = ?"
    cursor.execute(query, (seat_number, row_label, current_day))
    
    result = cursor.fetchone()
    
    if result:
        availability = result[0]
        return availability
    else:
        return None


@app.route("/selectacfloor", methods=['POST','GET'])
def selectacfloor():
    selected_venue = request.args.get('venue')
    current_day = datetime.now().strftime('%A')
    if selected_venue == '1':
        return render_template('acfloor1.html', current_day=current_day, get_room_availability=get_room_availability, floor=1)
    elif selected_venue == '2':
        return render_template('acfloor2.html', current_day=current_day, get_room_availability=get_room_availability, floor=2)
    else:
        return render_template('AC_building.html')

@app.route("/editvenue", methods=['POST'])
def editvenue():
    selected_venue = request.form.get('venue')
    current_day = request.form.get('day')
    print(selected_venue)
    print(current_day)
    if selected_venue is None or current_day is None:
        return render_template('adminlogin.html', error = "Invalid input please select again")
    
    # current_day = datetime.now().strftime('%A')    
    if selected_venue == 'Auditorium':
        return render_template('editauditorium.html',current_day=current_day, get_auditorium_seat_availability=get_auditorium_seat_availability)
    elif selected_venue == 'parking_slot':
        return render_template('editparking_slot.html')
    elif selected_venue == 'AC_floor1':
        return render_template('editAC_floor1.html', current_day=current_day, get_room_availability=get_room_availability, floor=1)
    elif selected_venue == 'AC_floor2':
        return render_template('editAC_floor2.html', current_day=current_day, get_room_availability=get_room_availability, floor=2)
    else: 
        return render_template('selectvenue.html')
    

def update_room_status(room_id, current_day, time_slot, floor, status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if(floor == 1) :
        query = f"UPDATE acFloor1 SET {room_id} = ? WHERE day = ? AND time_slot = ?"
        cursor.execute(query, (status, current_day, time_slot))
    elif(floor == 2):
        query = f"UPDATE acFloor2 SET {room_id} = ? WHERE day = ? AND time_slot = ?"
        cursor.execute(query, (status, current_day, time_slot))       
    conn.commit()
    conn.close()

@app.route("/changeACdatabase", methods=['POST'])
def changeACdatabase():
    # selected_venue = request.args.get('venue')
    # current_day = datetime.now().strftime('%A')
    if request.method == 'POST':
        room_statuses = request.form.getlist('mycheckbox')
        selected_day = request.form.get('dummy_variable')
        selected_floor = request.form.get('dummy_variable2')
        print(selected_floor)
        arr = [[0] * 4 for _ in range(9)]
        
        if(selected_floor == "1"):    
            for item in room_statuses:
                room_number, time_slot = item.split('_')
                room_id = 'r' + str(int(room_number) + 100)
                time_parts = time_slot.split('-')
                start_time = time_parts[0]
                first_number = int(start_time.split('am')[0]) if 'am' in start_time else int(start_time.split('pm')[0])
                
                if 'pm' in start_time and first_number != 12:  # Adjusting for 'pm' and 12pm
                    first_number += 12     
                arr[first_number - 9][int(room_number)-1] = 1            
                status = 'Occupied'
                update_room_status(room_id, selected_day, time_slot, 1, status)        
            for row_index, row in enumerate(arr):
                for col_index, element in enumerate(row):
                    if element == 0:
                        # Reconstruct time slot based on row_index
                        start_hour = row_index + 9
                        end_hour = start_hour + 1
                        
                        # Adjust time format for 'am' and 'pm' transitions
                        start_ampm = 'am' if start_hour < 12 else 'pm'
                        start_hour = start_hour % 12 if start_hour % 12 != 0 else 12
                        start_time = f"{start_hour}{start_ampm}"
                        
                        end_ampm = 'am' if end_hour < 12 else 'pm'
                        end_hour = end_hour % 12 if end_hour % 12 != 0 else 12
                        end_time = f"{end_hour}{end_ampm}"
                        
                        time_slot = f"{start_time}-{end_time}"
                        
                        room_number = col_index + 1  # Add 1 to convert back to room number
                        room_id = 'r' + str(room_number + 100)  # Construct room ID
                        update_room_status(room_id, selected_day, time_slot, 1, 'Vacant')
                        # update_room_status(room_id, selected_day, time_slot, 1, 'Vacant')

        
            return render_template('editAC_floor1.html', current_day=selected_day, get_room_availability=get_room_availability, floor=1)
        else:
            for item in room_statuses:
                room_number, time_slot = item.split('_')
                room_id = 'r' + str(int(room_number) + 200)
                time_parts = time_slot.split('-')
                start_time = time_parts[0]
                first_number = int(start_time.split('am')[0]) if 'am' in start_time else int(start_time.split('pm')[0])
                
                if 'pm' in start_time and first_number != 12:  # Adjusting for 'pm' and 12pm
                    first_number += 12     
                arr[first_number - 9][int(room_number)-1] = 1            
                status = 'Occupied'
                update_room_status(room_id, selected_day, time_slot, 2, status)        
            for row_index, row in enumerate(arr):
                for col_index, element in enumerate(row):
                    if element == 0:
                        # Reconstruct time slot based on row_index
                        start_hour = row_index + 9
                        end_hour = start_hour + 1
                        
                        # Adjust time format for 'am' and 'pm' transitions
                        start_ampm = 'am' if start_hour < 12 else 'pm'
                        start_hour = start_hour % 12 if start_hour % 12 != 0 else 12
                        start_time = f"{start_hour}{start_ampm}"
                        
                        end_ampm = 'am' if end_hour < 12 else 'pm'
                        end_hour = end_hour % 12 if end_hour % 12 != 0 else 12
                        end_time = f"{end_hour}{end_ampm}"
                        
                        time_slot = f"{start_time}-{end_time}"
                        
                        room_number = col_index + 1  # Add 1 to convert back to room number
                        room_id = 'r' + str(room_number + 200)  # Construct room ID
                        update_room_status(room_id, selected_day, time_slot, 2, 'Vacant')
                        # update_room_status(room_id, selected_day, time_slot, 2, 'Vacant')
            return render_template('editAC_floor2.html', current_day=selected_day, get_room_availability=get_room_availability, floor=2)

def update_seat_status(seat_num, row_label, current_day, status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Adjust seat number based on the row_label
    # row_label_numeric = ord(row_label.lower()) - ord('a') + 1
    # seat_num_adjusted = seat_num + 32 * (row_label_numeric - 1)

    query = f"UPDATE mainAuditorium SET status = ? WHERE day = ? AND row_label = ? AND seat_number = ?"
    cursor.execute(query, (status, current_day, row_label, seat_num))

    conn.commit()
    conn.close()

@app.route("/changeAudidatabase", methods=['POST'])
def changeAudidatabase():
    if request.method == 'POST':
        seat_statuses = request.form.getlist('mycheckbox') # only contains the entries of the filled seats
        current_day = request.form.get('dummy_variable')
        print(seat_statuses)
        arr = [[0] * 32 for _ in range(25)]
        
        for item in seat_statuses:
            status = 'Occupied'
            seat_num, row_num = item.split('_')
            row_label = chr(ord('a') + int(row_num) - 1)
            arr[int(row_num) - 1][int(seat_num) - 1] = 1
            update_seat_status(seat_num, row_label, current_day, status)
        print(arr)
        for row_index, row in enumerate(arr):
            for col_index, element in enumerate(row):
                if element == 0:
                    status = 'Vacant'
                    row_label = chr(row_index + ord('a'))
                    seat_num = col_index + 1
                update_seat_status(seat_num, row_label, current_day, status)
            
    
        return render_template('editauditorium.html',current_day=current_day, get_auditorium_seat_availability=get_auditorium_seat_availability)
