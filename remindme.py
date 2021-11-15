#get daily
#get reminders url stuff
from flask import Flask, request, jsonify
import requests 
import json
import telegram
from telegram import ReplyKeyboardMarkup,ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from datetime import datetime,date
import time

while True:
	api_token = '1132665639:AAHV76op4rCfEaW9Qkyopma5c-7JpkQsvhg' # fill in your api token here 
	bot = telegram.Bot(api_token)
	URL_flask = 'https://remember4smu.herokuapp.com/'
	getreminderURL = URL_flask + 'getreminder/'
	############################################################################3
	date_now = {"today":str(datetime.now().date())}
	#date_now = {"today":"2020-04-19"}
	print("datenow",date_now)
	r = requests.get(url=getreminderURL,json = date_now)
	#print('R: ',type(r),r)
	r = r.json()
	print(r,"this is r",type(r))
	if r == {}:
		None
	else:
		for k,v in r.items():
			msg_text = '✨✨✨✨Your Requested Reminder!✨✨✨✨\n'
			msg_text += '✨✨✨✨ASSIGNMENTS✨✨✨✨\n'
			#print("length of v",len(v))
			for i in range (len(v)):
				for desc,values in v[i].items():
					if desc == 'Assignment Name':
						msg_text += '📝{} : {} \n'.format(desc,values)
					elif desc == 'Assignment Deadline':
						msg_text += '📅{} : {} \n'.format(desc,values)
					elif desc == 'Assignment Weightage':
						msg_text += '󠀥󠀥󠀥‼️{} : {}% \n'.format(desc,values)
				msg_text += '\n'

			print("CMDLINE",msg_text)
			bot.send_message(chat_id=k, text=msg_text)
	time.sleep(86400)
