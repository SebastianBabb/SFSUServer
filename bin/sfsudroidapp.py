#!/usr/bin/python

__author__ = "Sebastian Babb"
__version__ = "1.0.0"
__maintainer__ = "Sebastian Babb"
__email__ = "sbabb@mail.sfsu.edu"
__status__ = "Production"

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
    # Query db for departments - currently using the course_subject col from the Courses table.
    cols, rows = db.query("SELECT DISTINCT course_subject FROM \"Courses\" ORDER By course_subject ASC")
    # If records returned, split and jsonify.
    if(rows):
        # Split columns into tuples. 
        #id, dept, email, phone = zip(*rows)
	dept = zip(*rows)
	# Return first element in array.
    	return jsonify(departments=list(dept[0]))
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
    cols, rows = db.query('''SELECT DISTINCT "Professors".id AS "teacher_id", "Professors".first_name AS "teacher_first_name", "Professors".last_name AS "teacher_last_name", "Courses".course_subject, "Courses".course_number, "Courses".course_name, "Courses".section_number, "Courses".course_meeting_day, "Courses".course_time, "Courses".course_description, "Courses".section_number FROM "Courses" INNER JOIN "Professors" ON "Professors".id = "Courses".teacher_id WHERE "Courses".course_subject = '%s' ORDER BY "Professors".id ASC''' %dept)

    if(rows):
        dict_list = []

	# Build a list of dictionaries.
	for row in rows:
	    dict_list.append(dict(zip(cols, row)))

    	return jsonify(classes=dict_list)
    else:
        return "No such dept %s" %dept

@app.route("/api/professors", methods=['GET', 'OPTIONS'])
def professors():
    dept = request.args.get('department')

    db = DBConn()
	
    cols, rows = db.query("SELECT DISTINCT first_name, last_name FROM \"Professors\" WHERE department_name= '%s'" %dept)

    if(rows):
	full_names = []
	# Build name
	for row in rows:
		full_names.append(row[0] + " " + row[1])

    	return jsonify(professors=full_names)
    else:
        return "No such dept %s" %dept

if __name__ == "__main__":
    import logging
    logging.basicConfig(filename='/var/log/sfsudroid.log',level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5656, debug=True )


