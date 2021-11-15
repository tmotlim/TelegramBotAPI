
import logging
import requests
import telegram
from datetime import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
						  ConversationHandler)
########## HEROKU FLASK API ########################################
api_token = 'xxx'

bot = telegram.Bot(api_token)
URL_flask = 'https://remember4smu.herokuapp.com/'
create_ta = URL_flask + 'createTA/'
create_course = URL_flask + 'createcourse/'
post_ass = URL_flask + 'createassignment/'
update_ass = URL_flask + 'updateassignment/'
delete_ass = URL_flask + 'deleteassignment/'
get_ass = URL_flask + 'getassignment/'
get_ta = URL_flask + 'getta/'
get_otp = URL_flask + 'getOTP/'
##abit of naming error for APIs --> getallcourse will return only courses related to TAs
##getcourse will return ALL Courses
get_course = URL_flask + 'getallcourse/'
stud_get_course = URL_flask + 'getcourse/'
setreminder = URL_flask + 'createreminder/'
create_student = URL_flask + 'createstud/'
###################################################################

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)
###### set in rows of 5 for easy counting =) ################################
(CHOOSING, CHOOSING_ROLE, TA_CHOICE, TA_CHECK, TA_COURSE_OPTION, 
TA_SECTION_OPTION, TYPING_REPLY,TA_COURSE_SECTION_OPTION, STUDENT_CHOICE, TYPING_CHOICE,
 ASG_NAME, ASG_WEIGHTAGE, ASG_DATE, CHANGE_ASG_CHOICE, CHANGE_ASG,
 CHANGE_ASG_N,CHANGE_ASG_W,CHANGE_ASG_D, HANDLE_TA_SELECTION, DELETE_ASSIGNMENT,
 STU_GET_SECTION, STU_PROCESS_ASG, SUBSCRIPTION,STU_SEE_OTHER_COURSE, PROCESS_REMINDER,
 CHOSEN_ASG,
 
  )= range(26)




def start(update, context):
	try:
		del context.user_data['course_choice']
		del context.user_data['section_choice']
		del context.user_data['tries']
		#del context.user_data['chat_id']
	except:
		print('All good')
	context.user_data['tries'] = 1
	reply_keyboard = [['TA', 'Student'],
				  ['Done']]
	markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
	first_name = update.message.chat['first_name']
	update.message.reply_text(
		"Hello {}! Welcome to SMU's ✨Remember4U✨ \n May I know what your role is? \nFeel free to press /done at any point to end the convo".format(first_name),
		reply_markup=markup)

	return CHOOSING_ROLE
####### error handles when user does not choose between TA/ Student #### 
####### decide pm whether to remove cause might be abit ugly to keep prompting starting message ####
#### if we gonna put in then change line 555 as well ########
def error_TA_Student (update,context):
	if update.message.text == 'Done':
		return done(update, context) 
	chat_id = update.message.chat['id']
	first_name = update.message.chat['first_name']
	msg_text = 'Hello, {}! Please click either TA or Student.'.format(first_name)
	bot.send_message(chat_id=chat_id, text=msg_text)
	return start(update, context)	



def stu_getcourse(update, context):
	chat_id = update.message.chat['id']
	first_name = update.message.chat['first_name']
	msg_text = 'Welcome {}! Which course would you like to look at?'.format(first_name)

	course_keyboard = []
	r = requests.get(url=stud_get_course)
	for i in r.json():
		for k,v in i.items():
				if (k == 'Course Code') and ([v] not in course_keyboard):
					course_keyboard.append([v])

	course_keyboard.append(['Back'])

	sr_markup = ReplyKeyboardMarkup(course_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
	return STU_GET_SECTION

#### error handles the part if user clicks on Student multiple times on main page ###
def error_student(update,context):
	chat_id = update.message.chat['id']
	first_name = update.message.chat['first_name']
	msg_text = 'Oopsies, {}! Your fingers are too quick! Try Again'.format(first_name)
	bot.send_message(chat_id=chat_id, text=msg_text)
	return stu_getcourse(update,context)

def stu_getsection(update,context):
	chat_id = update.message.chat['id']
	interested_course = update.message.text
	context.user_data['course_choice'] = interested_course
	section_keyboard = []
	r = requests.get(url=stud_get_course)
	for i in r.json():
		if i['Course Code'] == interested_course:
			section_keyboard.append([i['Section Number']])
	section_keyboard.append(['Back'])
	msg_text = 'Sure! Which section would you like to look at?'
	sr_markup = ReplyKeyboardMarkup(section_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
	#STU_PROCESS_ASG --> goes def stud_process_asg and gives me the output of the get section
	return STU_PROCESS_ASG

def stu_process_asg(update,context):
	chat_id = update.message.chat['id']
	interested_course = context.user_data['course_choice']
	interested_section = update.message.text
	context.user_data['section_choice'] = interested_section
	params = {'course_code':interested_course, 'section_no':interested_section}
	r = requests.get(url = get_ass, params = params)
	if r.json() == []:
		msg_text = 'Oops! No assignments have been added yet!'
		bot.send_message(chat_id=chat_id, text=msg_text)
		return stu_getcourse(update,context)		
	else:
		msg_text = '✨✨✨✨ASSIGNMENTS✨✨✨✨\n' + '\n'
		for i in r.json():
			for k,v in i.items():
				if k == 'Assignment Name':
					msg_text += '📝{} : {} \n'.format(k,v)
				elif k == 'Assignment Deadline':
					msg_text += '📅{} : {} \n'.format(k,v)
				elif k == 'Assignment Weightage':
					msg_text += '󠀥󠀥󠀥‼️{} : {}% \n'.format(k,v) 
					msg_text += '\n'

		msg_text += '✨✨✨✨✨✨✨✨✨✨✨✨✨✨\n'
		bot.send_message(chat_id=chat_id, text=msg_text)
		yes_no_keyboard = [['yes!'], ['nahhh']]
		msg_text = "Would you like to receive reminders for this?"
		sr_markup = ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True)
		bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
		return SUBSCRIPTION

def subscription(update,context):
	chat_id = update.message.chat['id']
	context.user_data['chat_id'] = chat_id
	text = update.message.text
	first_name = update.message.chat['first_name']
	if text == 'yes!':
		params = {'name': first_name, 'chatid': chat_id}
		r = requests.post(url = create_student, params=params)
		if (r.json() == 'done') or (r.json() == 'student already exists'): 
			return setReminders(update,context)
		else:
			msg_text = 'Ops, something went wrong while creating student D='
			bot.send_message(chat_id=chat_id, text=msg_text)

	elif text == 'nahhh':
		msg_text = "Alright! Anything else i can help you with?"
		if_no_keyboard = [['See another course'], ["Nope, I am done!"]]
		sr_markup = ReplyKeyboardMarkup(if_no_keyboard, one_time_keyboard=True)
		bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
		return STU_SEE_OTHER_COURSE


def setReminders(update,context):
	#chat_id = update.message.chat['id']
	chat_id = context.user_data['chat_id']
	msg_text = "How many days (in digits) later do you want to receive the reminders? "
	bot.send_message(chat_id=chat_id, text=msg_text)
	return PROCESS_REMINDER

def process_reminder(update,context):
	num_days = update.message.text.replace(' ','')
	chat_id = context.user_data['chat_id']
	interested_course = context.user_data['course_choice']
	interested_section = context.user_data['section_choice']
	try: 
		num_days = int(num_days)
		json = {
			'course_code': interested_course,
			'section_no': interested_section,
			'number_of_days': num_days}
		params = {'chatid': chat_id}
		r = requests.post(url = setreminder, json=json, params=params)
		print (r.json())
		if r.json() == 'Number of days exceeds final deadline':
			msg_text = 'Reminder date exceeds assignment deadlines. Pls re-enter valid number of days.'
			bot.send_message(chat_id=chat_id, text=msg_text)
			return setReminders(update,context)
		elif r.json() == 'done':
			msg_text = 'alright! Will remind you {} days later! Returning back to start =)'.format(num_days)
			bot.send_message(chat_id=chat_id, text=msg_text)
			return start(update,context)
		elif r.json() == {}:
			msg_text = 'Oops! No assignments have been added yet.'
			bot.send_message(chat_id=chat_id, text=msg_text)
			return setReminders(update,context)
	except Exception:
		msg_text = "I don't understand that. Pls try again!"
		bot.send_message(chat_id=chat_id, text=msg_text)
		return setReminders(update,context)		
	

def TA(update, context):
	chat_id = update.message.chat['id']
	first_name = update.message.chat['first_name']
	context.user_data['first_name'] = first_name
	params = {'chatid': chat_id}
	r = requests.get(url=get_ta, params=params)
	#print (r.json())
	#slight assumptions made for this keyboard ### will have to change D= ###
	if r.json() == 'ta alr in db!':
		msg_text = "Welcome {}! \n Please select a course you want to edit:".format(first_name)
		params = {'chatid': chat_id}
		r = requests.get(url=get_course, params=params)
		course_keyboard = []
		section_keyboard = []
		for i in r.json():
			for k,v in i.items():
					if (k == 'Course Code') and ([v] not in course_keyboard):
						course_keyboard.append([v])
					elif (k == 'Section Number') and ([v] not in section_keyboard):
						section_keyboard.append([v])
		course_keyboard.append(['Back'])
		section_keyboard.append(['Back'])
		#storing my section keyboard so that i can use in my next step 
		context.user_data['section_keyboard'] = section_keyboard
		sr_markup = ReplyKeyboardMarkup(course_keyboard, one_time_keyboard=True)
		bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
		# context.user_data['course_choice'] = 
		return TA_COURSE_OPTION
	elif r.json() == 'ta not in db!':
		# print (r.json())
		msg_text = 'Pls enter your OTP for verification!'
		bot.send_message(chat_id=chat_id, text=msg_text)
		MessageHandler(Filters.text,check_ta)
		return TA_CHECK



def get_section(update,context):
	text = update.message['text']
	context.user_data['course_choice'] = text
	#print (context.user_data['course_choice'],'PRINT COURSE CHOICE HERE')
	msg_text = "Please select a section you would like to edit:"
	chat_id = update.message.chat['id']
	section_keyboard = context.user_data['section_keyboard']
	sr_markup = ReplyKeyboardMarkup(section_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id,text=msg_text, reply_markup=sr_markup)
	return TA_COURSE_SECTION_OPTION
#### for copy pasting ## 
#bot.send_message(chat_id=chat_id, text=msg_text)
###
### coding logic abit patchy but 

def handle_TA_selection(update,context):
	context.user_data['section_choice'] = update.message['text']
	return TA_actions(update, context)
# should my check_ta return a value?
def TA_actions(update, context):
	chat_id = update.message.chat['id']
	msg_text = 'What actions would you like to perform?'
	#print('Might have error here', update.message['text'])
	studentReq_keyboard = [['Add Assignment', 'Update Assignment', 'Delete Assignment'],['Back']]
	sr_markup = ReplyKeyboardMarkup(studentReq_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
	return TA_CHOICE



def check_ta(update,context):
	print ('CHECK -- TA')
	chat_id = update.message.chat['id']
	tries = context.user_data['tries']

	chat_id = update.message.chat['id']
	text = update.message['text']
	params = {'otp': text, 'chatid':chat_id}
	r = requests.get(url=get_otp, params=params)
	if r.json() == 'invalid otp':
		
		
		msg_text = 'There might be a mistake with the OTP. Pls try again. You tried {} times'.format(tries)
		bot.send_message(chat_id=chat_id, text=msg_text)
		tries += 1
		context.user_data['tries'] = tries
		if tries > 3:	
			msg_text = 'Sorry you have tried too many times. Maybe you are not a TA?'
			bot.send_message(chat_id=chat_id, text=msg_text)
			return start(update,context)
		return TA(update,context)	
	return TA_COURSE_OPTION
	
		





def addAssignment(update,context):
	chat_id = update.message.chat['id']
	msg_text = "ok cool! What's the assignment?"
	bot.send_message(chat_id=chat_id, text=msg_text)
	return ASG_NAME

def asg_name(update,context):
	chat_id = update.message.chat['id']
	assignment_name = update.message.text.capitalize()
	# assignment_name = assignment_name.capitalize()
	print ('THIS IS ASG NAME',assignment_name)
	context.user_data['assignment_name'] = assignment_name
	msg_text = "Almost done... What's the weightage of this assignment?"
	bot.send_message(chat_id=chat_id, text=msg_text)
	return ASG_WEIGHTAGE

def asg_weightage(update,context):
	chat_id = update.message.chat['id']
	weightage = update.message.text
	weightage = weightage.replace('%', '')
	context.user_data['assignment_weightage'] = weightage
	msg_text = "Lastly, tell me when's the deadline! Follow the following format: YYYY-MM-DD HH:MM:SS"
	bot.send_message(chat_id=chat_id, text=msg_text)
	return ASG_DATE

def asg_date(update,context):
	chat_id = update.message.chat['id']
	#use these 5 items to create
	deadline = datetime.strptime(update.message.text, '%Y-%m-%d %H:%M:%S')
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	assignment_name = context.user_data['assignment_name']
	weightage = context.user_data['assignment_weightage']
	params = {
			"course_code": course_code, 
			"section_no": section_no, 
			"assignment_name": assignment_name,
			"weightage": weightage,
			"deadline": deadline
			}
	r = requests.post(url = post_ass, params = params)
	del context.user_data['assignment_name']
	del context.user_data['assignment_weightage']
	if r.status_code == 200: 
		msg_text = "Assignment added successfully!"
		bot.send_message(chat_id=chat_id, text=msg_text)
		return TA_actions(update, context)
	else:
		msg_text = "Oops something went wrong!"
		bot.send_message(chat_id=chat_id, text=msg_text)
		return TA_actions(update, context)

	return TA_actions(update, context)

#ask if they want to add more assignments

def regular_choice(update, context):
	text = update.message.text
	context.user_data['choice'] = text
	update.message.reply_text(
		'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

	return TYPING_REPLY




def updateAssignment(update,context):

	chat_id = update.message.chat['id']
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	print('THIS IS MY COURSE CODE ##########################', course_code)
	print('THIS IS MY SECTION CODE ##########################', section_no)
	msg_text = "ok cool! What's the assignment?"
	params = {'course_code':course_code, 'section_no':section_no}
	r = requests.get(url = get_ass, params = params)
	print (r.status_code,"response code for Update assignment")
	assignment_keyboard = []
	print (r.json(),"view my assignments!!!")
	for i in r.json():
		for k,v in i.items():
			if k == 'Assignment Name':
				assignment_keyboard.append([v])
	assignment_keyboard.append(['Back'])
	#context.user_data['asg_keyboard'] = assignment_keyboard
	sr_markup = ReplyKeyboardMarkup(assignment_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
	return CHANGE_ASG_CHOICE#CHOSEN_ASG
##### handle chosen assignment #############################
def chosen_asg(update,context):
	context.user_data['assignment_name'] = update.message.text
	return change_assignment(update,context)#CHANGE_ASG_CHOICE
################### !!!IMPORTANT ##############################################
#				NEED TO del context.userdata if i PRESS DONE, haven't do yet!!
##################################################
#second part, after knowing which assignment to update, ask what to update
def change_assignment(update,context):
	#context.user_data['assignment_name'] = update.message.text
	chat_id = update.message.chat['id']
	msg_text = "So what changed?"
	studentReq_keyboard = [['Assignment Name', 'Assignment Weightage', 'Assignment Deadline'],['Back']]
	sr_markup = ReplyKeyboardMarkup(studentReq_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
	return CHANGE_ASG


def change_asg_items(update,context):
	chat_id = update.message.chat['id']
	text = update.message.text
	if text == 'Assignment Name':
		msg_text = "What's the new assignment name?"
		bot.send_message(chat_id=chat_id, text=msg_text)
		return CHANGE_ASG_N
	elif text == 'Assignment Weightage':
		msg_text = "What's the new assignment weightage?"
		bot.send_message(chat_id=chat_id, text=msg_text)
		return CHANGE_ASG_W
	elif text == 'Assignment Deadline':
		msg_text = "When's the new assignment deadline? Follow the following format: YYYY-MM-DD HH:MM:SS"
		bot.send_message(chat_id=chat_id, text=msg_text)
		return CHANGE_ASG_D
	#elif text == 'Back': #not needed anymore because i handled back in the 'states' at line 400ish
		#TA_actions is to return to the options page --> add, update, delete
		#return TA_actions(update, context)


def change_asg_name(update,context):

	chat_id = update.message.chat['id']
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	old_asg = context.user_data['assignment_name']
	new_asg_name = update.message.text
	params = {
				"course_code": course_code, 
				"section_no": section_no, 
				"assignment_name": old_asg,
				"new_assignment_name": new_asg_name}
	r = requests.put(url = update_ass, params = params)
	if r.status_code == 200:
		msg_text = 'assignment name updated!!'
		bot.send_message(chat_id=chat_id, text=msg_text)
	else:
		msg_text = 'failed to update D='
		bot.send_message(chat_id=chat_id, text=msg_text)
	del context.user_data['assignment_name']
	context.user_data['assignment_name'] = new_asg_name
	return change_assignment(update,context)
	#return TA_actions(update, context)


def change_asg_weightage(update,context):
	chat_id = update.message.chat['id']
	new_assignment_weight = update.message.text
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	assignment_name = context.user_data['assignment_name']		
			
	params = {
	"course_code": course_code, 
	"section_no": section_no, 
	"assignment_name": assignment_name,
	"new_assignment_weightage": new_assignment_weight}
	r = requests.put(url = update_ass, params = params)

	if r.status_code == 200:
		msg_text = 'assignment weightage updated!!'
		bot.send_message(chat_id=chat_id, text=msg_text)
	else:
		msg_text = 'failed to update D='
		bot.send_message(chat_id=chat_id, text=msg_text)
	return change_assignment(update,context)
	#return TA_actions(update, context)


def change_asg_date(update,context):
	chat_id = update.message.chat['id']
	deadline = datetime.strptime(update.message.text, '%Y-%m-%d %H:%M:%S')
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	assignment_name = context.user_data['assignment_name']		
			
	params = {
	"course_code": course_code, 
	"section_no": section_no, 
	"assignment_name": assignment_name,
	"new_assignment_deadline": deadline}
	r = requests.put(url = update_ass, params = params)
	#print(r.json,"this is the r.json")
	#print (r.status_code,"This is the status code for update deadline")
	if r.status_code == 200:
		msg_text = 'assignment date updated!!'
		bot.send_message(chat_id=chat_id, text=msg_text)
	else:
		msg_text = 'failed to update D='
		bot.send_message(chat_id=chat_id, text=msg_text)
	return change_assignment(update,context)
	#return TA_actions(update, context)

def deleteAssignment(update, context):
	chat_id = update.message.chat['id']
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	print('THIS IS MY COURSE CODE ##########################', course_code)
	print('THIS IS MY SECTION CODE ##########################', section_no)
	msg_text = "ok cool! What's the assignment?"
	params = {'course_code':course_code, 'section_no':section_no}
	r = requests.get(url = get_ass, params = params)
	print (r.status_code,"response code for Update assignment")
	assignment_keyboard = []
	print (r.json(),"view my assignments!!!")
	for i in r.json():
		for k,v in i.items():
			if k == 'Assignment Name':
				assignment_keyboard.append([v])
	assignment_keyboard.append(['Back'])
	#context.user_data['asg_keyboard'] = assignment_keyboard
	sr_markup = ReplyKeyboardMarkup(assignment_keyboard, one_time_keyboard=True)
	bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=sr_markup)
	return DELETE_ASSIGNMENT

def process_delete_asg(update, context):
	chat_id = update.message.chat['id']
	assignment_to_del = update.message.text
	course_code = context.user_data['course_choice']
	section_no = context.user_data['section_choice']
	json = {
			"course_code": course_code, 
			"section_no": section_no, 
			"assignment_name": assignment_to_del}
	r = requests.delete(url = delete_ass, json=json)
	if r.status_code == 200: 
		msg_text = "Assignment deleted successfully! How else can I help you?"
	else:
		msg_text = "Something went wrong, couldn't delete assignment D="
	bot.send_message(chat_id=chat_id, text=msg_text)
	return TA_actions(update,context)

def done(update, context):
	chat_id = update.message.chat['id']
	user_data = context.user_data
	msg_text = "Good bye! Don't forget your submissions~ 😃😃. \nif you miss me press /start or you can press /done when you want to end."
	bot.send_message(chat_id=chat_id, text=msg_text)

	user_data.clear()
	return ConversationHandler.END


def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	updater = Updater("1132665639:AAHV76op4rCfEaW9Qkyopma5c-7JpkQsvhg", use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={

			CHOOSING_ROLE: [MessageHandler(Filters.regex('^TA$'),
										  TA),
						   MessageHandler(Filters.regex('^Student$'),
											stu_getcourse),
					### removed because kinda ugly ### corresponds to line 64
							CommandHandler('done', done),
							MessageHandler(Filters.text,
											error_TA_Student),
						   
						   
						   ],
			STU_SEE_OTHER_COURSE: [CommandHandler('done', done),
				MessageHandler(Filters.regex('^Nope, I am done!$'), done),
							MessageHandler(Filters.regex('^See another course$'),stu_getcourse)
			],
			STU_GET_SECTION : [CommandHandler('done', done),
					#handles error when user taps Student too fast
					MessageHandler(Filters.regex('^Student$'), error_student),
					MessageHandler(Filters.regex('^Back$'), start),
							MessageHandler(Filters.text,stu_getsection),
			],				
			STU_PROCESS_ASG : [CommandHandler('done', done),
				MessageHandler(Filters.regex('^Back$'), stu_getcourse),
							MessageHandler(Filters.text,stu_process_asg),
			],
			SUBSCRIPTION : [CommandHandler('done', done),
				MessageHandler(Filters.regex('^Done$'), start),
							MessageHandler(Filters.text,subscription)
			],
			PROCESS_REMINDER : [
					CommandHandler('done', done),
				MessageHandler(Filters.text,process_reminder)],
			TA_CHOICE: [MessageHandler(Filters.regex('^Add Assignment$'),
										addAssignment),
						MessageHandler(Filters.regex('^Update Assignment$'),
										updateAssignment),
						MessageHandler(Filters.regex('^Delete Assignment$'),
										deleteAssignment),
						MessageHandler(Filters.regex('^Back$'), TA)   
						   ],
			TA_CHECK : [CommandHandler('done', done),
				MessageHandler(Filters.text,
										  check_ta),
						   ],
			TA_COURSE_OPTION: [CommandHandler('done', done),
			MessageHandler(Filters.regex('^Back$'), start),
				MessageHandler(Filters.text,get_section),
						   ],
			TA_COURSE_SECTION_OPTION: [CommandHandler('done', done),
			MessageHandler(Filters.regex('^Back$'), start),
				MessageHandler(Filters.text,handle_TA_selection),
						   ],
			HANDLE_TA_SELECTION : [CommandHandler('done', done),
				MessageHandler(Filters.text,
										  TA_actions),
								],
			ASG_NAME: [	MessageHandler(Filters.regex('^Back$'), start),
						MessageHandler(Filters.text, asg_name),
						   ],
			ASG_WEIGHTAGE: [MessageHandler(Filters.text, asg_weightage),
						   ],
			ASG_DATE: [MessageHandler(Filters.text, asg_date),
						   ],
						 
			CHANGE_ASG_CHOICE: [MessageHandler(Filters.regex('^Back$'), TA_actions),
				MessageHandler(Filters.text,chosen_asg),
						   
						   ],
			
			CHANGE_ASG: [MessageHandler(Filters.regex('^Back$'), TA_actions),
					MessageHandler(Filters.text, change_asg_items),

							],
			
			CHANGE_ASG_N: [MessageHandler(Filters.regex('^Back$'), TA_actions),
					CommandHandler('done', done),
					MessageHandler(Filters.text, change_asg_name),
						   ],
			CHANGE_ASG_W: [MessageHandler(Filters.regex('^Back$'), TA_actions),
					CommandHandler('done', done),
					MessageHandler(Filters.text, change_asg_weightage),
						   ],
			CHANGE_ASG_D: [MessageHandler(Filters.regex('^Back$'), TA_actions),
					CommandHandler('done', done),
				MessageHandler(Filters.text, change_asg_date),
						   ],
			DELETE_ASSIGNMENT: [MessageHandler(Filters.regex('^Back$'), TA_actions),
					MessageHandler(Filters.text, process_delete_asg),

							],
						   
						#    ASG_NAME: [MessageHandler(Filters.text, asg_name),
						#    ],
						#    ASG_NAME: [MessageHandler(Filters.text, asg_name),
						#    ],
			# STUDENT_CHOICE: [MessageHandler(Filters.text,
			# 							  received_information),
			# 			   ],
			# TYPING_REPLY: [MessageHandler(Filters.text,
			# 							  received_information),
			# 			   ],
		},

		fallbacks=[MessageHandler(Filters.regex('^Done$'), done),
					CommandHandler('done', done),
					MessageHandler(Filters.regex('^Back$'), start)
				]
	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()

