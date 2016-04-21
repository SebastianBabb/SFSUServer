#!/usr/bin/python

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask import current_app
from flask import render_template
from flask import Response
from flask import send_from_directory
from flask import send_file
import json 

from DBConn import DBConn

app = Flask(__name__, static_url_path='')   

"""
Will get indivial file via ajax call for when user
clicks on file in file structure tree.
"""

@app.route("/api/example", methods=['GET','OPTIONS'])
def  test():
    return '{"message": "hello"}'

@app.route("/api/departments", methods=['GET', 'OPTIONS'])
def departments():
    # Get db.
    db = DBConn()
    # Query db for subjects.
    rows = db.query("SELECT * FROM \"Department\"")
    # If records returned, split and jsonify.
    if(rows):
        # Split columns into tuples. 
        id, dept, email, phone = zip(*rows)
	# Return test data for allen...
    	#return '"departments":[{"department":"Anthropology"}, {"department":"Biology"}, {"department":"Chemistry"}]'
    	return jsonify(departments=list(dept))
    #else:
        return "Oops"

@app.route("/api/classes", methods=['GET', 'OPTIONS'])
def classes():
    # Get department.
    dept = request.args.get('department')
    # Get db.
    db = DBConn()
    # Query db for subjects.
    # Note:  currently (4/21/16) no relation between Courses and Department tables.
    #rows = db.query("SELECT * FROM \"Classes\" ")

    return dept

if __name__ == "__main__":
    import logging
    logging.basicConfig(filename='/var/log/sfsudroid.log',level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5656, debug=True )
