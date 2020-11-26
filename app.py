import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import secrets

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST', 'DELETE'])

# CAN'T FIGURE OUT HOW TO SHOW JSON DATA SENT BACK
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
    # CAN'T FIGURE OUT HOW TO LOOP THROUGH ALL USERS, ONLY GETTING ONE USER BACK
    # GET USERS OR ONE SPECIFIC USER
    if request.method == 'GET':
        conn = None
        cursor = None
        user_id = request.json.get("id")
        users = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if user_id != None and user_id != "":
                cursor.execute("SELECT * FROM user WHERE id = ?", [user_id],)
            else:
                cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()
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
            if(users != None):
                user_data = {
                    "userId": users[0][0],
                    "email": users[0][1],
                    "username": users[0][2],
                    "bio": users[0][3],
                    "birthdate": users[0][4]
                }
                return Response(json.dumps(user_data, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again", mimetype = "text/html", status = 500)
    # SIGN UP NEW USER
    elif request.method == 'POST':
        conn = None
        cursor = None
        user_email = request.json.get("email")
        username = request.json.get("username")
        user_bio = request.json.get("bio")
        user_birthdate = request.json.get("birthdate")
        user_password = request.json.get("password")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, bio, birthdate, password) VALUES(?, ?, ?, ?, ?)", [user-email, username, user_bio, user_birthdate, user_password,])
            rows = cursor.rowcount
            if rows == 1:
                loginToken = secrets.token_hex(16)
                user_id = cursor.lastrowid
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?, ?)", [user_id, loginToken])
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
                user_info = {
                    "userId": user_id,
                    "email": user_email,
                    "username": username,
                    "bio": user_bio,
                    "birthdate": user_birthdate,
                    "loginToken": loginToken
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    # UPDATE / PATCH USER INFORMATION
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        user_email = request.json.get("email")
        username = request.json.get("username")
        user_bio = request.json.get("bio")
        user_birthdate = request.json.get("birthdate")
        user_password = request.json.get("password")
        loginToken = request.json.get("loginToken")
        user_id = request.json.get("id")
        user_token_success = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_token_success = cursor.fetchall()
            rows = cursor.rowcount
            if user_token_success:
                if(user_email != "" and user_email != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [user_email, user_token_success[2],])
                if(username != "" and username != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [username, user_token_success[2]])
                if(user_bio != "" and user_bio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [user_bio, user_token_success[2],])
                if(user_birthdate != "" and user_birthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [user_birthdate, user_token_success[2],])
                if(user_password != "" and user_password != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [user_password, user_token_success[2],])
            conn.commit()
            print(user_token_success)
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
                user_info = {
                    "userId": user_id,
                    "email": user_email,
                    "username": username,
                    "bio": user_bio,
                    "birthdate": user_birthdate,
                }
                return Response(json.dumps(user_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    
    # WILL NOT DELETE AT ALL
    # USER DELETE
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        user_password = request.json.get("password")
        login_token = request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?", [login_token,])
            user_id = cursor.fetchall()[0][0]
            cursor.execute("DELETE FROM user_session WHERE user_id = ?", [user_id,])
            cursor.execute("DELETE FROM user WHERE password = ? AND id = ?", [user_password, user_id,])
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
                return Response("Account has been deleted!", mimetype = "text/html", status = 204)
            else:
                return Response("There was an error attempting to delete your account...", mimetype = "text/html", status = 500)

@app.route('/api/tweets', methods=['GET', 'POST', 'DELETE', 'PATCH'])

# CANNOT GET ALL USERS?
def userTweets():
    if request.method == 'GET':
        conn = None
        cursor = None
        user_id = request.json.get("user_id")
        user_tweets = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if user_id == "" and user_tweets == None:
                cursor.execute("SELECT * FROM tweet")
                rows = cursor.fetchall()
                user_tweets = []
                column_name = [i[0] for i in cursor.description]
                for row in rows:
                    user_tweets.append(dict(zip(column_name, row)))
            else:
                cursor.execute("SELECT user_id, id, content, createdAt FROM tweet WHERE user_id = ?", [user_id,])
                rows = cursor.fetchall()
                user_tweets = []
                column_name = [i[0] for i in cursor.description]
                for row in rows:
                    user_tweets.append(dict(zip(column_name, row)))       
            # if user_id != "" and user_id != None:
            # elif userId == "" and userId == None:
            # else:
            #     cursor.execute("SELECT * FROM tweet")
            #     tweets = cursor.fetchall()
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
            if(user_tweets != None):
                return Response(json.dumps(user_tweets, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again", mimetype = "text/html", status = 500)