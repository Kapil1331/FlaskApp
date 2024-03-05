
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
@app.route("/enternew")
def enternew():
    return render_template("student.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=['POST', 'GET'])
def authenticate():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect('database.db')

        # Check if the username and password match a record in the database
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE name=? AND password=?', (username, password))
        user = cursor.fetchone()
        if(username == 'cap' and password == admin_password):
            return render_template('adminlogin.html')            
        else:
            if user:
                # Successful authentication, redirect to selectvenue.html
                conn.close()
                return render_template('selectvenue.html')
            else:
                # Authentication failed, render login.html with an error message
                conn.close()
                return render_template("login.html", error="Invalid username or password")

    else:
            return render_template("login.html")


# Route to add a new record (INSERT) student data to the database
@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            zip = request.form['zip']
            password = request.form['password']

            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students (name, addr, city, zip, password) VALUES (?,?,?,?,?)",(nm, addr, city, zip, password))

                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

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
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)


@app.route("/redirectvenue", methods=['POST','GET'])
def redirectvenue():
    selected_venue = request.args.get('venue')
    if selected_venue == 'Auditorium':
        return render_template('auditorium.html')
    elif selected_venue == 'parking_slot':
        return render_template('parking_slot.html')
    elif selected_venue == 'AC_building':
        return render_template('AC_building.html')
    else: 
        return render_template('selectvenue.html')  

def get_room_availability(room_id, current_day, time_slot, floor):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Choose the appropriate table based on the floor
    table_name = f'acFloor{floor}'
    
    # Use a prepared statement to prevent SQL injection
    query = f"SELECT {room_id} FROM {table_name} WHERE day = ? AND time_slot = ? AND {room_id} IS NOT NULL"
    cursor.execute(query, (current_day, time_slot))
    
    result = cursor.fetchone()  # Fetch a single row since we're looking for a specific time_slot
    
    if result:
        availability = result[0]
        return availability
    else:
        return None  # Return None if no availability is found



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

@app.route("/editvenue", methods=['POST','GET'])
def editvenue():
    selected_venue = request.args.get('venue')
    current_day = datetime.now().strftime('%A')
    if selected_venue == 'Auditorium':
        return render_template('editauditorium.html')
    elif selected_venue == 'parking_slot':
        return render_template('editparking_slot.html')
    elif selected_venue == 'AC_floor1':
        return render_template('editAC_floor1.html', current_day=current_day, get_room_availability=get_room_availability, floor=1)
    elif selected_venue == 'AC_floor2':
        return render_template('editAC_floor2.html', current_day=current_day, get_room_availability=get_room_availability, floor=2)
    else: 
        return render_template('selectvenue.html')
