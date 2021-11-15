# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import psycopg2
conn = psycopg2.connect("host=localhost dbname=projectdb user=projectuser password=projectpassword")
cur = conn.cursor()

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://projectuser:projectpassword@localhost:5432/projectdb' #hostname for the db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import TA, Course, Assignment, Student, Reminder

# Step 05: add routes and their binded functions here
@app.route('/createcourse/', methods=['POST'])
def create_course():
	course_code = request.json['course_code']
	section_no = request.json['section_no']
	email = request.json['email']

	find_course = Course.query.filter_by(course_code=course_code)
	if find_course is None:
		new_course = Course(course_code=course_code, section_no=section_no, email=email)
		db.session.add(new_course)
		db.session.commit()
		return jsonify('{} for {} is created'.format(course_code, section_no))
	elif find_course is not None:
		find_section = Course.query.filter_by(course_code=course_code, section_no=section_no).first()
		if find_section is None:
			new_course = Course(course_code=course_code, section_no=section_no, email=email)
			db.session.add(new_course)
			db.session.commit()
			return jsonify('{} for {} is created'.format(course_code, section_no))
		else:
			print(find_section)
			return jsonify('{} for {} already exist!'.format(course_code, section_no))
	return 

@app.route('/createassignment/', methods=['POST'])
def create_assignment():
	code = request.args.get('course_code')
	section = request.args.get('section_no')
	name = request.args.get('assignment_name')
	weightage = request.args.get('weightage')
	deadline = request.args.get('deadline')

	courseid = db.session.query(Course.id).filter(Course.course_code==code, Course.section_no==section)
	check_name = Assignment.query.filter_by(assignment_name=name, course_fk=courseid).first()
	if check_name is None:
		new_assignment = Assignment(assignment_name=name, assignment_weightage=weightage, assignment_deadline=deadline, course_fk=courseid)
		db.session.add(new_assignment)
		db.session.commit()
		return ('New assignment created')
	else:
		return ('Assignment for {}, {} already exists'.format(code,section))
	return


@app.route('/getassignment/', methods=['GET']) 
def get_asg():
	print('get_asg')
	if 'course_code' in request.args:
		code = str(request.args.get('course_code'))

		if 'section_no' in request.args:
			section = str(request.args.get('section_no'))
			courseid = db.session.query(Course.id).filter(Course.course_code==code, Course.section_no==section)
			asg = Assignment.query.filter_by(course_fk=courseid)
			return jsonify ([a.serialize() for a in asg])
		else:
			return ('Error: you have not entered a valid section number')
	return	

@app.route('/updateassignment/', methods=['PUT'])
def update_assignment():
	code = request.args.get('course_code')
	section = request.args.get('section_no')
	assignment_name = request.args.get('assignment_name') # in any situation this is compulsory to input
	courseid = db.session.query(Course.id).filter(Course.course_code==code, Course.section_no==section)
	asg = Assignment.query.filter_by(course_fk=courseid, assignment_name=assignment_name).first()

	if 'new_assignment_name' in request.args:
		new_assignment_name = request.args.get('new_assignment_name')
		asg.assignment_name = new_assignment_name
		db.session.commit()
		return jsonify(asg.serialize())

	elif 'new_assignment_weightage' in request.args:
		new_assignment_weight = request.args.get('new_assignment_weightage')
		asg.assignment_weightage = new_assignment_weight
		db.session.commit()
		return jsonify(asg.serialize())

	elif 'new_assignment_deadline' in request.args:
		new_assignment_deadline = request.args.get('new_assignment_deadline')
		asg.assignment_deadline = new_assignment_deadline
		db.session.commit()
		return jsonify(asg.serialize())

	return
	
@app.route('/deleteassignment/', methods=['DELETE'])
def delete_assignment():
	code = request.json['course_code']
	section = request.json['section_no']
	assignment_name = request.json['assignment_name']

	courseid = db.session.query(Course.id).filter(Course.course_code==code, Course.section_no==section)

	deleting = Assignment.query.filter_by(course_fk=courseid, assignment_name=assignment_name).first()
	db.session.delete(deleting)
	db.session.commit()
	return ('Deletion is Successful!')


@app.route('/createstud/', methods=['POST'])
def createStud():
	name = request.json['name']
	if 'chatid' in request.args:
		chatid = int(request.args.get('chatid'))
		try:
			check_stud = Student.query.filter_by(student_chatid=chatid).first()
			if check_stud is None: # check whether student already exists in db
				new_stud = Student(student_chatid=chatid, student_name=name)
				db.session.add(new_stud)
				db.session.commit()
				return jsonify(new_stud.serialize())
			else:
				return('Error: student {} already exists'.format(name))

		except Exception as e:
			return (str(e))
	else:
		return ('No input for student chat id')
	

@app.route('/createreminder/', methods=['POST'])
def createReminder():
	code = request.json['course_code']
	section = request.json['section_no']

	if 'number_of_days' in request.json:
		num_days = int(request.json['number_of_days'])
		date_stamp = datetime.now().date() + timedelta(days=num_days)
	else:
		return ('Input missing num days')
	
	if 'chatid' in request.args:
		chatid = int(request.args.get('chatid'))
		
		courseid = db.session.query(Course.id).filter(Course.course_code==code, Course.section_no==section)
		stud_id = Student.query.filter_by(student_chatid=chatid).first().id
		if stud_id is None:
			return ('Student does not exist in database')
		else:
			new_reminder = Reminder(studid=stud_id, reminder_date=date_stamp, course_id=courseid)
			db.session.add(new_reminder)
			db.session.commit()
			return jsonify (new_reminder.serialize())

	else: # if chat id not in request.args
		return ("Error: no chat id in input")

@app.route('/getreminder/', methods=['GET'])
def getreminder():
	dict_course = {}
	emptyisme = []
	chat_id = {}

	results = {}
	results2 = {}
	student_id = {}
	today = request.json['today']
	reminders = Reminder.query.filter_by(reminder_date=today)
	for reminder in reminders:
		find_studid = Reminder.query.filter_by(id=reminder.id).first().studid
		find_chat = Student.query.filter_by(id=find_studid).first().student_chatid
		# print(reminder, type(reminder),'this is reminder')
		# print(find_studid, type(find_studid), "this is studid")
		find_courseid = Reminder.query.filter_by(studid=find_studid, reminder_date=today).all()
		# print(find_courseid, type(find_courseid), 'this is course')
		for course in find_courseid:
			if dict_course == {}:
				dict_course.update({find_studid:[course.course_id]})
			elif find_studid in dict_course:
				if course.course_id not in dict_course[find_studid]:
					dict_course[find_studid].append(course.course_id)
			else:
				dict_course.update({find_studid:[course.course_id]})
	print(dict_course)
	for k,v in dict_course.items():
		for i in v:
			find_assign = Assignment.query.filter_by(course_fk=i).all()
			print(find_assign) # assignment for the course
			for each in find_assign:
				find_assid  = Assignment.query.filter_by(assignment_name=each.assignment_name, course_fk=i).first().id
			# print(find_details)
				find_details = Assignment.query.filter_by(id=find_assid).first()
				emptyisme.append(find_details)
		results[k] = emptyisme
		emptyisme = []
	for kkk,v in results.items():
		newstring = 'student'+ str(kkk)
		results2[newstring]= [k.serialize() for k in v]
	return jsonify(results2)


@app.route('/getallcourse/', methods=['GET'])
def get_all_course():
	if 'chatid' in request.args:
		chatid = int(request.args.get('chatid'))
		check_TA = TA.query.filter_by(chatid=chatid).first()
		if check_TA is None:
			return jsonify('Input chat ID does not belong to TA')
		else:
			check_TA = TA.query.filter_by(chatid=chatid).first().email
			course_detail = Course.query.filter_by(email=check_TA)
			return jsonify ([c.serialize() for c in course_detail])

@app.route('/getcourse/', methods=['GET'])
def get_course():
	course = Course.query.all()
	return jsonify ([c.serialize() for c in course])

@app.route('/getta/', methods=['GET'])
def getta():
	chatid = request.args.get('chatid')
	existing_ta = TA.query.filter_by(chatid=chatid).first()
	if existing_ta is not None:
		return jsonify('ta alr in db!')
	elif existing_ta is None:
		return jsonify('ta not in db!')

@app.route('/getOTP/', methods=['GET'])
def getOTP():
	print ("get OTP")
	if 'otp' in request.args:
		otp = request.args.get('otp')
		cur.execute("select email from otp where otp = '{}'".format(otp))
		email = cur.fetchone()
	if email is not None:
		chatid = request.args.get('chatid')
	  # need to add otp (email) into TA table, need to use telegram to retrieve chatid
		new_TA = TA(email=email, chatid=chatid)
		db.session.add(new_TA)
		db.session.commit()
		return jsonify('ta added')
	
	elif email is None:
		return jsonify('invalid otp')
	
	return


if __name__ == '__main__':
	app.run(debug=True)