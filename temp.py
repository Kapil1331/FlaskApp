from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required


@app.route("/user_login",methods=["GET", "POST"])
def user_login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("user_name") or not request.form.get("user_password"):
            return render_template("user_login.html", string='You must enter both username and password')
        
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("user_name")
        )

        if len(rows) != 1:
            return render_template("user_login.html", string='You must register first')
        if not check_password_hash(
            rows[0]["hash"], request.form.get("user_password")
        ):
            return render_template("user_login.html", string='Your password is incorrect')
        if not rows[0]["email"] == request.form.get("user_email"):
            return render_template("user_login.html", string='Your email is incorrect')
        
        session["user_id"] = rows[0]["user_id"]

        return redirect("user_home")
    elif request.method == "GET":
        return render_template("user_login.html")

@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        name = request.form.get("user_name")
        password = request.form.get("user_password")
        confirmation = request.form.get("user_confirmation")
        email = request.form.get("user_email")
        if not name:
            return render_template("register.html", string="You need to enter a username")
        taken_name = db.execute("SELECT * FROM users")
        for k in taken_name:
                if k["username"] == name:
                    return render_template("register.html", string="The entered username is already in use")
        if not password or not confirmation:
                return render_template("register.html", string="Both password and confirmation are necessary fields")
        if password != confirmation:
            return render_template("register.html", string="Both password and reentered password must be same")
        db.execute(
                "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
                name, 
                email,
                generate_password_hash(password),
        )
        id = db.execute("SELECT * FROM users WHERE username = ?", name)
        session["user_id"] = id[0]["user_id"]
        return redirect("user_home")
    elif request.method == "GET":
        return render_template("user_register.html")
