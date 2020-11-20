import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])

# GET Users or one specific user
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
    # elif request.method == 'POST':
    #     conn = None
    #     cursor = None
    #     blog_content = request.json.get("content")
    #     blog_created_at = request.json.get("created_at")
    #     blog_title = request.json.get("blog_title")
    #     rows = None