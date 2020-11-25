import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import secrets

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST', 'DELETE'])

def userLoginLogout():
    # USER LOGIN
    if request.method == 'POST':
        conn = None
        cursor = None
        userEmail = request.json.get("email")
        userPassword = request.json.get("password")
        rows = None
        user = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email = ? AND password = ?", [userEmail, userPassword,]) 
            user = cursor.fetchall()
            rows = cursor.rowcount
            if(rows == 1):
                loginToken = secrets.token_hex(16)
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?, ?)", [user[0][0], loginToken])
                conn.commit()
        except mariadb.ProgrammingError as e:
            print(e)
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
                return Response("Logged in!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    # USER LOGOUT 
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        userId = request.json.get("id")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE loginToken = ?", [loginToken,])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("You are logged out!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)


@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])

def nerdrUsers():
    # GET USERS OR ONE SPECIFIC USER
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if userId == "" and userId == None:
                cursor.execute("SELECT * FROM user")
            else:
                cursor.execute("SELECT * FROM user WHERE id = ?", [userId,])
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
            rows = cursor.rowcount
            if rows == 1:
                loginToken = secrets.token_hex(16)
                userId = cursor.lastrowid
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?, ?)", [userId, loginToken])
                conn.commit()
                rows = cursor.amount
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
                return Response("User signed up!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    # UPDATE / PATCH USER INFORMATION
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        userTokenSuccess = None
        userEmail = request.json.get("email")
        username = request.json.get("username")
        userBio = request.json.get("bio")
        userBirthdate = request.json.get("birthdate")
        userPassword = request.json.get("password")
        userId = request.json.get("id")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE id = ? AND loginToken = ?", [userId, loginToken,])
            userTokenSuccess = cursor.fetchall()
            rows = cursor.rowcount
            if userTokenSuccess and rows == 1:
                if(userEmail != "" and userEmail != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [userEmail, userId,])
                if(username != "" and username != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [username, userId,])
                if(userBio != "" and userBio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [userBio, userId,])
                if(userBirthdate != "" and userBirthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [userBirthdate, userId,])
                if(userPassword != "" and userPassword != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [userPassword, userId,])
            conn.commit()
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Information updated!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    # USER DELETE
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        userTokenSuccess = None
        userPassword = request.json.get("password")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            userTokenSuccess = cursor.fetchall()
            cursor.execute("SELECT * FROM user WHERE id = ?", [userTokenSuccess[0][2],])
            cursor.fetchall()
            # conn.commit()
            print(userTokenSuccess)
            rows = cursor.rowcount
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response( mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)

@app.route('/api/tweets', methods=['GET', 'POST', 'DELETE', 'PATCH'])

def userTweets():
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tweet")
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