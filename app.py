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
def loginEndPoint(): 
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
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?, ?)", [user[0][0], loginToken])
                conn.commit()
            else:
                return Response("Invalid login information!", mimetype = "text/html", status = 400)
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
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            token = cursor.fetchall()
            print(token)
            if token[0][1] == loginToken:
                cursor.execute("DELETE FROM user_session WHERE loginToken = ?", [loginToken,])
                conn.commit()
            else:
                return Response("Error! Please try again...", mimetype = "text/html", status = 400)
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
                return Response("You are logged out!", mimetype = "text/html", status = 204)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)


@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def usersEndPoint():
    # issues finding one specific user
    # GET USERS OR ONE SPECIFIC USER
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        userId = request.args.get("userId")
        users = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT * FROM user WHERE id = ?", [userId],)
            else:
                cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()
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
            if(users != None):
                all_users_data = []
                for user in users:
                    user_data = {
                        "userId": user[0],
                        "email": user[1],
                        "username": user[2],
                        "bio": user[3],
                        "birthdate": user[4]
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
            if user[0][1] == loginToken:
                cursor.execute("DELETE FROM user WHERE id = ? AND password = ?", [user[0][2], user_password,])
                conn.commit()
                rows = cursor.rowcount
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
def tweetsEndpoint():
    # GET USER TWEETS AND GET TWEETS FROM ONE USER
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = request.args.get("userId")
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
                num_of_letters = len(tweet_content)
                if num_of_letters <= 200 and len(user) == 1:
                    cursor.execute("INSERT INTO tweet(content, userId, createdAt) VALUES(?, ?, ?)", [tweet_content, user[0][0], createdAt,])
                    conn.commit()
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

@app.route('/api/follows', methods=['GET', 'POST', 'DELETE'])
def followsEndPoint():
    # USER THE USERID FOLLOWS
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = request.args.get("userId")
        follows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT u.id, u.email, u.username, u.bio, u.birthdate FROM follow f INNER JOIN user u ON u.id = f.followId WHERE f.userId = ?", [userId,])
            follows = cursor.fetchall()
            print(follows)
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
            if(follows != None):
                user_data = []
                for follow in follows:
                    user_following_info = {
                        "userId": follow[0],
                        "email": follow[1],
                        "username": follow[2],
                        "bio": follow[3],
                        "birthdate": follow[4]
                    }  
                    user_data.append(user_following_info)
                return Response(json.dumps(user_data, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again", mimetype = "text/html", status = 500)
    # CREATES A FOLLOW RELATIONSHIP BETWEEN TWO USERS
    elif request.method == 'POST':
        conn = None
        cursor = None
        followId = request.json.get("followId")
        loginToken = request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_follow = cursor.fetchall()
            if user_making_follow[0][0] != followId:
                cursor.execute("INSERT INTO follow(followId, userId) VALUES(?, ?)", [followId, user_making_follow[0][0]])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("You cannot follow yourself!", mimetype="text/html", status=400)
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
            if rows == 1:
                return Response("Followed!", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status=500)
    # DELETE A FOLLOW RELATIONSHIP- unfollow
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        followId = request.json.get("followId")
        loginToken = request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_unfollow = cursor.fetchall()
            if user_making_unfollow[0][1] == loginToken and user_making_unfollow[0][2] != followId :
                cursor.execute("DELETE FROM follow WHERE userId = ? AND followId = ?", [user_making_unfollow[0][2], followId,])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("There was an error!", mimetype="text/html", status = 400)
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
            if (rows == 1):
                return Response("Unfollowed!", mimetype="text/html", status = 204)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status = 500)

@app.route('/api/followers', methods=['GET'])
def followersEndPoint():
    # GET USERS THAT FOLLOW USERID
    if request.method == 'GET':
        conn = None
        cursor = None
        userId = request.args.get("userId")
        follower_info = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT f.userId, u.email, u.username, u.bio, u.birthdate FROM follow f INNER JOIN user u ON u.id = f.userId WHERE f.followId = ?", [userId,])
            followers = cursor.fetchall()
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
            if (followers != None):
                follower_data = []
                for follower in followers: 
                    follower_info = {
                        "userId": follower[0],
                        "email": follower[1],
                        "username": follower[2],
                        "bio": follower[3],
                        "birthdate": follower[4]
                    }
                    follower_data.append(follower_info) 
                return Response(json.dumps(follower_data, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status = 500)

@app.route('/api/tweet-likes', methods=['GET', 'POST', 'DELETE'])
def tweetLikesEndPoint():
    # GET TWEET SPECIFIC LIKES OR ALL LIKES
    if request.method == 'GET':
        conn = None
        cursor = None
        tweetId = request.args.get("tweetId")
        likes = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT tweet_like.tweetId, tweet_like.userId, user.username FROM tweet_like INNER JOIN user ON user.id = tweet_like.userId WHERE tweet_like.tweetId = ?", [tweetId,])
            likes = cursor.fetchall()
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
            if (likes != None):
                user_data = []
                for like in likes: 
                    likes_info = {
                        "tweetId": like[0],
                        "userId": like[1],
                        "username": like[2]
                    }
                    user_data.append(likes_info) 
                return Response(json.dumps(user_data, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status=500)
    #  CREATE NEW LIKE FOR USER ON A SPECIFIC TWEET
    elif request.method == 'POST':
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_like = cursor.fetchall()
            if user_making_like[0][1] == loginToken:
                cursor.execute("INSERT INTO tweet_like(tweetId, userId) VALUES(?, ?)", [tweetId, user_making_like[0][2],])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("There was an error!", mimetype="text/html", status = 400)
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
            if (rows != None):
                return Response("Tweet Liked!", mimetype="text/html", status = 204)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)
    # USER MAKING UNLIKE
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_unlike = cursor.fetchall()
            if user_making_unlike[0][1] == loginToken:
                cursor.execute("DELETE FROM tweet_like WHERE tweetId = ? AND userId = ?", [tweetId, user_making_unlike[0][2],])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("There was an error!", mimetype="text/html", status = 400)
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
            if (rows != None):
                return Response("Tweet Unliked!", mimetype="text/html", status = 204)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)

@app.route('/api/comments', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def commentsEndPoint():
    # SEND BACK SPECIFIC COMMENTS BASED ON TWEETS
    if request.method == 'GET':
        conn = None
        cursor = None
        tweetId = request.args.get("tweetId")
        comment_info = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if tweetId != None and tweetId != "":
                cursor.execute("SELECT comment.*, user.username FROM comment INNER JOIN user ON comment.userId = user.id WHERE comment.tweetId = ?", [tweetId,])
                comment_info = cursor.fetchall()
            elif tweetId == None and tweetId == "":
                cursor.execute("SELECT * FROM comment")
                comment_info = cursor.fetchall()
            else:
                return Response("There was an error!", mimetype="text/html", status = 400)
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
            if (comment_info != None):
                user_data = []
                for comment in comment_info: 
                    comment_data = {
                        "commentId": comment[0],
                        "tweetId": comment[3],
                        "userId": comment[4],
                        "username": comment[5],
                        "content": comment[1],
                        "createdAt": comment[2]
                    }
                    user_data.append(comment_data) 
                return Response(json.dumps(user_data, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status=500)
    # create a new comment for a user on a specific tweet
    elif request.method == 'POST':
        conn = None
        cursor = None
        tweetId = request.json.get("tweetId")
        loginToken = request.json.get("loginToken")
        comment_content = request.json.get("content")
        createdAt = datetime.datetime.now().strftime("%Y-%m-%d")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_comment = cursor.fetchall()
            num_of_letters = len(comment_content)
            rows = cursor.rowcount
            if user_making_comment[0][1] == loginToken and num_of_letters <= 150:
                cursor.execute("INSERT INTO comment(content, createdAt, tweetId, userId) VALUES(?, ?, ?, ?)", [comment_content, createdAt, tweetId, user_making_comment[0][2]])
                conn.commit()
                rows = cursor.rowcount

                #  GETTING ALL USERS AND COMMENTS, NEED TO ONLY GET THE USER THAT MADE POST AND THE COMMENT
                cursor.execute("SELECT comment.id, user.username FROM comment INNER JOIN user ON user.id = comment.userId WHERE comment.tweetId = ?", [tweetId,])
                user_comment = cursor.fetchall()
                print(user_comment)
            else:
                return Response("Comment cannot be over 150 characters!", mimetype="text/html", status = 400)
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
            if (rows == 1):
                comment_info = {
                    "commentId": user_comment[0][0],
                    "tweetId": tweetId,
                    "userId": user_making_comment[0][2],
                    "username": user_comment[0][1],
                    "content": comment_content,
                    "createdAt": createdAt
                }
                return Response(json.dumps(comment_info, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status=500)
    # UPDATING COMMENT
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        comment_content = request.json.get("content")
        createdAt = datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_updating_comment = cursor.fetchall()
            cursor.execute("SELECT userId FROM comment WHERE id = ?", [commentId,])
            comment_owner = cursor.fetchall()
            if user_updating_comment[0][1] == loginToken and user_updating_comment[0][2] == comment_owner[0][0]:
                cursor.execute("UPDATE comment SET content = ? WHERE id = ?", [comment_content, commentId])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("You are not the owner of this comment!", mimetype="text/html", status = 400)
            if rows != None:
                cursor.execute("SELECT comment.*, user.username FROM user INNER JOIN comment ON user.id = comment.userId WHERE comment.id = ?", [commentId,])
                user_comment = cursor.fetchall()
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
            if (rows == 1):
                comment_info = {
                    "commentId": commentId,
                    "tweetId": user_comment[0][3],
                    "userId": user_comment[0][4],
                    "username": user_comment[0][5],
                    "content": comment_content,
                    "createdAt": createdAt
                }
                return Response(json.dumps(comment_info, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)
    # DELETE COMMENT - ONLY IF USER OWNS COMMENT
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_deleting_comment = cursor.fetchall()
            cursor.execute("SELECT userId FROM comment WHERE id =?", [commentId,])
            comment_owner = cursor.fetchall()
            if user_deleting_comment[0][1] == loginToken and user_deleting_comment[0][2] == comment_owner[0][0]:
                cursor.execute("DELETE FROM comment WHERE id = ?", [commentId,])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("You are not the owner of this comment!", mimetype="text/html", status = 400)
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
            if (rows != None):
                return Response("Comment deleted!", mimetype="text/html", status = 204)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)

@app.route('/api/comment-likes', methods=['GET', 'POST', 'DELETE'])
def commentLikesEndpoint():
    # GET ALL LIKES ON ALL COMMENTS OR ALL LIKES ON A SPECIFIC COMMENT
    if request.method == 'GET':
        conn = None
        cursor = None
        commentId = request.args.get("commentId")
        likes = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT comment_like.commentId, comment_like.userId, user.username FROM comment_like INNER JOIN user ON user.id = comment_like.userId WHERE comment_like.commentId = ?", [commentId,])
            likes = cursor.fetchall()
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
            if (likes != None):
                user_data = []
                for like in likes: 
                    likes_info = {
                        "commentId": like[0],
                        "userId": like[1],
                        "username": like[2]
                    }
                    user_data.append(likes_info) 
                return Response(json.dumps(user_data, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype="text/html", status=500)
    #  CREATE NEW LIKE FOR USER ON A SPECIFIC COMMENT
    elif request.method == 'POST':
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_like = cursor.fetchall()
            print(user_making_like)
            if user_making_like[0][1] == loginToken:
                cursor.execute("INSERT INTO comment_like(commentId, userId) VALUES(?, ?)", [commentId, user_making_like[0][2],])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("There was an error!", mimetype="text/html", status = 400)
            cursor.execute("SELECT comment_like.*, user.username FROM comment_like INNER JOIN user ON user.id = comment_like.userId WHERE comment_like.commentId = ?", [commentId,])
            likes = cursor.fetchall()
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
            if (rows != None):
                return Response("Comment Liked!", mimetype="text/html", status = 204)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)
    # UNLIKE COMMENT
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken,])
            user_making_unlike = cursor.fetchall()
            print(user_making_unlike)
            cursor.execute("SELECT userId FROM comment_like WHERE commentId = ?", [commentId,])
            like_owner = cursor.fetchall()
            print(like_owner)
            if user_making_unlike[0][1] == loginToken:
                cursor.execute("DELETE FROM comment_like WHERE commentId = ? AND userId = ?", [commentId, user_making_unlike[0][2]])
                conn.commit()
                rows = cursor.rowcount
            else:
                return Response("You cannot unlike a comment you haven't liked!", mimetype="text/html", status = 400)
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
            if (rows != None):
                return Response("Comment unliked!", mimetype="text/html", status = 204)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)

