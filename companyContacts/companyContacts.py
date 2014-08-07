#all the imports
import sqlite3
import json
from random import randint
from collections import Counter
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from contextlib import closing
import smtplib
from xlrd import open_workbook

################### Variables ######################

DATABASE = 'cc.db'
DEBUG = True
SECRET_KEY = 'development key'

USERNAME = 'admin'
PASSWORD = 'default'

workbook = open_workbook('/Users/adornadula/Perforce/ApoorvaPerforceWorkspace/ficds/OverallScan_detailed_report.xls')

editResults = [];

#creating the actual application
app = Flask(__name__)
app.config.from_object(__name__)

################ Initialization & General ################

#initializes the database
def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

#More elegant way of opening and closing requests
@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

# connect to specified database
#can open a connection on request and also from he the interactive Python shell or a script
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])


################ Views ################
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/view')
def view():
	current = g.db.execute('select Name, ContactName, ContactEmail, ContactPhoneNumber, Description from Company')
	companies = [dict(Name=row[0], ContactName=row[1], ContactEmail=row[2], ContactPhoneNumber=row[3], Description=row[4]) for row in current.fetchall()]
	return render_template('view.html', companies = companies)

@app.route('/add')
def add():
	return render_template('add.html')

@app.route('/edit')
def edit():
	return render_template('edit.html', editResults = editResults)

@app.route('/email')
def email():
	return render_template('email.html')

@app.route('/update')
def update():
	init_db()
	wb = open_workbook('/Users/adornadula/Documents/other/SWE/masterSpreadsheet.xlsx')
	for s in wb.sheets():
		for row in range(s.nrows):
			values = []
			for col in range(s.ncols):
				values.append(s.cell(row, col).value);

			companyName = values[0]
			contactName = values[1]
			contactEmail = values[2]
			contactPhone = values[3]
			notes = values[4]

			print(companyName)

			g.db.execute('insert into Company (Name, ContactName, ContactEmail, ContactPhoneNumber, Description) values (?, ?, ?, ?, ?)', [companyName, contactName, contactEmail, contactPhone, notes])
			g.db.commit()
	return redirect(url_for('view'))

#Shows the edit form for the company
@app.route('/editComp/<cID>')
def editComp(cID):
	global editResults
	current = g.db.execute('SELECT Name, ContactName, ContactEmail, ContactPhoneNumber, Description, CompanyID FROM Company WHERE CompanyID=?', [cID])
	editResult = [dict(Name=row[0], ContactName=row[1], ContactEmail=row[2], ContactPhoneNumber=row[3], Description=row[4], CompanyID=row[5]) for row in current.fetchall()]
	editResults = []
	return render_template("editCompany.html", editResults = editResult[0])


################ Action ################
@app.route('/addAction', methods=['POST'])
def addAction():
	companyName = request.form["compName"]
	contactName = request.form["contName"]
	contactEmail = request.form["contEmail"]
	contactPhone = request.form["contPhone"]
	notes = request.form["description"]

	g.db.execute('insert into Company (Name, ContactName, ContactEmail, ContactPhoneNumber, Description) values (?, ?, ?, ?, ?)', [companyName, contactName, contactEmail, contactPhone, notes])
	g.db.commit()

	currentID = g.db.execute('SELECT max(CompanyID) FROM Company')
	print(currentID.fetchall()[0][0])

	return redirect(url_for('add'))

#Displays the companies that fit the query
@app.route('/editAction', methods= ['POST'])
def editAction():
	global editResults
	companyName = request.form['compName']
	current = g.db.execute('SELECT Name, ContactName, ContactEmail, ContactPhoneNumber, Description, CompanyID FROM Company WHERE Name=?', [companyName])
	editResults = [dict(Name=row[0], ContactName=row[1], ContactEmail=row[2], ContactPhoneNumber=row[3], Description=row[4], CompanyID=row[5]) for row in current.fetchall()]
	return redirect(url_for('edit'))

#Updates the company in the database
@app.route('/saveEdit/<cID>', methods=['POST'])
def saveEdit(cID):
	companyName = request.form["compName"]
	contactName = request.form["contName"]
	contactEmail = request.form["contEmail"]
	contactPhone = request.form["contPhone"]
	notes = request.form["description"]

	g.db.execute('UPDATE Company SET Name=?, ContactName=?, ContactEmail=?, ContactPhoneNumber=?, Description=? WHERE CompanyID=?', [companyName, contactName, contactEmail, contactPhone, notes, cID])
	g.db.commit()
	return redirect(url_for('edit'))


################ Other ################

#fires up server if we want to run this as a stand alone application
if __name__ == '__main__':
	#app.run(host = '0.0.0.0')
	app.run()








