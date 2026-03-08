from flask import Flask, render_template, request, redirect, session, send_from_directory
import mysql.connector
import os
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

# Database connection

import mysql.connector
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT

db = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# Upload folder (absolute path)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Home Page
@app.route("/")
def home():
    return render_template("login.html")


# Register
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor()

        sql = "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)"
        cursor.execute(sql,(username,email,password))

        db.commit()

        return redirect("/")

    return render_template("register.html")


# Login
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    cursor = db.cursor(dictionary=True)

    sql = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(sql,(email,password))

    user = cursor.fetchone()

    if user:
        session["user_id"] = user["id"]
        return redirect("/dashboard")

    return "Login Failed"


# Dashboard
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        note = request.form["note"]
        image = request.files["image"]

        filename = ""

        if image and image.filename != "":
            # unique filename
            filename = str(uuid.uuid4()) + "_" + image.filename

            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(path)

        sql = "INSERT INTO notes(user_id,note,image) VALUES(%s,%s,%s)"
        cursor.execute(sql,(user_id,note,filename))

        db.commit()

    sql = "SELECT * FROM notes WHERE user_id=%s"
    cursor.execute(sql,(user_id,))

    notes = cursor.fetchall()

    return render_template("dashboard.html", notes=notes)


# Upload image show
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


app.run(debug=True)