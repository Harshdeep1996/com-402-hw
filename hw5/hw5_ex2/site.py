#!/usr/bin/env python3
import os
import sys
import populate
from flask import g
from flask import Flask, current_app
from flask import render_template, request, jsonify
import pymysql


app = Flask(__name__)
username = "root"
password = "root"
database = "hw5_ex2"

# This method returns a list of messages in a json format such as
# [
# { "name": <name>, "message": <message> },
# { "name": <name>, "message": <message> },
# ...
# ]
# If this is a POST request and there is a parameter "name" given, then only
# messages of the given name should be returned.
# If the POST parameter is invalid, then the response code must be 500.
@app.route("/messages", methods=["GET", "POST"])
def messages():
    with db.cursor() as cursor:
        sql = "SELECT name, message FROM messages"

        if request.method == "GET":
            cursor.execute(sql)
            rows = cursor.fetchall()
            return jsonify(rows), 200
        
        print(request)
        data = request.get_json()
        print(data)
        try:
            name = data['name']
        except KeyError:
            return "Invalid input", 500

        sql += " WHERE name=%s"
        print(sql)
        cursor.execute(sql, name)
        rows = cursor.fetchall()

        return jsonify(rows), 200


# This method returns the list of users in a json format such as
# { "users": [ <user1>, <user2>, ... ] }
# This methods should limit the number of users if a GET URL parameter is given
# named limit. For example, /users?limit=4 should only return the first four
# users.
# If the paramer given is invalid, then the response code must be 500.
@app.route("/users", methods=["GET"])
def contact():
    with db.cursor() as cursor:
        
        sql = "SELECT name FROM users"
        
        cursor.execute(sql)
        results = cursor.fetchall()
        print(len(results))
        users = [result["name"] for result in results]
        
        if not request.args.get('limit'):
            return jsonify({"users": users}), 200

        limit = request.args.get('limit')
        
        try:
            limit = int(limit)
            limited_users = users[:limit]
            if limit < 0:
                raise IndexError
        
        except (ValueError, IndexError):
            return "Invalid input", 500

        return jsonify({"users": limited_users}), 200

if __name__ == "__main__":
    seed = "randomseed"
    if len(sys.argv) == 2:
        seed = sys.argv[1]

    db = pymysql.connect("localhost",
                         username,
                         password,
                         database,
                         cursorclass=pymysql.cursors.DictCursor)
    with db.cursor() as cursor:
        populate.populate_db(seed, cursor)
        db.commit()
    print("[+] database populated")

    app.run(host='0.0.0.0', port=80)
