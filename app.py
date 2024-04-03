
from flask import Flask
from flask import render_template, Response, request, make_response
from flask import request,jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_qrcode import QRcode
import sqlite3
import pdfkit
import random

app = Flask(__name__)
QRcode(app)
admin_id = 'cap'
admin_password_hash = generate_password_hash('1234')  # Hash the admin password

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def enternew():
    return render_template("student.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

@app.route("/login")
def login():
    return render_template("login.html")

# @app.route("/authenticate", methods=['POST', 'GET'])
# def authenticate():
#     if request.method == 'POST':
#         # Retrieve form data
#         firstname = request.form['username1']
#         lastname = request.form['username2']
#         mis = request.form['mis']
#         password = request.form['password']

#         # Connect to the database
#         conn = sqlite3.connect('database.db')
#         cursor = conn.cursor()
#         cursor.execute('SELECT * FROM students2 WHERE firstname=? AND lastname=?', (firstname,lastname))
#         user = cursor.fetchone()
#         if(firstname == 'cap' and lastname == 'T' and password == admin_password):
#             return render_template('adminlogin.html')   

#         if(user):            
#             # Check if the username and password match a record in the database
#             conn = sqlite3.connect('database.db')
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM students2 WHERE firstname=? AND lastname=? AND password=? AND mis=?', (firstname,lastname,password,mis))
#             userandpass = cursor.fetchone()

#             if(firstname == 'cap' and lastname == 'T' and password == admin_password):
#                 return render_template('adminlogin.html')            
#             else:
#                 if userandpass:
#                     # Successful authentication, redirect to selectvenue.html
#                     print("Successful authentication")
#                     conn.close()
#                     return render_template('selectvenue.html',mis = mis)
#                 else:
#                     # Authentication failed, render login.html with an error message
#                     print("Authentication failed")
#                     conn.close()
#                     return render_template("login.html", error="Incorrect password/MIS. Please try again.")
        
#         else:
#             conn.close()
#             return render_template("student.html", error="The user dose not exist. Please register")
        
#     else:
#             return render_template("login.html")

@app.route("/authenticate", methods=['POST', 'GET'])
def authenticate():
    if request.method == 'POST':
        firstname = request.form['username1']
        lastname = request.form['username2']
        mis = request.form['mis']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students2 WHERE firstname=? AND lastname=?', (firstname, lastname))
        user = cursor.fetchone()
        if firstname == 'cap' and lastname == 'T' and check_password_hash(admin_password_hash, password):
            return render_template('adminlogin.html')
        if user:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students2 WHERE firstname=? AND lastname=? AND mis=?', (firstname, lastname, mis))
            userandpass = cursor.fetchone()

            if userandpass and check_password_hash(userandpass[3], password):  #Checking the password
                print("Successful authentication")
                conn.close()
                return render_template('selectvenue.html', mis=mis)
            else:
                print("Authentication failed")
                conn.close()
                return render_template("login.html", error="Incorrect password/MIS. Please try again.")
        else:
            conn.close()
            return render_template("student.html", error="The user does not exist. Please register")
    else:
        return render_template("login.html")

# @app.route("/addrec", methods = ['POST', 'GET'])
# def addrec():
#     if request.method == 'POST':
#         try:
#             firstname = request.form['username1']
#             lastname = request.form['username2']
#             email = request.form['email']
#             mis = request.form['mis']
#             password = request.form['password']
#             cpassword = request.form['cpassword']
#             with sqlite3.connect('database.db') as con:
#                 cur = con.cursor()
#                 cur.execute("INSERT INTO students2 (firstname, lastname, email, password, mis) VALUES (?,?,?,?,?)", (firstname, lastname, email, password, mis))

#                 con.commit()
#                 msg = "You have successfully created an account. Please proceed to login."
#         except:
#             con.rollback()
#             msg = "Error in the INSERT"

#         finally:
#             con.close()
#             return render_template('login.html',msg=msg)

class Database:
    @staticmethod
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
    @staticmethod
    def get_auditorium_seat_availability(seat_number, row_label, current_day):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        row_label = chr(ord('a') + int(row_label) - 1) # converts numbers to alphabets
        # seat_number = seat_number + 32 * (ord(row_label.lower()) - ord('a')) 

        query = "SELECT status FROM mainAuditorium WHERE seat_number = ? AND row_label = ? AND day = ?"
        cursor.execute(query, (seat_number, row_label, current_day))
        
        result = cursor.fetchone()
        
        if result:
            availability = result[0]
            return availability
        else:
            return None
    @staticmethod
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
    @staticmethod
    def update_seat_status(seat_num, row_label, current_day, status):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # row_label_numeric = ord(row_label.lower()) - ord('a') + 1
        # seat_num_adjusted = seat_num + 32 * (row_label_numeric - 1)

        query = f"UPDATE mainAuditorium SET status = ? WHERE day = ? AND row_label = ? AND seat_number = ?"
        cursor.execute(query, (status, current_day, row_label, seat_num))

        conn.commit()
        conn.close()

@app.route("/addrec", methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            firstname = request.form['username1']
            lastname = request.form['username2']
            email = request.form['email']
            mis = request.form['mis']
            password = request.form['password']
            cpassword = request.form['cpassword']
            if password != cpassword:
                return render_template('student.html', error="Passwords do not match")
            else:
                # Hash the password before storing
                hashed_password = generate_password_hash(password)
                with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO students2 (firstname, lastname, email, password, mis) VALUES (?,?,?,?,?)",
                                (firstname, lastname, email, hashed_password, mis))
                    con.commit()
                    msg = "You have successfully created an account. Please proceed to login."
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            return render_template('login.html', msg=msg)

@app.route('/list')
def list():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")

    rows = cur.fetchall()
    con.close()
    return render_template("list.html",rows=rows)

@app.route("/edit", methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            id = request.form['id']
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM students WHERE rowid = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            return render_template("edit.html",rows=rows)

@app.route("/editrec", methods=['POST','GET'])
def editrec():
    if request.method == 'POST':
        try:
            rowid = request.form['rowid']
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            zip = request.form['zip']

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
            return render_template('result.html',msg=msg)

@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
            rowid = request.form['id']
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


@app.route("/redirectvenue", methods=['POST'])
def redirectvenue():
    current_day = datetime.now().strftime('%A') 
    mis = request.form.get('misno')
    selected_venue = request.form.get('venue')
    # print(selected_venue)
    if not selected_venue:
        error = "No venue selected. Please select one"
        return render_template('selectvenue.html', error = error)  
    if selected_venue == 'Auditorium':
        return render_template('auditorium.html',current_day=current_day, get_auditorium_seat_availability = Database.get_auditorium_seat_availability, mis = mis)
    elif selected_venue == 'parking_slot':
        return render_template('parking_slot.html',current_day=current_day, get_auditorium_seat_availability = Database.get_auditorium_seat_availability, mis = mis)
    elif selected_venue == 'AC_building_1':
        return render_template('acfloor1.html', current_day=current_day, get_room_availability=Database.get_room_availability, floor=1, mis = mis)
    elif selected_venue == 'AC_building_2':
        return render_template('acfloor2.html', current_day=current_day, get_room_availability=Database.get_room_availability, floor=2, mis = mis)
    else: 
        return render_template('selectvenue.html')  

@app.route("/seatbook")


@app.route("/bookseat", methods=['POST'])
def bookseat():
    # seat = request. get_json()

    # seat = request.form.get('formValues')
    # print(seat)
    # row = seat[0]
    # column = seat[1]
    # mis = seat[2]
    # current_day = seat[3]
    mis = request.form.get('misno')
    row = request.form.get('row')
    column = request.form.get('column')
    current_day =  request.form.get('day')
    if not row or not column:
        error = "Invalid seat number, re-enter"
        return render_template("auditorium.html", current_day = current_day, mis = mis, error = error, get_auditorium_seat_availability = Database.get_auditorium_seat_availability)

    if(int(row) > 25 or int(row) < 1 or int(column) > 32 or int(column) < 1):
        error = "Invalid seat number, re-enter"
        return render_template("auditorium.html", current_day = current_day, mis = mis, error = error, get_auditorium_seat_availability = Database.get_auditorium_seat_availability)
    receiptnum = (int(mis) // 5000) + int(row) + int(column) + random.randint(1,20)
    
    if Database.get_auditorium_seat_availability(column, row, current_day) == 'Occupied':
        error = "The seat you have booked is already Occupied! Select another seat."
        return render_template("auditorium.html", current_day = current_day, mis = mis, error = error, get_auditorium_seat_availability = Database.get_auditorium_seat_availability)

    row_label = chr(int(row) + 96)
    print(row_label)
    if(int(row) > 25 or int(row) < 1 or int(column) > 32 or int(column) < 1):
        error = "Invalid seat number, re-enter"
        return render_template("auditorium.html", current_day = current_day, mis = mis, error = error, get_auditorium_seat_availability = Database.get_auditorium_seat_availability)        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    table_name = "mainAuditorium"
    query = f"UPDATE {table_name} SET status = 'Occupied' WHERE day = ? AND row_label = ? AND seat_number = ?"
    cursor.execute(query, (current_day, row_label, column))
    conn.commit()
    conn.close()
    pdf = "positive"
    return render_template("auditorium.html", receiptnum = receiptnum ,current_day = current_day, mis = mis, pdf = pdf, get_auditorium_seat_availability = Database.get_auditorium_seat_availability, column = column , row = row)        

@app.route("/generate_pdf", methods=['POST'])
def generate_pdf():
    mis = request.form.get('misno')
    row = request.form.get('row')
    column = request.form.get('column')
    current_day =  request.form.get('day')
    row_label = chr(int(row) + 96)
    receiptnum = request.form.get('receiptnum')
    # receiptnum = (int(mis) // 5000) + int(row) + int(column) + random.randint(1,20)
    html = f"<html><body><h1>Receipt number : {receiptnum}<h1/><h1>{mis} : You request has been processed</h1><h1>Your booked seat is : {row}-{column}</h1></body></html>"  
    pdf = pdfkit.from_string(html, False, configuration=pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf'))
    headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f"attachment;filename={mis}_receipt.pdf"
    }

    response = Response(pdf, headers=headers)
    return response


@app.route("/selectacfloor", methods=['POST','GET'])
def selectacfloor():
    selected_venue = request.args.get('venue')
    current_day = datetime.now().strftime('%A')
    if selected_venue == '1':
        return render_template('acfloor1.html', current_day=current_day, get_room_availability=Database.get_room_availability, floor=1)
    elif selected_venue == '2':
        return render_template('acfloor2.html', current_day=current_day, get_room_availability=Database.get_room_availability, floor=2)
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
        return render_template('editauditorium.html',current_day=current_day, get_auditorium_seat_availability=Database.get_auditorium_seat_availability)
    elif selected_venue == 'parking_slot':
        return render_template('editparking_slot.html',current_day=current_day, get_auditorium_seat_availability=Database.get_auditorium_seat_availability)
    elif selected_venue == 'AC_floor1':
        return render_template('editAC_floor1.html', current_day=current_day, get_room_availability=Database.get_room_availability, floor=1)
    elif selected_venue == 'AC_floor2':
        return render_template('editAC_floor2.html', current_day=current_day, get_room_availability=Database.get_room_availability, floor=2)
    else: 
        return render_template('selectvenue.html')
    

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
                Database.update_room_status(room_id, selected_day, time_slot, 1, status)        
            for row_index, row in enumerate(arr):
                for col_index, element in enumerate(row):
                    if element == 0:
                        # Reconstruct time slot based on row_index
                        start_hour = row_index + 9
                        end_hour = start_hour + 1
                        
                        start_ampm = 'am' if start_hour < 12 else 'pm'
                        start_hour = start_hour % 12 if start_hour % 12 != 0 else 12
                        start_time = f"{start_hour}{start_ampm}"
                        
                        end_ampm = 'am' if end_hour < 12 else 'pm'
                        end_hour = end_hour % 12 if end_hour % 12 != 0 else 12
                        end_time = f"{end_hour}{end_ampm}"
                        
                        time_slot = f"{start_time}-{end_time}"
                        
                        room_number = col_index + 1  # Add 1 to convert back to room number
                        room_id = 'r' + str(room_number + 100)  # Construct room ID
                        Database.update_room_status(room_id, selected_day, time_slot, 1, 'Vacant')
                        # update_room_status(room_id, selected_day, time_slot, 1, 'Vacant')

        
            return render_template('editAC_floor1.html', current_day=selected_day, get_room_availability=Database.get_room_availability, floor=1)
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
                Database.update_room_status(room_id, selected_day, time_slot, 2, status)        
            for row_index, row in enumerate(arr):
                for col_index, element in enumerate(row):
                    if element == 0:
                        start_hour = row_index + 9
                        end_hour = start_hour + 1
                        
                        start_ampm = 'am' if start_hour < 12 else 'pm'
                        start_hour = start_hour % 12 if start_hour % 12 != 0 else 12
                        start_time = f"{start_hour}{start_ampm}"
                        
                        end_ampm = 'am' if end_hour < 12 else 'pm'
                        end_hour = end_hour % 12 if end_hour % 12 != 0 else 12
                        end_time = f"{end_hour}{end_ampm}"
                        
                        time_slot = f"{start_time}-{end_time}"
                        
                        room_number = col_index + 1  # Add 1 to convert back to room number
                        room_id = 'r' + str(room_number + 200)  # Construct room ID
                        Database.update_room_status(room_id, selected_day, time_slot, 2, 'Vacant')
                        # update_room_status(room_id, selected_day, time_slot, 2, 'Vacant')
            return render_template('editAC_floor2.html', current_day=selected_day, get_room_availability=Database.get_room_availability, floor=2)

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
            Database.update_seat_status(seat_num, row_label, current_day, status)
        print(arr)
        for row_index, row in enumerate(arr):
            for col_index, element in enumerate(row):
                if element == 0:
                    status = 'Vacant'
                    row_label = chr(row_index + ord('a'))
                    seat_num = col_index + 1
                Database.update_seat_status(seat_num, row_label, current_day, status)
            
    
        return render_template('editauditorium.html',current_day=current_day, get_auditorium_seat_availability=Database.get_auditorium_seat_availability)
