import time
import os
import datetime
import pandas as pd
import numpy as np

#Object to manage all the user's data

class DatabaseManager(object):

	def __init__(self,ProjectHandler = None, UserStatus = None, db_type = None):

		# Loading User Status
		self.UserStatus = UserStatus
		#Loading Project Handler - paths handler
		self.PH = ProjectHandler
		#Loading database type considering the running type
		self.db_type = db_type

		self.date = datetime.datetime.now()


	def load_Scale(self, time = None, weight = None, muscle_mass = None, bone_mass = None, fat_mass = None):

		#Loading data
		self.ScaleFile = open(self.scale_name, 'a')
		for i in range (len(time)):
			self.df_scale  = self.df_scale.append({'date':time[i],'Weight': weight[i], 'Muscle mass': muscle_mass[i], 'Bone mass': bone_mass[i] , 'Fat mass Weight': fat_mass[i]}, ignore_index=True)
		self.df_scale.to_csv(self.scale_name, index = False )

		self.ScaleFile.close()

	def load_ScanWatch(self, time = None, hr = None, calories = None, steps = None, hr_max = None, hr_min = None):

		print(hr_min)
	
		#Loading data
		self.ScanWatchfile = open(self.scanwatch_name, 'a')
		for i in range (len(time)):
			self.df_scanwatch = self.df_scanwatch.append({'date': time[i], 'HR_Average':hr[i],'Calories': calories[i], 'Steps': steps[i], 'HR_min': hr_min[i], 'HR_max': hr_max[i]}, ignore_index=True)
		self.df_scanwatch.to_csv(self.scanwatch_name, index = False )

		self.ScanWatchfile.close()

	def load_SleepMat(self, time = None, bd = None, dsd = None, dts = None, dtw = None, hr = None, lsd = None, rsd = None, rr = None, ss = None,wpc = None, wpd = None,
				   tst = None,ttb = None, awb = None, ap = None, obc = None, start_date = None, end_date = None, date_hr_ap = None, hr_ap = None, date_rr_ap = None, rr_ap = None):

		#Loading data
		self.SleepMatFile = open(self.sleepmat_name, 'a')
		max_size = max(len(date_hr_ap), len(date_rr_ap), len(time))
		print(date_hr_ap)
		if len(date_hr_ap) < max_size:

			date_hr_ap = np.append(date_hr_ap, [None] * (max_size - len(date_hr_ap)))
			date_rr_ap = np.append(date_rr_ap, [None] * (max_size - len(date_rr_ap)))
			hr_ap = np.append(hr_ap, [np.nan] * (max_size - len(hr_ap)))
			rr_ap = np.append(rr_ap, [np.nan] * (max_size - len(rr_ap)))

		#print(len(time))
		#print(len(date_hr_ap))
		#print(len(date_rr_ap))
		#print(len(hr_ap))
		#print(len(rr_ap))
		#print(hola)
		for i in range (len(time)):
			self.df_sleepsummary = self.df_sleepsummary.append({'date': time[i], 'Breathing disturbances': bd[i], 'Deep sleep duration': dsd[i], 'Duration to sleep': dts[i] , 'Duration to wakeup': dtw[i],
								'HR average': hr[i], 'Light sleep duration': lsd[i], 'Rem sleep duration': rsd[i], 'RR average': rr[i], 'Sleep score': ss[i], 'Wake up count': wpc[i],
								'Wake up duration': wpd[i], 'Total sleep time': tst[i], 'Total time in bed': ttb[i], 'Awake in bed': awb[i], 'Apnea': ap[i], 'Out of bed count': obc[i],
								'start_date': start_date[i], 'end_date': end_date[i], 'date_hr_sleep_ap':date_hr_ap[i] , 'hr_sleep_ap':hr_ap[i], 'date_rr_sleep_ap':date_rr_ap[i], 'rr_sleep_ap':rr_ap[i]}, ignore_index=True)
		self.df_sleepsummary.to_csv(self.sleepmat_name, index = False )

	
		self.SleepMatFile.close()


	def load_SensorInfo(self, sensor = None, hash_deviceid = None, MAC_address = None):
		
		self.DevicesFile = open(self.devices_info, 'a')
		for i in range (len(sensor)):

			self.df_devices = self.df_devices.append({'Device': sensor[i], 'Hash_deviceid': hash_deviceid[i], 'MAC_address': MAC_address[i]}, ignore_index = True)
		
		self.df_devices.to_csv(self.devices_info, index = False )

		self.DevicesFile.close()


	def load_intra_activity(self, time = None, hr = None, time_steps = None, steps = None,  time_calories = None, calories = None):

		self.ScanIntraFile = open(self.scanwatch_intraday, 'a')

		max_size = max(len(time), len(time_steps), len(time_calories))

		if len(time) < max_size:

			time = np.append(time, [np.nan] * (max_size - len(time)))
			hr = np.append(hr, [np.nan] * (max_size - len(hr)))

		# Fill time_steps and steps with NaN until they reach max_size

		if len(time_steps) < max_size:

			time_steps = np.append(time_steps, [np.nan] * (max_size - len(time_steps)))
			steps = np.append(steps, [np.nan] * (max_size - len(steps)))

		# Fill time_calories and calories with NaN until they reach max_size

		if len(time_calories) < max_size:
			time_calories = np.append(time_calories, [np.nan] * (max_size - len(time_calories)))
			calories = np.append(calories, [np.nan] * (max_size - len(calories)))


		for i in range(max_size):

			self.df_scawatch_intra = self.df_scawatch_intra.append({'date HR': time[i], 'Heart Rate': hr[i], 'date Steps': time_steps[i], 'Steps': steps[i], 'date Calories': time_calories[i] , 'Calories': calories[i]},ignore_index = True)

		self.df_scawatch_intra.to_csv(self.scanwatch_intraday, index = False)
		self.ScanIntraFile.close()

	def load_intra_sleep(self, start_date = None, end_date = None, ss = None, hr = None, hr_date = None, rr = None, rr_date = None, snoring = None, snoring_date = None, sdnn_1 = None, sdnn_1_date = None):

		max_size = max(len(start_date), len(hr_date))
		self.SleepIntraFile = open(self.sleepmat_intraday, 'a')
		#print(hr)

		if len(start_date) < max_size:

			start_date = np.append(start_date, [np.nan] * (max_size - len(start_date)))
			end_date = np.append(end_date, [np.nan] * (max_size - len(end_date)))
			ss = np.append(ss, [np.nan] * (max_size - len(ss)))

		for i in range(max_size):
			#print('Here intra')

			self.df_sleep_intra  = self.df_sleep_intra.append({'startdate': start_date[i], 'enddate': end_date[i], 'Sleep state':ss[i], 'Heart Rate date': hr_date[i], 'Heart Rate': hr[i] ,  'Respiration rate date': rr_date[i],
			 													'Respiration rate': rr[i] , 'Snoring date': snoring_date[i], 'Snoring': snoring[i], 'sdnn_1 date': sdnn_1_date[i], 'sdnn_1': sdnn_1[i]} ,ignore_index = True)


		self.df_sleep_intra.to_csv(self.sleepmat_intraday, index = False)
		self.SleepIntraFile.close()


	def load_usage(self, user_id = None, start_date = None, end_date = None, report_generation_date = None, sleep_usage = None, sleep_battery = None, sleep_lastday = None,  watch_usage = None, watch_battery = None, watch_lastday = None,  scale_usage = None, scale_battery = None, scale_lastday = None):	
	
		self.df_usage = self.df_usage.append({
			'id': user_id,
			'start_date': start_date,
			'end_date': end_date,
			'report_generation_date':  report_generation_date,
			'SleepMat Usage': sleep_usage,
			'SleepMat Battery': sleep_battery,
			'SleepMat Last reading': sleep_lastday,
			'Watch Usage': watch_usage,
			'Watch Battery': watch_battery,
			'Watch Last reading': watch_lastday,
			'Scale Usage': scale_usage,
			'Scale Battery': scale_battery,
			'Scale Last reading': scale_lastday,
			}, ignore_index=True)

		# Updated DataFrame to the CSV file
		self.df_usage.to_csv(self.usage_info, index=False, mode='a', header = False)

		self.UsageFile.close()


	def set_User(self, US):

		#User status
		self.UserStatus = US

	def set_date_report(self, date):

		self.report_date = date

		print(self.report_date)


	def get_path(self):

		return(self.user_folder)


	def create_session(self):

		#Create folders for each user

		self.user_folder_wd = self.PH + "/" +"General" + "/" + str(self.UserStatus['id'])

		self.user_folder = self.PH + "/" +"General" + "/" + str(self.UserStatus['id']) +"/"+ self.report_date


		#Create folders for each user - testing purposes



	

		if not os.path.exists(self.user_folder):
			os.makedirs(self.user_folder)


		#Create sensors file

		self.scale_name = self.user_folder_wd+ "/Scale.csv"
		self.scanwatch_name = self.user_folder_wd + "/ScanWatch_summary.csv"
		self.sleepmat_name = self.user_folder_wd + "/SleepMat_summary.csv"

		self.devices_info = self.user_folder_wd+ "/Devices.csv"
		self.usage_info = self.user_folder_wd+ "/Usage.csv"

		#Create sensors file for higher granularity

		self.scanwatch_intraday = self.user_folder_wd + "/ScanWatch_intra_activity.csv"
		self.sleepmat_intraday = self.user_folder_wd + "/Sleepmat_intra_activity.csv"
		

		#Open the files to save the data
		self.ScaleFile = open(self.scale_name, 'a+')
		self.ScanWatchfile = open(self.scanwatch_name, 'a+')
		self.SleepMatFile = open(self.sleepmat_name, "a+")
		self.DevicesFile = open(self.devices_info, "w+")
		
		self.ScanIntraFile = open(self.scanwatch_intraday, "a+")
		self.SleepIntraFile = open(self.sleepmat_intraday, "a+")

		self.UsageFile = open(self.usage_info, "a+")

		#Headers on devices files

		self.df_devices = pd.DataFrame({'Device': [], 'Hash_deviceid': [], 'MAC_address': []} )
		self.df_devices.to_csv(self.devices_info, index = False )

		#Headers and data on usage files
		try:
			existing_data = pd.read_csv(self.usage_info)
			self.df_usage = existing_data
		except:
			
			self.df_usage = pd.DataFrame({'id': [], 'start_date': [], 'end_date': [], 'report_generation_date':[], 'SleepMat Usage': [], 'SleepMat Battery': [],'SleepMat Last reading' : [], 'Watch Usage': [], 'Watch Battery': [], 'Watch Last reading': [],
				 'Scale Usage': [], 'Scale Battery': [], 'Scale Last reading': []})
		
			self.df_usage.to_csv(self.usage_info, index = False )

		#Headers on each files

		
		try:
			existing_data_hr = pd.read_csv(self.scanwatch_name)
			self.df_scanwatch = existing_data_hr

		except:
			self.df_scanwatch = pd.DataFrame({'date': [], 'HR_Average': [], 'Calories': [], 'Steps': [], 'HR_min': [], 'HR_max':[]} )
			self.df_scanwatch.to_csv(self.scanwatch_name, index = False )


		try:
			existing_data_scale = pd.read_csv(self.scale_name)
			self.df_scale = existing_data_scale
		except:

			self.df_scale = pd.DataFrame({'date': [], 'Weight': [], 'Muscle mass': [], 'Bone mass': [] , 'Fat mass Weight': [] } )
			self.df_scale.to_csv(self.scale_name, index = False )

		try:
			existing_data_sleep = pd.read_csv(self.sleepmat_name)
			self.df_sleepsummary = existing_data_sleep

		except:
			self.df_sleepsummary = pd.DataFrame({'date': [], 'Breathing disturbances': [], 'Deep sleep duration': [], 'Duration to sleep': [] , 'Duration to wakeup': [],
									'HR average': [], 'Light sleep duration': [], 'Rem sleep duration': [], 'RR average': [], 'Sleep score': [], 'Wake up count': [],
								 	'Wake up duration': [], 'Total Sleep Time': [], 'Wake up duration': [], 'Total sleep time': [], 'Total time in bed': [], 'Awake in bed': [], 'Apnea': [], 'Out of bed count': [], 'start_date': [],
									'end_date': [], 'date_hr_sleep_ap':[] , 'hr_sleep_ap':[], 'date_rr_sleep_ap':[], 'rr_sleep_ap':[] } )
			self.df_sleepsummary.to_csv(self.sleepmat_name, index = False )
		try:
			existing_data_scanintra = pd.read_csv(self.scanwatch_intraday)
			self.df_scawatch_intra = existing_data_scanintra
		except:
			self.df_scawatch_intra = pd.DataFrame({'date HR': [], 'Heart Rate': [], 'date Steps':[], 'Steps': [], 'date Calories': [] , 'Calories': []})
			self.df_scawatch_intra.to_csv(self.scanwatch_intraday, index = False)

		

		try:
			existing_data_sleepintra = pd.read_csv(self.sleepmat_intraday)
			self.df_sleep_intra = existing_data_sleepintra 

		except:
			self.df_sleep_intra =  pd.DataFrame({'startdate':[], 'enddate': [], 'Sleep state':[], 'Heart Rate date': [], 'Heart Rate': [] ,  'Respiration rate date': [],
			 												'Respiration rate': [] , 'Snoring date': [], 'Snoring': [], 'sdnn_1 date': [], 'sdnn_1': []})
			self.df_sleep_intra.to_csv(self.sleepmat_intraday, index = False)

		#Closing files

		self.ScaleFile.close()
		self.ScanWatchfile.close()
		self.SleepMatFile.close()
		self.ScanIntraFile.close()
		self.SleepIntraFile.close()


	def close_all_cvs_files(self):

		#Closing files

		self.ScaleFile.close()
		self.ScanWatchfile.close()
		self.SleepMatFile.close()
		self.ScanIntraFile.close()
		self.SleepIntraFile.close()


	def cleaning_cvs_files(self, cvs_from = None):


		if cvs_from == 'Scan_summary':
			file_name = self.scanwatch_name
			ref_column_name = 'date'
		elif cvs_from == 'Sleep_summary':
			file_name = self.sleepmat_name
			ref_column_name = 'start_date'
		elif cvs_from == 'Scale':
			file_name = self.scale_name
			ref_column_name = 'date'
		elif cvs_from == 'Intra_watch':
			file_name = self.scanwatch_intraday
			ref_column_name = 'date HR'
		elif cvs_from == 'Intra_sleep':
			file_name = self.sleepmat_intraday
			ref_column_name = 'startdate'
		
		# Open the corresponding data file
		df = pd.read_csv(file_name, header = 0, delimiter=',')
		#Converting the dates to datetime
		#print(HOLA)
		if cvs_from == 'Intra_watch':
			df[ref_column_name] = pd.to_datetime(df[ref_column_name], unit = 's') 
		elif cvs_from == 'Intra_sleep':
			df[ref_column_name] = pd.to_datetime(df[ref_column_name], unit = 's')
		else:
			df[ref_column_name] = pd.to_datetime(df[ref_column_name])

		# Sorting values according the date
		df = df.sort_values(by = ref_column_name, ascending=False)
		df = df.drop_duplicates(subset=ref_column_name, keep = 'first')
		

	

		if cvs_from == 'Intra_watch':
			df[ref_column_name] = df[ref_column_name].apply(lambda x: x.timestamp() if pd.notnull(x) else np.nan)
		if cvs_from == 'Intra_sleep':
			df[ref_column_name] = df[ref_column_name].apply(lambda x: x.timestamp() if pd.notnull(x) else np.nan)
		
			



		#Info to csv file
		df.to_csv(file_name, index=False)
		#file_name.close()
	
	




	def set_user(self, p):

		self.user = p

	def register_user(self, id_user = 'nd'):

		print('Here in register user from SM')

		self.user = {"id" : id_user}
		self.save_user()
		self.set_User(US = self.UserStatus)
		self.create_session()
		return self.UserStatus

	def save_user(self):

		print('In save_user')

		#Check the user in the database

		self.UserStatus = self.check_user()
		print('UserStatus', self.UserStatus)

		path = self.PH

		if not self.UserStatus['registered']:

			print('Here not registered')

			#path = self.PH

			if os.path.exists(path + "/Users.csv"):

				f = open(path + "/Users.csv", 'a')

				#save new user information
				#rint()

				f.write(self.user['id']+";"+(str(self.date.year) +"-"+ str(self.date.month)+"-"+ str(self.date.day))+'\n'
                    )

		else:
			print('registered')

			#f = open(path + "/Users.csv", 'w+')
			#f.write("Id; Date of Registration\n")
			#f.close()

			#f = open(path + "/Users.csv", 'a')
			#save new user information
			#f.write(self.user['id']          +";" +'\n')
			#close the file
			#f.close()


	def check_user(self):

		print('Checking User Status')

		path = self.PH

		if os.path.exists(path + "/Users.csv"):

			print('Exists')

			f = open(path + "/Users.csv", 'r')
			lines = f.readlines()
			f.close()
			users = lines[1:]
			print(users)
			#check patient lists
			for p in users:
				pl = p.split(";")
				if pl[0] == self.user['id']:
					print("User Already in the database")
					return {"registered" : True,"id" : self.user['id']}

			return{"registered" : False, "id" : self.user['id']}

		else:

			print('No Exists')

			f = open(path + "/Users.csv", 'w+')
			f.write("Id; Date of Registration\n")
			f.close()
			return {"registered" : False, "id" : self.user['id']}
		
	def delete_usage(self):
		pass




