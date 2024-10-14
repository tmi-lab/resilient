import sys
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from withings_api import WithingsAuth, WithingsApi, AuthScope
from withings_api.common import GetSleepField, GetSleepSummaryField, get_measure_value, MeasureType, CredentialsType, MeasureGetActivityResponse, AuthFailedException
import arrow
import time
import numpy as np
import math
import json
from datetime import timedelta, datetime



#To save users credential and update refresh the token
import argparse
import os
from os import path
import pickle
from typing import cast
from urllib import parse
from typing_extensions import Final
import pandas as pd

#Module: Data utilities module - preprocessing of the data 
import data_utils.data_utils as data_utils
# Module: Database libraries to save Users' data 
import db.database as database
#Module : Databasde Django api

import db.database_django as database_api

#Module: Graphics generation class
import resources.Graph_generation as graph
# Module: PDF generation class to generate the reports 
import resources.PDF_generation as pdf_gen




#This code is an adaptation of the following repository: https://github.com/vangorra/python_withings_api
#With libraries and methods modified.


# IMPORTANT!
# Create the developer account: https://developer.withings.com/developer-guide/v3/integration-guide/advanced-research-api/developer-account/create-your-accesses-no-medical-cloud

# This class is for making the authorization procedures and the OAuth2 flow
# Please refer to the following pages to have a greater understanding :
# https://developer.withings.com/developer-guide/v3/integration-guide/advanced-research-api/get-access/oauth-web-flow
# Access and refresh tokens : https://developer.withings.com/developer-guide/v3/integration-guide/advanced-research-api/get-access/access-and-refresh-tokens



class Devices_OAuth2flow(object):

	def __init__(self, client_id: None, 
					   costumer_secret: None, 
					   callback_uri: None,
					   report_type: None,
					   id_participant: None,
					   running_type: None,
					   setup_month: None,
					   from_report: None,
					   to_report:None):
		#Running type
		self.running_type = running_type
		# Report type
		self.report_type = report_type
		#If it is a report with fixed length
		self.setup_month = setup_month
		#If it is between arranged dates
		self.from_report = from_report
		self.to_report = to_report
		
		# Inputs: client_id, consumer_secret, callback_uri
		# Take into account that this inputs will be created after you
		# create your developer account

		self.client_id = client_id
		self.costumer_secret = costumer_secret
		self.callback_uri = callback_uri



		# Creates the database object
		self.database = database.General(db_type = self.running_type)
		#Create database object api
		self.database_api = database_api.Database_API()

		

		if self.report_type == 1:
			self.dates()

		# Creates the data utils object
		self.data_utils = data_utils.Data_Handler()
		
	

		# ID for each user
		#self.id_user = str(next(iter(id_participant)))
  
		self.id_user = id_participant
	

		#Create the credentials File
		# This file has the authorization and refresh token which are
		# used to acquire the data fromo Withings server 

		self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		self.db_path = "db"
		self.additional_path = "db/General"
		credentials_path = ".credentials"
		users_db = "Users.csv"


		#Path to credentials from each users

		self.final_path = path.abspath(path.join(self.base_path, self.additional_path, self.id_user, credentials_path))
		#Path to Users.csv file
		self.users_path = path.abspath(path.join(self.base_path, self.db_path, users_db))


		# Get info from the database

		# Get id from API databse

		self.db_id = self.database_api.get_unique_id(id_user = self.id_user)
		self.database.SM.set_User({"registered" : True, "id": self.id_user})
		self.uuid_db = self.db_id['users'][0]['id']
		
		self.CREDENTIALS_FILE: Final = self.final_path
		print(self.CREDENTIALS_FILE)
		
	def create_auth_url(self):

		# This function is to create the URL which will be used by the
		# user to authorize the acquisition of the data
		print('isusssssssssssssssssssssssssssssse')
		print(self.client_id)
		print(self.costumer_secret)
		print(self.callback_uri)

		self.auth = WithingsAuth(

			client_id = str(self.client_id),
			consumer_secret= str(self.costumer_secret),
			callback_uri = str(self.callback_uri),

			scope=(
				AuthScope.USER_ACTIVITY,
				AuthScope.USER_METRICS,
				AuthScope.USER_INFO,
				AuthScope.USER_SLEEP_EVENTS,
				)
			)

		self.authorize_url = self.auth.get_authorize_url()

	def get_user_credentials(self):

		#Depending if the device is already registered and has credentials an authorization
		#either an authorization token can be generated (for new devices) or the refresh token
		#can be used if data is requested (and 3 hours have passed after the last call)

		if path.isfile(self.CREDENTIALS_FILE):
			print("Attempting to load credentials from:", self.CREDENTIALS_FILE)
			self.api = WithingsApi(self.load_credentials(), refresh_cb = self.save_credentials)
			try:
				self.api.user_get_device()
			except MissingTokenError:
				os.remove(self.CREDENTIALS_FILE)
				print("Credentials in file are expired. Re-starting auth procedure...")
			except AuthFailedException:
				print('Im here AuthFailedException')

				#m = self.load_credentials() 
				#auth_token = m.refresh_token

		if not path.isfile(self.CREDENTIALS_FILE):

			print("Attempting to get credentials...")
			auth = self.create_auth_url()


			print("Goto this URL in your browser and authorize:", self.authorize_url)
			print("Once you are redirected, copy and paste the whole url"
		        "(including code) here."
		     )

			redirected_uri: Final = input("Provide the entire redirect uri: ")

			redirected_uri_params: Final = dict(
				parse.parse_qsl(parse.urlsplit(redirected_uri).query)
				)

			self.auth_code: Final = redirected_uri_params["code"]
			print("Getting credentials with auth code", self.auth_code)
			self.save_credentials(self.auth.get_credentials(self.auth_code))
			self.api = WithingsApi(self.load_credentials(), refresh_cb = self.save_credentials)

		orig_access_token = self.api.get_credentials().access_token
		print("Refreshing token...")
		self.api.refresh_token()
		print("After Refreshing")
		print( 'UserID', self.api.get_credentials().userid)

		self.dates_report(setup_month = self.setup_month, from_date = self.from_report, to_date = self.to_report)

	def dates_report(self, setup_month = None, from_date = None, to_date = None):
		#Registration date from API
		try:
			registration_date = self.db_id['users'][0]['created_at']
		except:
			registration_date = datetime.now().strftime("%Y-%m-%d")

		#calculate the number of days between the register day and the current date
		date_of_registration =  datetime.strptime(registration_date, '%Y-%m-%d')
		#Setting the initial date - considaring current day
		self.ending_day_c = self.data_utils.initial_day()

		
		# Calculate the difference in days
		days_difference = ((datetime.now()- timedelta(days=self.ending_day_c)) - date_of_registration).days

		#For reports of 3 months
		if setup_month:
			if days_difference > 90:
				self.starting_day_c = -(90 - self.ending_day_c)
			else:
				self.starting_day_c = - days_difference
		else:
			# This is to test last 
			self.ending_day_c = -to_date
			self.starting_day_c = -from_date

		#Conversion to datetime for db
		self.end_date = arrow.utcnow().shift(days = self.ending_day_c).replace(hour=0, minute=0, second=0)
		self.end_date = self.end_date.datetime
		self.end_date_timestamp = self.end_date.timestamp()
		self.start_date = arrow.utcnow().shift(days = self.starting_day_c).replace(hour=0, minute=0, second=0)
		self.start_date = self.start_date.datetime
		self.start_date_timestamp = self.start_date.timestamp()

		#From withings current week 
		self.ending_day_current_week = self.data_utils.initial_day()
		self.starting_day_current_week = self.ending_day_current_week - 7
		# Dates
		self.initial_dates = arrow.utcnow().shift(days = self.starting_day_c)
		self.initial_dates_rep = self.initial_dates.format('D-MMM-YYYY')
		self.initial_dates_table = self.initial_dates.format('D MMM ')

		self.ending_dates = arrow.utcnow().shift(days = self.ending_day_c)
		self.ending_dates_table = self.ending_dates.format('D MMM ')

		#Create folders for week report
		self.database.SM.set_date_report(date = datetime.now().strftime('%Y-%m-%d'))
		self.database.SM.create_session()
		

	def devices_info(self):

		# This function generates the device information. For instance, the hash_deviceid,
		# battery levels, serial number, device_id, among others. Some of this parameters
		# are used in other services to activate functions.
		
		expected_model_ids = {'Sleep Monitor', 'Activity Tracker', 'Scale'}
		self.battery = {}
		devices = self.api.user_get_device()
		devices = devices['devices']
		
		# Creating a dictionary with type_id as keys and battery as values
		self.battery = {device['type']: device['battery'] for device in devices}
		
		for model_id in expected_model_ids:
			if model_id not in self.battery:
				self.battery[model_id] = None

	def register_devices(self):
		# This function register the device information.
		ids_list = [] 
		devices = self.api.user_get_device()
		print(devices)
		devices = devices['devices']

		self.values_devices = {
			'scale': None,
			'sleep_mat': None,
			'scan_watch': None
			}
		
		filtered_data = [{'Device': d['type'], 'Hash_deviceid': d['hash_deviceid'], 'MAC_address': d['mac_address']} for d in devices]
		
		type_d = [i['type'] for i in devices]
		hash_deviceid = [i['hash_deviceid'] for i in devices]
		MAC_address = [i['mac_address'] for i in devices]
		# Devices to csv database files
		self.database.SM.load_SensorInfo(sensor = type_d, hash_deviceid = hash_deviceid, MAC_address = MAC_address)
		# Devices to API database -devices
		self.database_api.upload_device_info(dict = filtered_data)
		for i in range(len(hash_deviceid)):
			ids_devices = self.database_api.get_device_info(device_hash = hash_deviceid[i])
			ids_list.append(ids_devices)
		
		for item in ids_list:
			self.values_devices.update(item)
		# Devices to API database - user
		self.database_api.update_devices_in_user(user_uid = self.uuid_db, scale_id = self.values_devices['scale'],
										    scanwatch_id = self.values_devices['scan_watch'], sleepmat_id = self.values_devices['sleep_mat'])

	def create_nonce(self):

		# This function generates the nonce. The nonce is a signature used
		# to sign requests and it is used by some Withings services.

		signature = self.api.get_signature()
		self.nonce = signature['body']['nonce']
		#print('nonce', self.nonce)

	#Function  to acquire scale values 
	
	def scale_data(self):
		self.scale_data_w = {}
		self.monthly_scale_data = {}

		#Extracting scale current week data from 
		scale_values_w = self.api.measure_get_meas(startdate=arrow.utcnow().shift(days = self.starting_day_current_week).replace(hour=23, minute=59, second=59),
											  enddate = arrow.utcnow().shift(days= self.ending_day_current_week).replace(hour=23, minute=59, second=59), lastupdate = None)
		#Current week values
		self.scale_data_w['date'] = [arrow.get(x.date) for x in scale_values_w.measuregrps]
		self.scale_data_w['measures'] = [x.measures for x in scale_values_w.measuregrps]

		self.last_scale = self.scale_data_w['date']
		self.weight, self.muscle_mass, self.bone_mass, self.fat_mass, hydration = self.data_utils.scale_data_extractor(self.scale_data_w['measures'])
		self.scale_data_w['date'], self.weight = self.data_utils.data_cleaning(self.scale_data_w['date'],self.weight)

		print(self.weight)
		print(type(self.weight))

		# Agreggated data from last three months from db
		scale_values_db = self.database_api.get_scale_data(user = self.id_user, start_date = self.start_date, end_date = self.end_date)
		data = [{key: value for key, value in entry.items() if key != 'id'} for entry in scale_values_db['scales']]

		# Extracting dates and steps into separate arrays
		dates_db = [entry['date'] for entry in data]
		dates_db = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in dates_db]

		weight_db = [entry['weight'] for entry in data]
		weight_db = np.array(weight_db, dtype=float)
	
		muscle_mass_db = [entry['muscle_mass'] for entry in data]
		#muscle_mass_db = np.array(muscle_mass_db, dtype=float)

		bone_mass_db = [entry['bone_mass'] for entry in data]
		#bone_mass_db = np.array(bone_mass_db, dtype=float)

		fat_mass_db = [entry['fat_mass'] for entry in data]
		#fat_mass_db = np.array(fat_mass_db, dtype=float)

		
		# Agreggated values

		self.dates_scale_agg = dates_db + self.scale_data_w['date']
		self.weight_agg = np.concatenate((weight_db ,self.weight))
		self.muscle_mass_agg = np.concatenate((muscle_mass_db, self.muscle_mass))
		self.bone_mass_agg = np.concatenate((bone_mass_db, self.bone_mass))
		self.fat_mass_agg = np.concatenate((fat_mass_db, self.fat_mass))

	#Functions to acquire watch values
	def intra_activitydata_watch(self):

		dates_hr_watch = []
		hr_watch = []
		dates_steps_watch = []
		steps_watch = []
		dates_calories_watch = []
		calories_watch = []
		dates_to_test = {}
		hr_to_test = {}


		self.dates_HR_watch_agg = []
		self.hr_watch_agg = []
		self.dates_step_watch_agg = []
		self.steps_watch_agg = []
		self.dates_cal_watch_agg = []
		self.cal_watch_agg = []
		self.intra_activity_watch = {} 

		#Variables to extract intra activity values
		week_days = list(range(self.starting_day_current_week, self.ending_day_current_week))

		week_days.append(week_days[-1]+1)
		
		for i in range (len(week_days)):
			
			self.meas_intraactivity = self.api.measure_get_intraactivity(startdate= arrow.utcnow().shift(days= week_days[i]).replace(hour=0, minute=0, second=0), enddate=arrow.utcnow().shift(days = week_days[i]+1).replace(hour=0, minute=0, second=0))
			measurement_intra_activity = {timestamp: {key: value for key, value in self.meas_intraactivity['series'][timestamp].items() if key not in ['model_id', 'deviceid', 'model']} for timestamp in self.meas_intraactivity['series']}
			dates_hr_watch = [key for key, sub_dict in measurement_intra_activity.items() if 'heart_rate' in sub_dict]
			hr_watch = [sub_dict['heart_rate'] for sub_dict in measurement_intra_activity.values() if 'heart_rate' in sub_dict]

			dates_steps_watch = [key for key, sub_dict in measurement_intra_activity.items() if 'steps' in sub_dict]
			steps_watch = [sub_dict['steps'] for sub_dict in measurement_intra_activity.values() if 'steps' in sub_dict]

			dates_calories_watch = [key for key, sub_dict in measurement_intra_activity.items() if 'calories' in sub_dict]
			calories_watch = [sub_dict['calories'] for sub_dict in measurement_intra_activity.values() if 'calories' in sub_dict]

			dates_hr_watch, hr_watch = self.data_utils.hr_filtering(dates_hr_watch, hr_watch)

			dates_to_test[i] = dates_hr_watch
			hr_to_test[i] = hr_watch
			self.dates_HR_watch_agg.append(dates_hr_watch)
			self.hr_watch_agg.append(hr_watch)
			self.dates_step_watch_agg.append(dates_steps_watch)
			self.steps_watch_agg.append(steps_watch)
			self.dates_cal_watch_agg.append(dates_calories_watch)
			self.cal_watch_agg.append(calories_watch)

		
		#Heart rate values from watch after processing
		self.dates_HR_watch_agg = sum(self.dates_HR_watch_agg ,[])
		self.hr_watch_agg = sum(self.hr_watch_agg,[])
		#Step values after processing
		self.dates_step_watch_agg = sum(self.dates_step_watch_agg,[])
		self.steps_watch_agg = sum(self.steps_watch_agg,[])
		#Calories values after processing
		self.dates_cal_watch_agg = sum(self.dates_cal_watch_agg,[])
		self.cal_watch_agg = sum(self.cal_watch_agg,[])

		start_dates_hr = self.wakeup_hours
		end_dates_hr = self.fellasleep_hours
		self.hr_based_sleep = self.data_utils.hr_average_basedon_sleep(dates = dates_to_test, HR = hr_to_test, startdates = start_dates_hr, enddates = end_dates_hr )
		
		#Databased dates
		agreggated_hr_watch = self.database_api.get_scanwatch_intra_activity_data(user = self.id_user, start_date = self.start_date_timestamp, end_date = self.end_date_timestamp)
		dates_HR_db = []
		heart_rates_db = []
		for entry in agreggated_hr_watch :
			dates_HR_db.append(entry['date_heart_rate'])
			heart_rates_db.append(entry['heart_rate'])		
		

		#Intraactivity data from the watch (from sleep service + db)
		
		self.intra_activity_watch['dates_HR'] = self.dates_HR_watch_agg + dates_HR_db
		self.intra_activity_watch['Heart Rate'] = self.hr_watch_agg + heart_rates_db

			
		#print(dates_hr_watch)
		#print(hr_watch)


	
	def activity_data_watch(self):
		# This function returns the activity data + database values. Please refer
		# to the withings API documentation to see what type of data
		# you can get from this service.
		self.activity_data = {}

		#Data from the database API
		data = self.database_api.get_scanwatch_summary_data(user = self.id_user, start_date= self.start_date, end_date= self.end_date)
		data = [{key: value for key, value in entry.items() if key != 'id'} for entry in data['scanwatches_summary']]

		# Extracting dates and steps into separate arrays
		dates_db = [entry['date'] for entry in data]
		dates_db = [arrow.get(date, 'YYYY-MM-DD') for date in dates_db]
		steps_db = [entry['steps'] for entry in data]
		steps_db = np.array(steps_db, dtype=float)
		steps_db[steps_db == -2.0] = np.nan
		hr_db = [entry['average_heart_rate'] for entry in data]
		hr_db = np.array(hr_db, dtype=float)
		hr_db[hr_db == -2.0] = np.nan
		
		
		# Extracting data from Withings API - summary
		self.meas_activity  =  self.api.measure_get_activity(startdateymd = arrow.utcnow().shift(days= self.starting_day_current_week), enddateymd = arrow.utcnow().shift(days= self.ending_day_current_week))
		result = [{'date': activity.date, 'average_heart_rate': activity.hr_average, 'calories': activity.calories, 'steps': activity.steps, 'hr_min':activity.hr_min, 'hr_max':activity.hr_max} for activity in self.meas_activity.activities]
		self.date_activity = [entry['date'] for entry in result]
		self.summary_heart_rate = [entry['average_heart_rate'] for entry in result]
		self.summary_steps = [entry['steps'] for entry in result]
		self.summary_calories = [entry['calories'] for entry in result]
		self.summary_hr_min = [entry['hr_min'] for entry in result]
		self.summary_hr_max = [entry['hr_max'] for entry in result]
		
		self.final_hr = self.data_utils.backup_data(value2 = self.summary_heart_rate, value1 = self.hr_based_sleep)		

		#Filling with current data
		#self.database_api.upload_scanwatch_summary_data(user = self.uuid_db, watch_id = self.values_devices['scan_watch'], date = self.date_activity, hr_i = self.final_hr,
												  #cal_i = self.summary_calories, steps_i = self.summary_steps, hr_max_i = self.summary_hr_max, hr_min_i = self.summary_hr_min)
		
		#Agreggated Data (Withings + db)
		#Steps
		self.activity_data['date'] = self.date_activity + dates_db
		#self.activity_data['date'] = np.array([np.datetime64(date.datetime) for date in self.activity_data['date']])
		self.activity_data['steps'] = self.summary_steps + steps_db.tolist()
		# Heart Rate
		self.activity_data['heart rate'] = self.final_hr + hr_db.tolist()

	def intra_sleep(self):

		self.sleep_data_rr_w = []
		self.sleep_data_hr_w = []
		self.sleephf_snoring_w = []
		self.sleephf_sdnn_w = []
		self.sleephf_startdate_w = []
		self.sleephf_enddate_w = []
		self.sleephf_states_w =[]
		mean_rr = []
		mean_hr = []

		week_days = list(range(self.starting_day_current_week, self.ending_day_current_week))
		week_days.append(-1)

		for i in range (len(week_days)):
			all_rr_values = []
			all_values_hr = []
			count_hr = 0
			count_rr = 0

			self.get_sleep_1 = self.api.sleep_get(data_fields=GetSleepField,startdate=arrow.utcnow().shift(days= week_days[i]).replace(hour=13, minute=0, second=0), enddate=arrow.utcnow().shift(days = week_days[i]+1).replace(hour=13, minute=0, second=0),)

			try:
				#Respiration rate
				sleephf_data_rr = [x['rr'] for x in self.get_sleep_1['series']]
				all_rr_values = [value for data_dict in sleephf_data_rr for value in data_dict.values()]
				count_rr = len(all_rr_values)  # Get the count of values
				mean_rr_day= sum(all_rr_values) / count_rr if count_rr > 0 else None
				#Heart rate 
				sleephf_data_hr = [x['hr'] for x in self.get_sleep_1['series']]
				all_values_hr = [value for data_dict in sleephf_data_hr for value in data_dict.values()]
				count_hr = len(all_values_hr)  # Get the count of values
				mean_hr_day = sum(all_values_hr) / count_hr if count_hr > 0 else None
				#snoring
				hf_snoring = [x['snoring'] for x in self.get_sleep_1['series']]
				#sdnn_1
				hf_sdnn = [x['sdnn_1'] for x in self.get_sleep_1['series']]
				#start_date
				hf_startdate = [x['startdate'] for x in self.get_sleep_1['series']]
				#end_date
				hf_enddate = [x['enddate'] for x in self.get_sleep_1['series']]
				#state
				hf_state = [x['state'] for x in self.get_sleep_1['series']]

				#Arrays with all the values from each measurement
				self.sleep_data_rr_w.append(sleephf_data_rr)
				self.sleep_data_hr_w.append(sleephf_data_hr)
				self.sleephf_snoring_w.append(hf_snoring)
				self.sleephf_sdnn_w.append(hf_sdnn)
				self.sleephf_startdate_w.append(hf_startdate)
				self.sleephf_enddate_w.append(hf_enddate)
				self.sleephf_states_w.append(hf_state)
				mean_rr.append((mean_rr_day))
				mean_hr.append((mean_hr_day))

			except:
				mean_rr.append(float('nan'))
				mean_hr.append(float('nan'))
				print("Missing sleep data")

		# Data from the api
		data = self.database_api.get_sleep_intra_activity_data(user = self.id_user, start_date= self.start_date_timestamp, end_date= self.end_date_timestamp)
		
		dates_rr_db = [entry['date_respiration_rate'] for entry in data]
		rr_sleep_db = [entry['respiration_rate'] for entry in data]
		dates_hr_db = [entry['date_heart_rate'] for entry in data]
		hr_sleep_db = [entry['heart_rate'] for entry in data]

		# This data represent Respiration Rate 'rr' in the withings structure

		sleep_data_rr = sum(self.sleep_data_rr_w,[])
		self.dates_rr_w = [i for s in [d.keys() for d in sleep_data_rr] for i in s]
		self.dates_rr_w = [int(x) for x in self.dates_rr_w]
		self.dates_rr = dates_rr_db + self.dates_rr_w

		self.rr_sleephf_w = [i for s in [d.values() for d in sleep_data_rr] for i in s]
		self.rr_sleephf = rr_sleep_db + self.rr_sleephf_w


		# This data represent Heart Rate 'hr' in the withings structure

		sleep_data_hr = sum(self.sleep_data_hr_w,[])
		self.dates_hr_sleep_w = [i for s in [d.keys() for d in sleep_data_hr] for i in s]
		self.dates_hr_sleep_w = [int(x) for x in self.dates_hr_sleep_w]
		self.dates_hr_sleep = dates_hr_db + self.dates_hr_sleep_w

		self.hr_sleephf_w = [i for s in [d.values() for d in sleep_data_hr] for i in s]
		self.hr_sleephf = hr_sleep_db + self.hr_sleephf_w


		#This data respresent Snoring 'snoring' in the withings structute
		self.sleephf_snoring_w= sum(self.sleephf_snoring_w,[])
		self.dates_snoring_w = [i for s in [d.keys() for d in self.sleephf_snoring_w] for i in s]
		self.dates_snoring_w = [int(x) for x in self.dates_snoring_w]
		self.snoring_sleephf_w = [i for s in [d.values() for d in self.sleephf_snoring_w] for i in s]


		#This data respresent Heart rate variability 'sdnn_1' in the withings structute

		self.sleephf_sdnn_w = sum(self.sleephf_sdnn_w,[])
		self.dates_sdnn_w = [i for s in [d.keys() for d in self.sleephf_sdnn_w] for i in s]
		self.dates_sdnn_w = [int(x) for x in self.dates_sdnn_w]
		self.sdnn_1_sleephf_w = [i for s in [d.values() for d in self.sleephf_sdnn_w] for i in s]

		#Start dates
		self.sleephf_startdate_w = sum(self.sleephf_startdate_w ,[])
		self.sleephf_enddate_w = sum(self.sleephf_enddate_w,[])
		self.sleephf_states_w = sum(self.sleephf_states_w,[])


		# Backup funtion in case sleep summary service is not updating the average of hr and rr per night
		self.rr_mean_bu = self.data_utils.backup_data(value1 = mean_rr, value2 = self.current_rr)
		self.hr_mean_bu = self.data_utils.backup_data(value1 = mean_hr, value2 = self.current_heart_rate)
		
		#Summary values for the graph
		# Database API data to merge it with current values
		
		#Data from the database API
		data = self.database_api.get_sleep_summary_data(user = self.id_user, start_date = self.start_date, end_date= self.end_date)
		print(data)
	
		dates_hr_db = [entry['hr_date_af'] for entry in data]
		dates_rr_db = [entry['hr_date_rr'] for entry in data]
		hr_af = [entry['hr_af'] for entry in data]
		hr_rr = [entry['hr_rr'] for entry in data]

		print(hr_af)
		print(hr_rr)
		#print(hola)

		

		sleep = zip(dates_hr_db, hr_af, dates_rr_db, hr_rr)
		filtered_sleep = [(date_hr_db, af, date_rr_db, rr) for (date_hr_db, af, date_rr_db, rr) in sleep if date_hr_db is not None]
		dates_hr_db_filtered, hr_af_filtered, dates_rr_db_filtered, hr_rr_filtered = zip(*filtered_sleep) if filtered_sleep else ([], [], [], [])
		
		
		dates_hr_db_filtered = list(dates_hr_db_filtered)
		dates_hr_db_filtered= [np.datetime64(date) for date in dates_hr_db_filtered]
		hr_af_filtered = list(hr_af_filtered)
		dates_rr_db_filtered = list(dates_rr_db_filtered)
		dates_rr_db_filtered= [np.datetime64(date) for date in dates_rr_db_filtered]
		hr_rr_filtered = list(hr_rr_filtered)

		
		#Data for graph 
		self.dates_summ_hr_sleep = dates_hr_db_filtered + self.current_dates_ss
		self.summ_hr_sleep = hr_af_filtered +  self.hr_mean_bu
		#Data for graph 
		self.dates_summ_rr_sleep = dates_rr_db_filtered + self.current_dates_ss
		self.summ_rr_sleep = hr_rr_filtered +  self.rr_mean_bu

	def sleep(self):

		sleepbu_data = {} 
		self.sleeps_data = {}
		self.sleep_summary = self.api.sleep_get_summary(data_fields=GetSleepSummaryField, startdateymd=arrow.utcnow().shift(days = self.starting_day_current_week),enddateymd=arrow.utcnow().shift(days = self.ending_day_current_week), lastupdate = None)
		self.sleeps_data['date'] = [arrow.get(x.date) for x in self.sleep_summary.series]
		try:
			self.last_sleep = self.sleeps_data['date'][-1]
		except:
			self.last_sleep = None
			print('No sleep data available')
		
		self.sleeps_data['start_date'] = [arrow.get(x.startdate) for x in self.sleep_summary.series]
		self.sleeps_data['end_date'] = [arrow.get(x.enddate) for x in self.sleep_summary.series]
		self.sleeps_data['data'] = [x.data for x in self.sleep_summary.series]


	
		
		#Sleep service all the values for the
		
		self.sleeps_data['breathing disturbances'] = [x.breathing_disturbances_intensity for x in self.sleeps_data['data']]
		self.sleeps_data['deep sleep duration'] = [x.deepsleepduration for x in self.sleeps_data['data']]
		self.sleeps_data['duration to sleep'] = [x.durationtosleep for x in self.sleeps_data['data']]
		self.sleeps_data['duration to wakeup'] = [x.durationtowakeup for x in self.sleeps_data['data']]
		self.sleeps_data['hr average'] = [x.hr_average for x in self.sleeps_data['data']]
		self.sleeps_data['hr_min'] = [x.hr_min for x in self.sleeps_data['data']]
		self.sleeps_data['hr_max'] = [x.hr_max for x in self.sleeps_data['data']]
		self.sleeps_data['rr_min'] = [x.rr_min for x in self.sleeps_data['data']]
		self.sleeps_data['rr_max'] = [x.rr_max for x in self.sleeps_data['data']]
		self.sleeps_data['light sleep duration'] = [x.lightsleepduration for x in self.sleeps_data['data']]
		self.sleeps_data['rem sleep duration'] = [x.remsleepduration for x in self.sleeps_data['data']]
		self.sleeps_data['rr average'] = [x.rr_average for x in self.sleeps_data['data']]
		self.sleeps_data['sleep score'] = [x.sleep_score for x in self.sleeps_data['data']]
		self.sleeps_data['wake up count'] = [x.wakeupcount for x in self.sleeps_data['data']]
		self.sleeps_data['total sleep time'] = [x.total_sleep_time for x in self.sleeps_data['data']]
		self.sleeps_data['total timeinbed'] = [x.total_timeinbed for x in self.sleeps_data['data']]
		self.sleeps_data['waso'] = [x.waso for x in self.sleeps_data['data']]
		self.sleeps_data['wake up duration'] = [x.wakeupduration for x in self.sleeps_data['data']]
		self.sleeps_data['awake in bed'] =  np.subtract(self.sleeps_data['total timeinbed'],self.sleeps_data['total sleep time'])
		self.sleeps_data['apnea'] =  [x.apnea_hypopnea_index for x in self.sleeps_data['data']]
		self.sleeps_data['out of bed count'] = [x.out_of_bed_count for x in self.sleeps_data['data']]
		

		#Values  of total time in bed, awake in bed conversion to hours /3600 
		self.sleeps_data['total sleep time']=[x/3600 for x in self.sleeps_data['total sleep time']]
		self.sleeps_data['awake in bed']=[x/3600 for x in self.sleeps_data['awake in bed']]

		# Database API data to merge it with current values
		#Data from the database API
		data = self.database_api.get_sleep_summary_data(user = self.id_user, start_date= self.start_date, end_date= self.end_date)
		#Dates from data
		dates_db = [entry['date'] for entry in data]
		dates_db = [arrow.get(date) for date in dates_db]
		

		start_date_db = [entry['start_date'] for entry in data]
		start_date_db = [arrow.get(date_string) for date_string in start_date_db]

		end_date_db = [entry['end_date'] for entry in data]
		end_date_db = [arrow.get(date_string) for date_string in end_date_db]
	
		# Sleep time from data
		sleep_time_db = [entry['total_sleep_time'] for entry in data]
		#sleep_time_db = [math.nan if x == -2.0 else x for x in sleep_time_db]
		sleep_time_db  = [math.nan if x is None else x for x in sleep_time_db]
	
		# Awake bed 
		awake_bed_db = [entry['awake_in_bed'] for entry in data]
		#awake_bed_db= [math.nan if x == -2.0 else x for x in awake_bed_db]
		awake_bed_db  = [math.nan if x is None else x for x in awake_bed_db]

		#Out of bed
		out_of_bed_db = [entry['out_of_bed_count'] for entry in data]
		#out_of_bed_db = [math.nan if x == -2.0 else x for x in out_of_bed_db]
		out_of_bed_db   = [math.nan if x is None else x for x in out_of_bed_db ]

		#Sleep Heart Rate

		hr_sleep_db = [entry['average_heart_rate'] for entry in data]
		#hr_sleep_db = [math.nan if x == -2.0 else x for x in hr_sleep_db]
		hr_sleep_db   = [math.nan if x is None else x for x in hr_sleep_db]

		#Respiration Rate
		rr_sleep_db = [entry['average_rr'] for entry in data]
		#rr_sleep_db = [math.nan if x == -2.0 else x for x in rr_sleep_db]
		rr_sleep_db   = [math.nan if x is None else x for x in rr_sleep_db]

		#Apnea

		apnea_sleep_db = [entry['apnea']for entry in data]
		apnea_sleep_db = [math.nan if x is None else x for x in apnea_sleep_db]



		
		# Agreggated Data (Withings + db):
		self.dates_agg = self.sleeps_data['date'] + dates_db
		self.start_dates_agg = self.sleeps_data['start_date'] + start_date_db
		self.end_dates_agg = self.sleeps_data['end_date'] + end_date_db

		self.sleep_time_agg = self.sleeps_data['total sleep time'] + sleep_time_db
		self.awake_bed_agg = self.sleeps_data['awake in bed'] + awake_bed_db
		self.out_bed_agg = self.sleeps_data['out of bed count'] + out_of_bed_db
		self.hr_sleep_agg = self.sleeps_data['hr average'] + hr_sleep_db
		self.rr_sleep_agg = self.sleeps_data['rr average'] + rr_sleep_db
		self.apnea_sleep_agg = self.sleeps_data['apnea'] + apnea_sleep_db

		
		
		
		

		#Woke up and fell asleep times
		#This is to calculate the woke up and fell asleep times 
		sleep_summary_backup = self.api.sleep_get_summary(data_fields=GetSleepSummaryField, startdateymd=arrow.utcnow().shift(days =  self.ending_day_c - 7),enddateymd=arrow.utcnow().shift(days = self.ending_day_c + 1), lastupdate = None)
		sleepbu_data['date'] = [arrow.get(x.date) for x in sleep_summary_backup.series]
		sleepbu_data['start_date'] = [arrow.get(x.startdate) for x in sleep_summary_backup.series]
		sleepbu_data['end_date'] = [arrow.get(x.enddate) for x in sleep_summary_backup.series]
		sleepbu_data['data'] = [x.data for x in sleep_summary_backup.series]
		sleepbu_data['night_events'] = [x.night_events for x in sleepbu_data['data']]
		current_dates_ne, current_events, positions = self.data_utils.unique_values_sleep(sleepbu_data['date'], sleepbu_data['start_date'], sleepbu_data['end_date'], sleepbu_data['night_events'])
		self.daily_dates(startdate = sleepbu_data['start_date'], enddate = sleepbu_data['end_date'], positions = positions)		
		
		

		

		# Unique values Total Sleep Time - Graph and Table
		self.dates_agg_ss , self.current_sleep_time, _ = self.data_utils.unique_values_sleep(self.dates_agg , self.start_dates_agg, self.end_dates_agg, self.sleep_time_agg) 	
		
		# Unique values Awake in bed - Out of bed count (This values are only used in the graph)
		self.dates_agg_ss, self.current_awake_bed, _ = self.data_utils.unique_values_sleep(self.dates_agg , self.start_dates_agg, self.end_dates_agg, self.awake_bed_agg) 
		self.dates_agg_ss, self.current_out_bed, _ = self.data_utils.unique_values_sleep(self.dates_agg , self.start_dates_agg, self.end_dates_agg, self.out_bed_agg) 

		# Unique values for Sleep Apnoea - Graph and Table
		self.current_dates_ss, self.current_apnea, _ = self.data_utils.unique_values_sleep(self.dates_agg, self.start_dates_agg, self.end_dates_agg, self.apnea_sleep_agg) 
		#self.current_dates_ss, self.current_apnea = self.data_utils.data_cleaning(self.current_dates_ss, self.current_apnea)

		#Unique values calculation (The values for the variables are the ones taken between the biggest difference from start date and end date)

		self.current_dates_ss, self.current_heart_rate, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'] , self.sleeps_data['start_date'] , self.sleeps_data['end_date'] , self.sleeps_data['hr average']) 	
		self.current_dates_ss, self.current_rr, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'] , self.sleeps_data['start_date'] , self.sleeps_data['end_date'] , self.sleeps_data['rr average']) 
		
	def daily_dates(self, startdate = None, enddate = None, positions = None):

		#POSITIOOOONS
		print('POSIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIITIONS')
		print(positions)

		start_dates = [startdate[i] for i in positions]
		end_dates = [enddate[i] for i in positions]

		self.wakeup_hours = end_dates[:-1]
		self.fellasleep_hours = start_dates[1:]
		
		#print('Wakeup dates', end_dates)
		#print('sleep', start_dates)

	def daily_dates_prev(self, startdate = None, enddate = None, positions = None):
		start_dates = [startdate[i] for i in positions]
		end_dates = [enddate[i] for i in positions]

		self.wakeup_hours_prev = end_dates[:-1]
		self.fellasleep_hours_prev = start_dates[1:]

	#The following function is to generate the images for the PDF files
		
	def plot_creator(self):
		self.graph = graph.Graph_generator(start_date =self.initial_dates,
										   end_date = self.ending_dates,
										   report_type = self.report_type)
		self.graph.plot_bar(self.activity_data['date'],self.activity_data['steps'])
		self.graph.plot_scatter(x = self.intra_activity_watch['dates_HR'], y = self.intra_activity_watch['Heart Rate'], k = self.activity_data['date'], j = self.activity_data['heart rate'], name = "HR_ScanWatch")
		self.graph.plot_continous(self.dates_scale_agg,self.weight_agg, "Scale")
		self.graph.plot_stacked_bar(x = self.dates_agg_ss, y = self.current_sleep_time,
									z = self.current_awake_bed, o = self.current_out_bed)
		self.graph.plot_scatter(x = self.dates_rr, y = self.rr_sleephf , k = self.dates_summ_rr_sleep, j = self.summ_rr_sleep, name = "RR")
		self.graph.plot_scatter(x = self.dates_hr_sleep, y = self.hr_sleephf , k = self.dates_summ_hr_sleep,  j = self.summ_hr_sleep, name = "HR")
	
	#The following function is to fill the database with the values from the devices (modules called: db)
	def db_api_filling(self):
		self.database_api.upload_scale_data(user = self.uuid_db, date = self.scale_data_w['date'], scale_id = self.values_devices['scale'], weight = self.weight,
									  muscle_mass = self.muscle_mass, bone_mass = self.bone_mass, fat_mass =self.fat_mass)
		self.database_api.upload_intra_scanwatch_summary_data(user = self.uuid_db, watch_id = self.values_devices['scan_watch'], 
														date_hr_i = self.dates_HR_watch_agg, hr_i = self.hr_watch_agg, date_calories_i = self.dates_cal_watch_agg,
														cal_i = self.cal_watch_agg, date_steps_i= self.dates_step_watch_agg, steps_i = self.steps_watch_agg)
		self.database_api.upload_scanwatch_summary_data(user = self.uuid_db, watch_id = self.values_devices['scan_watch'], date = self.date_activity, hr_i = self.final_hr,
												  cal_i = self.summary_calories, steps_i = self.summary_steps, hr_max_i = self.summary_hr_max, hr_min_i = self.summary_hr_min)
		self.database_api.upload_sleep_summary_data(user = self.uuid_db, sleep_id = self.values_devices['sleep_mat'], date = self.sleeps_data['date'], bd = self.sleeps_data['breathing disturbances'], dsd = self.sleeps_data['deep sleep duration'], dts = self.sleeps_data['duration to sleep'],
                                   dtw = self.sleeps_data['duration to wakeup'], hr = self.sleeps_data['hr average'], lsd = self.sleeps_data['light sleep duration'], rsd = self.sleeps_data['rem sleep duration'], rr = self.sleeps_data['rr average'],
								   ss = self.sleeps_data['sleep score'], wc = self.sleeps_data['wake up count'], wd = self.sleeps_data['wake up duration'], tst = self.sleeps_data['total sleep time'], tib = self.sleeps_data['total timeinbed'], ab = self.sleeps_data['awake in bed'],
								   apn = self.sleeps_data['apnea'], obc = self.sleeps_data['out of bed count'], start_date = self.sleeps_data['start_date'], end_date = self.sleeps_data['end_date'], hr_date_ap = self.current_dates_ss, hr_ap = self.hr_mean_bu,
								   rr_date_ap = self.current_dates_ss, rr_ap = self.rr_mean_bu)
		self.database_api.upload_intra_sleep_summary_data(user = self.uuid_db, sleep_id = self.values_devices['sleep_mat'], start_date = self.sleephf_startdate_w, end_date = self.sleephf_enddate_w, ss = self.sleephf_states_w,
                                        date_hr = self.dates_hr_sleep_w, hr = self.hr_sleephf_w, date_rr = self.dates_rr_w, rr = self.rr_sleephf_w, date_s = self.dates_snoring_w, sn = self.snoring_sleephf_w, date_sddn = self.dates_sdnn_w,
										sdnn_1 = self.sdnn_1_sleephf_w)

	def db_cleaning(self):
		self.database.SM.cleaning_cvs_files(cvs_from ='Scan_summary')
		self.database.SM.cleaning_cvs_files(cvs_from ='Sleep_summary')
		self.database.SM.cleaning_cvs_files(cvs_from ='Scale')
		self.database.SM.cleaning_cvs_files(cvs_from ='Intra_watch')
		self.database.SM.cleaning_cvs_files(cvs_from ='Intra_sleep')

	# The following function is to fill the table inf the PDF		
	def table_filler(self):

		self.current_sleep_hr = self.data_utils.values_dates_intersection(dates = self.dates_summ_hr_sleep, start_date = arrow.utcnow().shift(days = self.starting_day_current_week) , end_date = arrow.utcnow().shift(days = self.ending_day_current_week), values = self.summ_hr_sleep)
		self.current_sleep_rr = self.data_utils.values_dates_intersection(dates = self.dates_summ_rr_sleep, start_date = arrow.utcnow().shift(days = self.starting_day_current_week) , end_date = arrow.utcnow().shift(days = self.ending_day_current_week), values = self.summ_rr_sleep)
		self.current_sleep_time_1 = self.data_utils.values_dates_intersection(dates = self.dates_agg_ss, start_date = arrow.utcnow().shift(days = self.starting_day_current_week) , end_date = arrow.utcnow().shift(days = self.ending_day_current_week), values = self.current_sleep_time)
		self.current_apnea_1 = self.data_utils.values_dates_intersection(dates = self.dates_agg_ss, start_date = arrow.utcnow().shift(days = self.starting_day_current_week) , end_date = arrow.utcnow().shift(days = self.ending_day_current_week), values = self.current_apnea)
		self.current_weight = self.data_utils.values_dates_intersection(dates = self.dates_scale_agg, start_date = arrow.utcnow().shift(days = self.starting_day_current_week).replace(hour=0, minute=0, second=0), end_date = arrow.utcnow().shift(days = self.ending_day_current_week + 1).replace(hour=0, minute=0, second=0), values = self.weight_agg)
		self.current_daily_hr = self.data_utils.values_dates_intersection(dates = self.activity_data['date'], start_date = arrow.utcnow().shift(days = self.starting_day_current_week) , end_date = arrow.utcnow().shift(days = self.ending_day_current_week), values = self.activity_data['heart rate'])
		self.current_steps = self.data_utils.values_dates_intersection(dates = self.activity_data['date'], start_date = arrow.utcnow().shift(days = self.starting_day_current_week) , end_date = arrow.utcnow().shift(days = self.ending_day_current_week), values = self.activity_data['steps'])

		#Sleep
		self.HR_Sleep_table = ([self.current_sleep_hr, self.summ_hr_sleep, []])
		self.RR_Sleep_table = ([self.current_sleep_rr, self.summ_rr_sleep, []])
		self.ST_Sleep_table = ([self.current_sleep_time_1, self.current_sleep_time,[]])
		self.AP_Sleep_table = ([self.current_apnea_1,self.current_apnea,[]])

		#Scale
		self.Weight_table = (self.current_weight,self.weight_agg,[])

		#ScanWatch
		self.HR_table = ([self.current_daily_hr,self.activity_data['heart rate'],[]]) 
		self.Steps_table = ([self.current_steps,self.activity_data['steps'],[]])

	def usage_levels(self):
		print('Here in usages')

		#Date selection according to the type of the report
		if self.report_type == 1:
			start_date = arrow.utcnow().shift(days = self.starting_day_c) 
			end_date = arrow.utcnow().shift(days = self.ending_day_c)
			start_date_scale = arrow.utcnow().shift(days = self.starting_day_p-8) 

			# Data from sensors for report type = 1
			sleep_u = self.hr_mean_bu
			watch_u = self.activity_data['steps']
			scale_u = self.weight

		if self.report_type == 0:
			start_date = arrow.utcnow().shift(days = self.starting_day_p) 
			end_date = arrow.utcnow().shift(days = self.ending_day_p)


			start_date_scale = arrow.utcnow().shift(days = self.starting_day_p-8) 

			#print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
			#print(start_date_scale)

			#Values from last week for scanwatch and sleepmat
			sleep_u = self.current_sleep_hr
			watch_u = self.current_daily_hr

			#print(watch_u)
			#print(self.final_hr)

			#Values for the last two weeks of scale to calculate the usage 
			scale_u = self.data_utils.values_dates_intersection(dates = self.monthly_scale_data['date'], start_date = start_date_scale, end_date = end_date, values = self.weight_m)
	

		# Usage
	
		usage = self.data_utils.usage_understanding(start_date = start_date, end_date = end_date,  start_date_scale = start_date_scale,  sleep_u = sleep_u, watch_u = watch_u, scale_u = scale_u)
		
		#Battery 
		self.battery_report = self.battery

		#Last date of usage

		try:
			watch_last_usage =  self.activity_data['date'][-1]
		except IndexError:
			watch_last_usage =  None

		try:
			scale_last_usage =  self.last_scale[0]
		except IndexError:
			scale_last_usage =  None
		
		try:
			sleep_last_usage =  self.last_sleep
		except IndexError:
			sleep_last_usage =  None

		

		self.last_day_use = {'Watch': watch_last_usage, 'Scale': scale_last_usage, 'Sleep': sleep_last_usage} 
		print(usage)
		print(self.last_day_use)
		print(self.battery)


		self.database.SM.load_usage( user_id = self.id_user, start_date = start_date, end_date = end_date, sleep_usage = usage['Sleep Mat'], sleep_battery = self.battery['Sleep Monitor'], sleep_lastday = self.last_day_use['Sleep'], watch_usage = usage['Watch'],
									 watch_battery = self.battery['Activity Tracker'], watch_lastday = self.last_day_use['Watch'], scale_usage = usage['Scale'], scale_battery = self.battery['Scale'], scale_lastday = self.last_day_use['Scale'])

	#The following functions will be used to get the users' raw data. Please keep in mind that you need to activate and deactivate
	#the device you want to acquiere the raw data from

	def activate_raw_data(self, data_type = None):

		#This function allows the user to activate the raw data acquisition, data_type: type of data that needs to be 
		#activated (1: accelerometer, 2: optical sensor)
		self.api.activate_raw_data(hash_deviceid = self.hash_deviceid, rawdata_type = 1, enddate = arrow.utcnow().shift(days = 2))


	def deactivate_raw_data(self, data_type = None):
		#This function allows the user to deactivate the raw data acquisition, data_type: type of data that needs to be 
		#activated (1: accelerometer, 2: optical sensor)
		self.api.deactivate_raw_data(hash_deviceid = self.hash_deviceid, rawdata_type = 1)
		


	def get_raw_data(self):

		#This function allows to get the data collected during the times used in the activate_raw_data function.
		get_raw = self.api.get_raw_data(hash_deviceid = self.hash_deviceid, rawdata_type = 1, startdate = arrow.utcnow().shift(days=-20), enddate = arrow.utcnow().shift(days=-1))
		return(get_raw)

	def save_credentials(self, credentials: CredentialsType) -> None:

		"""Save credentials to a file."""
		print("Saving credentials in:", self.CREDENTIALS_FILE)
		with open(self.CREDENTIALS_FILE, "wb") as file_handle:
			pickle.dump(credentials, file_handle)

	def load_credentials(self) -> CredentialsType:

		"""Load credentials from a file."""
		print("Using credentials saved in:", self.CREDENTIALS_FILE)
		with open(self.CREDENTIALS_FILE, "rb") as file_handle:
			return cast(CredentialsType, pickle.load(file_handle))

	def doc_generation(self):

		path = self.database.SM.get_path()
		print(path)
		self.table_filler()

		self.document_generation = pdf_gen.PDF_generation(day_hr = self.HR_table, 
					night_hr = self.HR_Sleep_table, 
					night_rr = self.RR_Sleep_table,
					steps = self.Steps_table, 
					sleep_duration = self.ST_Sleep_table, 
					sleep_apnoea = self.AP_Sleep_table,
					weight = self.Weight_table,
					c_date = self.initial_dates_table,
					e_date = self.ending_dates_table,
					path = path,
					id_nhs = self.id_user,
					report_type = self.report_type)

	def remove_images(self):

		files_in_folder = os.listdir(self.base_path)

		for file_name in files_in_folder:
			file_path = os.path.join(self.base_path, file_name)
			if os.path.isfile(file_path) and file_name.lower().endswith('.png'):
				os.remove(file_path)
				print(f"Removed: {file_name}")
			else:
				print(f"Skipped: {file_name}")


	@staticmethod
	def main(cls):
		
		M = cls(client_id = 'client id', 
						 costumer_secret = 'costumer secret',
						 callback_uri = 'url',
						 report_type = 1
				)
		
		M.get_user_credentials()
		M.devices_info()
		M.scale_data()
		M.sleep()
		M.sleep_daily()
		M.activity_data_watch()
		M.plot_creator()
		M.doc_generation()
		M.remove_images()
		M.usage_levels()
		#M.deactivate_raw_data()
		#M.activate_raw_data()
	
	

if __name__ == "__main__":
    Devices_OAuth2flow.main()


