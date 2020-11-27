import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import secrets
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST', 'DELETE'])

# CAN'T FIGURE OUT HOW TO SHOW JSON DATA SENT BACK
def userLoginLogout(): 
    # USER LOGIN
    if request.method == 'POST':
        conn = None
        cursor = None
        user_email = request.json.get("email")
        user_password = request.json.get("password")
        rows = None
        user = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email = ? AND password = ?", [user_email, user_password,]) 
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
        except Exception as e:
            print(e)
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
        except Exception as e:
            print(e)
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
        userId = request.json.get("userId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if userId != None and userId != "":
                cursor.execute("SELECT * FROM user WHERE id = ?", [userId],)
            else:
                cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
        except mariadb.ProgrammingError:
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError:
            print("Oops, there's a database error...")
        except mariadb.OperationalError:
            print("Connection error, please try again...")
        except Exception as e:
            print(e)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows):
                all_users_data = []
                for row in rows:
                    user_data = {
                        "userId": row[0],
                        "email": row[1],
                        "username": row[2],
                        "bio": row[3],
                        "birthdate": row[4]
                        }  
                    all_users_data.append(user_data)
                return Response(json.dumps(all_users_data, default = str), mimetype = "application/json", status = 200)
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
        user = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, bio, birthdate, password) VALUES(?, ?, ?, ?, ?)", [user_email, username, user_bio, user_birthdate, user_password,])
            rows = cursor.rowcount
            if rows == 1:
                loginToken = secrets.token_hex(16)
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?, ?)", [userId, loginToken])
                conn.commit()
                rows = cursor.amount
        except mariadb.ProgrammingError:
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError:
            print("Oops, there's a database error...")
        except mariadb.OperationalError:
            print("Connection error, please try again...")
        except Exception as e:
            print(e)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_info = {
                    "userId": userId,
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
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?", [loginToken,])
            user_success = cursor.fetchone()
            print(user_success)
            if user_success:
                if(user_email != "" and user_email != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [user_email, user_success[0],])
                if(username != "" and username != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [username, user_success[0],])
                if(user_bio != "" and user_bio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [user_bio, user_success[0],])
                if(user_birthdate != "" and user_birthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [user_birthdate, user_success[0],])
                if(user_password != "" and user_password != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [user_password, user_success[0],])
                conn.commit()
                rows = cursor.rowcount
                cursor.execute("SELECT * FROM user WHERE id =?", [user_success[0],])
                user = cursor.fetchall()
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        except Exception as e:
            print(e)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None):
                user_data = {
                    "userId": user_success[0],
                    "email": user[0][1],
                    "username": user[0][2],
                    "bio": user[0][3],
                    "birthdate": user[0][4],
                }
                return Response(json.dumps(user_data, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    # USER DELETE
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        user_password = request.json.get("password")
        loginToken = request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user = cursor.fetchall()
            print(user[0][1])
            print(loginToken)
            if user[0][1] == loginToken:
                cursor.execute("DELETE FROM user WHERE id = ? AND password = ?", [user[0][2], user_password,])
                conn.commit()
                rows = cursor.rowcount
                print(rows)
            else:
                return Response("There was an error with your password...", mimetype = "text/html", status = 500)
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        except Exception as e:
            print(e)
            print("There's a Database error")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Account has been deleted!", mimetype = "text/html", status = 204)
            else:
                return Response("There was an error deleting your account...", mimetype = "text/html", status = 500)

@app.route('/api/tweets', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def userTweets():
    # GET USER TWEETS AND GET TWEETS FROM ONE USER
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = request.json.get("userId")
        rows = None
        tweet_info = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if userId != None and userId != "":
                cursor.execute("SELECT t.id, t.userId, t.content, t.createdAt, u.username FROM tweet t INNER JOIN user u ON t.userId = u.id WHERE u.id = ?", [userId,])
            else:
                cursor.execute("SELECT t.id, t.userId, t.content, t.createdAt, u.username FROM tweet t INNER JOIN user u ON t.userId = u.id")
            rows = cursor.fetchall() 
            print(rows)
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        except Exception as e:
            print(e)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None):
                all_tweets = []
                for row in rows:
                    users_tweets = {
                        "tweetId": row[0],
                        "userId": row[1],
                        "username": row[4],
                        "content": row[2],
                        "createdAt": row[3]
                    }  
                    all_tweets.append(users_tweets)
                return Response(json.dumps(all_tweets, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again", mimetype = "text/html", status = 500)
    # CREATE TWEET
    elif request.method == 'POST':
            conn = None
            cursor = None
            loginToken = request.json.get("loginToken")
            tweet_content = request.json.get("content")
            rows = None
            tweetId = None
            createdAt = datetime.datetime.now().strftime("%Y-%m-%d")
            try:
                conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT us.userId, u.username FROM user_session us INNER JOIN user u ON us.userId = u.id WHERE us.loginToken = ?", [loginToken,])
                user = cursor.fetchall()
                print(user)
                num_of_letters = len(tweet_content)
                if num_of_letters <= 200 and len(user) == 1:
                    cursor.execute("INSERT INTO tweet(content, userId, createdAt) VALUES(?, ?, ?)", [tweet_content, user[0][0], createdAt,])
                    conn.commit()
                    print(len(user))
                    tweetId = cursor.lastrowid
                else:
                    print("NERDR cannot be over 200 letters!")
            except mariadb.ProgrammingError as e:
                print(e)
                print("There was a coding error by a NERDR here... ")
            except mariadb.DatabaseError as e:
                print(e)
                print("Oops, there's a database error...")
            except mariadb.OperationalError as e:
                print(e)
                print("Connection error, please try again...")
            except Exception as e:
                print(e)
            finally:
                if(cursor != None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if(tweetId != None):
                    tweet_info = {
                        "tweetId": tweetId,
                        "userId": user[0][0],
                        "username": user[0][1],
                        "content": tweet_content,
                        "createdAt": createdAt
                    }
                    return Response(json.dumps(tweet_info, default=str), mimetype="application/json", status=201)
                else:
                    return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)
    # UPDATE TWEET
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        tweetId = request.json.get("tweetId")
        loginToken = request.json.get("loginToken")
        tweet_content = request.json.get("content")
        updated_tweet_info = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user = cursor.fetchall()
            if user[0][1] == loginToken:
                cursor.execute("UPDATE tweet SET content = ? WHERE id = ?", [tweet_content, tweetId,])
                conn.commit()
            rows = cursor.rowcount
            cursor.execute("SELECT * FROM tweet WHERE id = ?", [tweetId,])
            updated_tweet = cursor.fetchall()
            print(updated_tweet)
        except mariadb.ProgrammingError as e:
            print(e)
            print("There was a coding error by a NERDR here... ")
        except mariadb.DatabaseError as e:
            print(e)
            print("Oops, there's a database error...")
        except mariadb.OperationalError as e:
            print(e)
            print("Connection error, please try again...")
        except Exception as e:
            print(e)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updated_tweet_info = {
                    "tweetId": updated_tweet[0][0],
                    "content": updated_tweet[0][1],
                }  
                return Response(json.dumps(updated_tweet_info, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again", mimetype = "text/html", status = 500)
    # DELETE TWEET
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        tweetId = request.json.get("tweetId")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user = cursor.fetchall()
            if user[0][1] == loginToken:
                cursor.execute("DELETE FROM tweet WHERE id = ?", [tweetId,])
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
        except Exception as e:
            print(e)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("NERDR deleted!", mimetype = "text/html", status = 204)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)