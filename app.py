import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import secrets

app = Flask(__name__)
CORS(app)

@app.route('/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])

# GET USERS OR ONE SPECIFIC USER
def nerdrUsers():
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")
            userId = cursor.fetchall()
        except mariadb.ProgrammingError:
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError:
            print("Oops, there's a database error...")
        except mariadb.OperationalError:
            print("Connection error, please try again...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(userId != None):
                return Response(json.dumps(userId, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again", mimetype = "text/html", status = 500)

    # SIGN UP NEW USER
    elif request.method == 'POST':
        conn = None
        cursor = None
        userEmail = request.json.get("email")
        username = request.json.get("username")
        userBio = request.json.get("bio")
        userBirthdate = request.json.get("birthdate")
        userPassword = request.json.get("password")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, bio, birthdate, password) VALUES(?, ?, ?, ?, ?)", [userEmail, username, userBio, userBirthdate, userPassword,])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError:
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError:
            print("Oops, there's a database error...")
        except mariadb.OperationalError:
            print("Connection error, please try again...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                loginToken = secrets.token_hex(16)
                return Response("User signed up!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    
    # UPDATE / PATCH USER INFORMATION
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        userEmail = request.json.get("email")
        username = request.json.get("username")
        userBio = request.json.get("bio")
        userBirthdate = request.json.get("birthdate")
        userPassword = request.json.get("password")
        userId = request.json.get("userId")
        # loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if(userEmail != "" and userEmail != None):
                cursor.execute("UPDATE user SET email = ? WHERE userId = ?", [userEmail, userId,])
            if(username != "" and username != None):
                cursor.execute("UPDATE user SET username = ? WHERE userId = ?", [username, userId,])
            if(userBio != "" and userBio != None):
                cursor.execute("UPDATE user SET bio = ? WHERE userId = ?", [userBio, userId,])
            if(userBirthdate != "" and userBirthdate != None):
                cursor.execute("UPDATE user SET birthdate = ? WHERE userId = ?", [userBirthdate, userId,])
            if(userPassword != "" and userPassword != None):
                cursor.execute("UPDATE user SET password = ? WHERE userId = ?", [userPassword, userId,])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError:
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError:
            print("Oops, there's a database error...")
        except mariadb.OperationalError:
            print("Connection error, please try again...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows <= 6):
                return Response("Information updated!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)