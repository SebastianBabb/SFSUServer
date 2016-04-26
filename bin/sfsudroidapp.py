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
    # Query db for departments - currently using the course_name col from the Courses table.
    cols, rows = db.query("SELECT DISTINCT course_name FROM \"Courses\" ORDER By course_name ASC")
    # If records returned, split and jsonify.
    if(rows):
        # Split columns into tuples. 
        #id, dept, email, phone = zip(*rows)
	dept = zip(*rows)
    	return jsonify(departments=list(dept))
    else:
        return "Oops"

@app.route("/api/classes", methods=['GET', 'OPTIONS'])
def classes():
    # Get department.
    dept = request.args.get('department')
    # Get db.
    db = DBConn()
    # Query db for class record.
    # Note:  currently (4/21/16) no relation between Courses and Department tables.
    cols, rows = db.query("SELECT DISTINCT course_name, course_number, course_description  FROM \"Courses\" WHERE course_name = '%s' ORDER BY course_number ASC" %dept);

    if(rows):
        dict_list = []

	# Build a list of dictionaries.
	for row in rows:
	    dict_list.append(dict(zip(cols, row)))

    	return jsonify(classes=dict_list)
    else:
        return "No such dept %s" %dept

if __name__ == "__main__":
    import logging
    logging.basicConfig(filename='/var/log/sfsudroid.log',level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5656, debug=True )
