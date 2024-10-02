import os, sys

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../db'))
sys.path.append(ab_path)

import lib.SessionManager as SM
import shutil

class General(object):

	def __init__(self, 
			  db_type: None):
		#load project handler
		self.dir = os.getcwd()

		self.db_type = db_type
		print('from db', self.db_type)

	
		self.database_path = self.dir + '/'+'db'

		
		
		#self.PH = ProjectHandler
		# Update user status
		self.UserStatus = {"registered" : False, "id":""}

		self.SM = SM.DatabaseManager(ProjectHandler = self.database_path, UserStatus = self.UserStatus,  db_type = self.db_type)


		#Create session manager
		self.TherapyStatus = {"user": "none", "mode":0}


	def register(self, user = None):
		#Function to register the patient in the DB
		self.UserStatus = self.SM.register_user(id_user = user)
		

		#self.TherapyStatus['user'] = self.UserStatus['name']


	def login(self, i):

		p = {"id": i}


		self.SM.set_User(p = p)

		status = self.SM.check_user()

		self.SM.set_User(US = status)

		#self.TherapyStatus['user'] = status['name']

		return status


	def clear_database(self):

		folder = self.PH

		if os.path.exists(folder):

			#remove directions

			for f in os.listdir(foler):
				f = os.path.join(folder, f)

				shutil.rmtree(f)