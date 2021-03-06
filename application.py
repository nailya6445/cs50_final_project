import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show reading list"""

    if request.method == "GET":
        quote1 = db.execute("SELECT quote FROM quotes ORDER BY random() LIMIT 1")
        # Execute list joining "book" and "idlist" tables
        list = db.execute("SELECT Title1, Status, LastUpdate, Author, Year, Country, Language FROM idlist INNER JOIN book on idlist.Title1=book.Title WHERE id=:id",
                          id=session["user_id"])
        # If the user has no list yet
        if not list:
            el = {'Title1': "No", 'Author': "No", 'Year': "No", 'Country': "No", 'Language': "No", 'Status': "No", 'LastUpdate': "No"}
        return render_template("index.html", list=list, yourquote=quote1[0]["quote"])
    return render_template("index.html")

@app.route("/adjust", methods=["GET", "POST"])
@login_required
def search():
    """Search for books that match query"""
    if request.method == "GET":

        if not request.args.get("q"):
            return render_template("adjust.html")
        else:
            q = request.form.get("q") + "%"

            books = db.execute("SELECT Title, Author FROM book WHERE Title LIKE: q OR Author LIKE: q",
                                q=q)
     return jsonify(books)
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)
        # Ensure password was submitted
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        # Check for Uniqueness of username
        check_uniq = db.execute("SELECT username FROM users WHERE username=:username",
                                username=request.form.get("username"))
        if check_uniq:
            return apology("Username already exists", 400)
        # Generate hash of the password
        hash = generate_password_hash(request.form.get("password"))

        # Insert into database username and a hash of user's password
        insert_user_hash = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                                      username=request.form.get("username"), hash=hash)
        # Remember which user has registered
        cur = db.execute("SELECT * FROM users WHERE username = :username",
                         username=request.form.get("username"))
        session["user_id"] = cur[0]["id"]
        quote1 = db.execute("SELECT quote FROM quotes ORDER BY random() LIMIT 1")
        # Redirect user to Index page
        return render_template("index.html", yourquote=quote1[0]["quote"])
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    return apology("Register first", 403)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
