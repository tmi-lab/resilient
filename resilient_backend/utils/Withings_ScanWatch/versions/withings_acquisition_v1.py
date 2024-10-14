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
					   running_type: None):
		#Running type
		self.running_type = running_type
		# Report type
		self.report_type = report_type
		
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

		# Creates the data utils object
		self.data_utils = data_utils.Data_Handler()
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

		if self.report_type == 0:
			self.dates_SPC_charts()

	def dates_SPC_charts(self):

		#Registration date from API
		try:
			registration_date = self.db_id['users'][0]['created_at']
			print('********registration**********')
		except:
			registration_date = datetime.now().strftime("%Y-%m-%d")

		print(registration_date)

		df = pd.read_csv(self.users_path , header = 0, delimiter=';')
		filtered_df = df[df['Id'] == self.id_user]
		
		#if not filtered_df.empty:
			#date_of_registration = filtered_df[' Date of Registration'].iloc[0]
			#print(f"Date of registration for ID {self.id_user}: {date_of_registration}")
		#else:
			#print(f"No records found for ID {self.id_user}")

		#calculate the number of days between the register day and the current date
		date_of_registration =  datetime.strptime(registration_date, '%Y-%m-%d')

		#Setting the initial date - considaring current day
		self.ending_day_c = self.data_utils.initial_day()
		
		
		# Calculate the difference in days
		days_difference = ((datetime.now()- timedelta(days=self.ending_day_c)) - date_of_registration).days
		#self.starting_day_c = -days_difference

		#print(self.starting_day)
		#print(hola)
		if days_difference > 90:
			self.starting_day_c = -(90 - self.ending_day_c)
		else:
			self.starting_day_c = - days_difference
		
		#self.ending_day_c = -360
		#self.starting_day_c = -430

		self.ending_day_p = self.data_utils.initial_day()
		self.starting_day_p = self.ending_day_p - 6


		# Dates
		self.initial_dates = arrow.utcnow().shift(days = self.starting_day_c)
		#print(self.initial_dates)
		self.initial_dates_rep = self.initial_dates.format('D-MMM-YYYY')
		#print('Initial_Dates from main', self.initial_dates)
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
	
	def activity_data_watch(self): 

		# This function returns the activity data. Please refer
		# to the withings API documentation to see what type of data
		# you can get from this service.

		self.activity_data = {}
		self.pre_activity_data = {}
		self.month_activity_data = {}

		self.meas_activity  =  self.api.measure_get_activity(startdateymd = arrow.utcnow().shift(days=self.starting_day_c), enddateymd = arrow.utcnow().shift(days= self.ending_day_c))
		self.prev_meas_activity  =  self.api.measure_get_activity(startdateymd = arrow.utcnow().shift(days=self.starting_day_p), enddateymd = arrow.utcnow().shift(days= self.ending_day_p))

		#Current Week
		self.activity_data['date'] = [arrow.get(x.date) for x in self.meas_activity.activities]
		self.activity_data['heart_rate'] = [x.hr_average for x in self.meas_activity.activities]
		self.activity_data['date'], self.activity_data['heart_rate'] =self.data_utils.data_cleaning(self.activity_data['date'],self.activity_data['heart_rate'])
		self.activity_data['calories'] = [x.totalcalories for x in self.meas_activity.activities]
		self.activity_data['date'], self.activity_data['calories'] = self.data_utils.data_cleaning(self.activity_data['date'],self.activity_data['calories'])
		self.activity_data['steps'] = [x.steps for x in self.meas_activity.activities]
		self.activity_data['date'], self.activity_data['steps'] = self.data_utils.data_cleaning(self.activity_data['date'],self.activity_data['steps'])
		self.activity_data['hr_min'] = [x.hr_min for x in self.meas_activity.activities]
		self.activity_data['date'], self.activity_data['hr_min'] = self.data_utils.data_cleaning(self.activity_data['date'],self.activity_data['hr_min'])
		self.activity_data['hr_max'] = [x.hr_max for x in self.meas_activity.activities]
		self.activity_data['date'], self.activity_data['hr_max'] = self.data_utils.data_cleaning(self.activity_data['date'],self.activity_data['hr_max'])

		self.intra_activitydata(type_time = "current")

		#Previous Week
		self.pre_activity_data['heart_rate'] = [x.hr_average for x in self.prev_meas_activity.activities]
		self.pre_activity_data['steps'] = [x.steps for x in self.prev_meas_activity.activities]

	def intra_activitydata_watch(self, type_time = None):

		watch_data = []
		self.HR_watch = []
		self.steps_watch = []
		self.calories_watch = []
		self.dates_hr = []
		dates = []
		self.dates_steps = []
		dates_s = []
		self.dates_calories = []
		dates_c = []
		HR = []
		mean_HR = []
		dates_to_test = {}
		hr_to_test = {}
		if type_time == "current":
			starting_day = self.starting_day_c 
			ending_day = self.ending_day_c
			#print('Endind date', ending_day)

		if type_time == "prev":
			starting_day = self.starting_day_p
			ending_day = self.ending_day_p
		
		week_days = list(range(starting_day, ending_day))

		try:
			week_days.append(week_days[-1]+1)
			
			total = abs(starting_day) - abs(ending_day)

			for i in range (len(week_days)):

				self.meas_intraactivity = self.api.measure_get_intraactivity(startdate= arrow.utcnow().shift(days= week_days[i]).replace(hour=0, minute=0, second=0), enddate=arrow.utcnow().shift(days = week_days[i]+1).replace(hour=0, minute=0, second=0))
				dates = [key for key, sub_dict in self.meas_intraactivity['series'].items() if 'heart_rate' in sub_dict]
				watch_data = [sub_dict['heart_rate'] for sub_dict in self.meas_intraactivity['series'].values() if 'heart_rate' in sub_dict]
				dates_s = [key for key, sub_dict in self.meas_intraactivity['series'].items() if 'steps' in sub_dict]
				step_watch_data = [sub_dict['steps'] for sub_dict in self.meas_intraactivity['series'].values() if 'steps' in sub_dict]
				dates_c = [key for key, sub_dict in self.meas_intraactivity['series'].items() if 'calories' in sub_dict]
				calories_watch_data = [sub_dict['calories'] for sub_dict in self.meas_intraactivity['series'].values() if 'calories' in sub_dict]
				
				dates, watch_data = self.data_utils.hr_filtering(dates, watch_data)

				dates_to_test[i] = dates
				hr_to_test[i] = watch_data
				self.dates_hr.append(dates)
				self.HR_watch.append(watch_data)
				self.dates_steps.append(dates_s)
				self.steps_watch.append(step_watch_data)
				self.dates_calories.append(dates_c)
				self.calories_watch.append(calories_watch_data)
				time.sleep(2.5)

			#self.small_test(dates_to_test)
			self.HR_watch = sum(self.HR_watch,[])
			self.steps_watch = sum(self.steps_watch,[])
			self.calories_watch = sum(self.calories_watch,[])
			#dates_db_a = sum(dates_db_a, [])
			self.dates_hr = sum(self.dates_hr,[])
			self.dates_hr_1 = [int(x) for x in self.dates_hr]
			self.dates_steps = sum(self.dates_steps,[])
			#dates_steps = [int(x) for x in dates_steps]
			self.dates_calories = sum(self.dates_calories,[])
			#dates_calories = [int(x) for x in dates_calories]

			if type_time == "current":
				start_dates_hr = self.wakeup_hours
				end_dates_hr = self.fellasleep_hours
				self.hr_based_sleep = self.data_utils.hr_average_basedon_sleep(dates = dates_to_test, HR = hr_to_test, startdates = start_dates_hr, enddates = end_dates_hr )
				self.final_hr = self.data_utils.backup_data(value2 = self.activity_data['heart_rate'], value1 = self.hr_based_sleep)

			if type_time == "prev":
				start_dates_hr = self.wakeup_hours_prev
				end_dates_hr = self.fellasleep_hours_prev

				if start_dates_hr == []:
					print('No data for the week')
					self.final_hr_prev = []
				else:
					self.hr_based_sleep_prev = self.data_utils.hr_average_basedon_sleep(dates = dates_to_test, HR = hr_to_test, startdates = start_dates_hr, enddates = end_dates_hr )
					self.final_hr_prev = self.data_utils.backup_data(value2 = self.pre_activity_data['heart_rate'], value1 = self.hr_based_sleep_prev)
					
				return(self.final_hr_prev)

		except IndexError:

			print('No dates for heart rate')
			self.dates_hr_1 = []
			self.HR_watch = []
			self.final_hr = []

	def scale_data(self):

		self.scale_data = {}
		self.monthly_scale_data = {}

		self.meas_current = self.api.measure_get_meas(startdate=arrow.utcnow().shift(days= self.starting_day_c).replace(hour=23, minute=59, second=59), enddate = arrow.utcnow().shift(days= self.ending_day_c).replace(hour=23, minute=59, second=59), lastupdate = None)
		self.meas_monthly = self.api.measure_get_meas(startdate = arrow.utcnow().shift(days= self.starting_day_c), enddate = arrow.utcnow().shift(days= self.ending_day_c).replace(hour=23, minute=59, second=59), lastupdate = None)
		
		#Current week values
		self.scale_data['date'] = [arrow.get(x.date) for x in self.meas_current.measuregrps]
		self.scale_data['measures'] = [x.measures for x in self.meas_current.measuregrps]
		print('SCALEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
		self.last_scale = self.scale_data['date']
		self.weight, self.muscle_mass, self.bone_mass, self.fat_mass, hydration = self.data_utils.scale_data_extractor(self.scale_data['measures'])

		#Cleaning data for the table
		self.scale_data['date'], self.weight = self.data_utils.data_cleaning(self.scale_data['date'],self.weight)
		#Monthly values
		self.monthly_scale_data['date'] = [arrow.get(x.date) for x in self.meas_monthly.measuregrps]

		#Graph x titles dates
		try:
			self.scale_starting_date = self.monthly_scale_data['date'][-1]
			self.scale_ending_date = self.monthly_scale_data['date'][0]
		except:
			self.scale_starting_date = None
			self.scale_ending_date = None


		self.monthly_scale_data['measures'] = [x.measures for x in self.meas_monthly.measuregrps]
	
		self.weight_m, muscle_mass_m, bone_mass_m, fat_mass_m, hydration_m = self.data_utils.scale_data_extractor(self.monthly_scale_data['measures'])
		self.monthly_scale_data['date'], self.weight_m = self.data_utils.data_cleaning(self.monthly_scale_data['date'], self.weight_m)
		
		#Cleaning data for the table
		
		self.monthly_scale_data['date_mm'], self.muscle_mass_m = self.data_utils.unique_values_scale(self.monthly_scale_data['date'], muscle_mass_m)
		self.monthly_scale_data['date_mm'], self.muscle_mass_m = self.data_utils.data_cleaning(self.monthly_scale_data['date'], muscle_mass_m)
		self.monthly_scale_data['date_bm'], self.bone_mass_m = self.data_utils.unique_values_scale(self.monthly_scale_data['date'], bone_mass_m)
		self.monthly_scale_data['date_bm'], self.bone_mass_m = self.data_utils.data_cleaning(self.monthly_scale_data['date'], bone_mass_m)
		self.monthly_scale_data['date_fm'], self.fat_mass_m = self.data_utils.unique_values_scale(self.monthly_scale_data['date'], fat_mass_m)
		self.monthly_scale_data['date_fm'], self.fat_mass_m = self.data_utils.data_cleaning(self.monthly_scale_data['date'], fat_mass_m)
		self.monthly_scale_data['date_h'], self.hydration_m = self.data_utils.unique_values_scale(self.monthly_scale_data['date'], hydration_m)
		self.monthly_scale_data['date_h'], self.hydration_m = self.data_utils.data_cleaning(self.monthly_scale_data['date'], hydration_m)
	
	def sleep(self):

		sleephf_data = {}

		self.sleeps_data = {}
		self.sleeps_data_1 = {}

		sleepbu_data = {}

		sleepbu_data_p = {}

		prev_sleeps_data = {}

		month_sleeps_data = {}

		self.get_sleep = self.api.sleep_get(data_fields=GetSleepField,startdate=arrow.utcnow().shift(days= self.starting_day_c+1), enddate=arrow.utcnow().shift(days= self.starting_day_c+2),)
		
		sleephf_data['start_date'] = [arrow.get(x['startdate']) for x in self.get_sleep['series']]
		sleephf_data['end_date'] = [arrow.get(x['enddate']) for x in self.get_sleep['series']]
		sleephf_data['state'] = [x['state'] for x in self.get_sleep['series']]

		self.sleep_summary = self.api.sleep_get_summary(data_fields=GetSleepSummaryField, startdateymd=arrow.utcnow().shift(days = self.starting_day_c),enddateymd=arrow.utcnow().shift(days = self.ending_day_c), lastupdate = None)
		self.prev_sleep_summary = self.api.sleep_get_summary(data_fields=GetSleepSummaryField, startdateymd=arrow.utcnow().shift(days = self.starting_day_p),enddateymd=arrow.utcnow().shift(days= self.ending_day_p), lastupdate = None)

		self.sleeps_data['date'] = [arrow.get(x.date) for x in self.sleep_summary.series]
		try:
			self.last_sleep = self.sleeps_data['date'][-1]

		except:
			self.last_sleep = None
			print('No sleep data available')
		self.sleeps_data['start_date'] = [arrow.get(x.startdate) for x in self.sleep_summary.series]
		self.sleeps_data['end_date'] = [arrow.get(x.enddate) for x in self.sleep_summary.series]
		self.sleeps_data['data'] = [x.data for x in self.sleep_summary.series]

		prev_sleeps_data['date'] = [arrow.get(x.date) for x in self.prev_sleep_summary.series]
		prev_sleeps_data['start_date'] = [arrow.get(x.startdate) for x in self.prev_sleep_summary.series]
		prev_sleeps_data['end_date'] = [arrow.get(x.enddate) for x in self.prev_sleep_summary.series]
		prev_sleeps_data['data'] = [x.data for x in self.prev_sleep_summary.series]

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
		self.sleeps_data['snoring'] = [x.snoring for x in self.sleeps_data['data']]
		self.sleeps_data['snoring_count'] = [x.snoringepisodecount for x in self.sleeps_data['data']]
		self.sleeps_data['wake up count'] = [x.wakeupcount for x in self.sleeps_data['data']]
		self.sleeps_data['total sleep time'] = [x.total_sleep_time for x in self.sleeps_data['data']]
		self.sleeps_data['total timeinbed'] = [x.total_timeinbed for x in self.sleeps_data['data']]
		self.sleeps_data['waso'] = [x.waso for x in self.sleeps_data['data']]
		self.sleeps_data['wake up duration'] = [x.wakeupduration for x in self.sleeps_data['data']]
		self.sleeps_data['awake in bed'] =  np.subtract(self.sleeps_data['total timeinbed'],self.sleeps_data['total sleep time'])
		self.sleeps_data['apnea'] =  [x.apnea_hypopnea_index for x in self.sleeps_data['data']]
		
		self.sleeps_data['out of bed count'] = [x.out_of_bed_count for x in self.sleeps_data['data']]

		self.sleeps_data['total sleep time']=[x/3600 for x in self.sleeps_data['total sleep time']]
		self.sleeps_data['awake in bed']=[x/3600 for x in self.sleeps_data['awake in bed']]
		
		self.sleeps_data_1['total sleep time'] = self.sleeps_data['total sleep time']
		self.sleeps_data_1['total timeinbed'] = self.sleeps_data['total timeinbed']
		self.sleeps_data_1['awake in bed'] = self.sleeps_data['awake in bed']
		self.sleeps_data_1['apnea'] = self.sleeps_data['apnea']
		self.sleeps_data_1['out of bed count'] = self.sleeps_data['out of bed count']

		# Previous week values
		prev_sleeps_data['hr average'] = [x.hr_average for x in prev_sleeps_data['data']]
		prev_sleeps_data['rr average'] = [x.rr_average for x in prev_sleeps_data['data']]
		prev_sleeps_data['total sleep time'] = [x.total_sleep_time for x in prev_sleeps_data['data']]
		prev_sleeps_data['apnea'] = [x.apnea_hypopnea_index for x in prev_sleeps_data['data']]


		#Unique values calculation (The values for the variables are the ones taken between the biggest difference from start date and end date)
		self.current_dates_ss, self.current_heart_rate, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'], self.sleeps_data['start_date'], self.sleeps_data['end_date'], self.sleeps_data['hr average']) 
		previous_dates_ss, self.prev_heart_rate, _ = self.data_utils.unique_values_sleep(prev_sleeps_data['date'], prev_sleeps_data['start_date'], prev_sleeps_data['end_date'], prev_sleeps_data['hr average'])
		self.current_dates_ss, self.current_rr, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'], self.sleeps_data['start_date'], self.sleeps_data['end_date'], self.sleeps_data['rr average']) 
		previous_dates_ss, self.prev_rr, _ = self.data_utils.unique_values_sleep(prev_sleeps_data['date'], prev_sleeps_data['start_date'], prev_sleeps_data['end_date'], prev_sleeps_data['rr average'])
		
		prev_sleeps_data['total sleep time']=[x/3600 for x in prev_sleeps_data['total sleep time']]

		#This is to calculate the woke up and fell asleep times 
		sleep_summary_backup = self.api.sleep_get_summary(data_fields=GetSleepSummaryField, startdateymd=arrow.utcnow().shift(days = self.starting_day_c),enddateymd=arrow.utcnow().shift(days = self.ending_day_c + 1), lastupdate = None)
		sleepbu_data['date'] = [arrow.get(x.date) for x in sleep_summary_backup.series]
		sleepbu_data['start_date'] = [arrow.get(x.startdate) for x in sleep_summary_backup.series]
		sleepbu_data['end_date'] = [arrow.get(x.enddate) for x in sleep_summary_backup.series]
		sleepbu_data['data'] = [x.data for x in sleep_summary_backup.series]
		sleepbu_data['night_events'] = [x.night_events for x in sleepbu_data['data']]
		current_dates_ne, current_events, positions = self.data_utils.unique_values_sleep(sleepbu_data['date'], sleepbu_data['start_date'], sleepbu_data['end_date'], sleepbu_data['night_events'])
		
		#This is to calculate the woke up and fell asleep times - PREVIOUS
		sleep_summary_backup_p = self.api.sleep_get_summary(data_fields=GetSleepSummaryField, startdateymd=arrow.utcnow().shift(days = self.starting_day_p),enddateymd=arrow.utcnow().shift(days = self.ending_day_p + 1), lastupdate = None)
		sleepbu_data_p['date'] = [arrow.get(x.date) for x in sleep_summary_backup_p.series]
		sleepbu_data_p['start_date'] = [arrow.get(x.startdate) for x in sleep_summary_backup_p.series]
		sleepbu_data_p['end_date'] = [arrow.get(x.enddate) for x in sleep_summary_backup_p.series]
		sleepbu_data_p['data'] = [x.data for x in sleep_summary_backup_p.series]
		sleepbu_data_p['night_events'] = [x.night_events for x in sleepbu_data_p['data']]
		
		prev_dates_ne, prev_events, positions_prev = self.data_utils.unique_values_sleep(sleepbu_data_p['date'], sleepbu_data_p['start_date'], sleepbu_data_p['end_date'], sleepbu_data_p['night_events'])

		self.daily_dates(startdate = sleepbu_data['start_date'], enddate = sleepbu_data['end_date'], positions = positions)		
		self.daily_dates_prev(startdate = sleepbu_data_p['start_date'], enddate = sleepbu_data_p['end_date'], positions = positions_prev)

		
		# Unique values Total Sleep Time - Graph and Table
		self.current_dates_ss, self.current_sleep_time, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'], self.sleeps_data['start_date'], self.sleeps_data['end_date'], self.sleeps_data['total sleep time']) 
		self.previous_dates_ss, self.prev_sleep_time, _ = self.data_utils.unique_values_sleep(prev_sleeps_data['date'], prev_sleeps_data['start_date'], prev_sleeps_data['end_date'], prev_sleeps_data['total sleep time'])
		
		# Unique values Awake in bed - Out of bed count (This values are only used in the graph)
		self.current_dates_ab, self.current_awake_bed, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'], self.sleeps_data['start_date'], self.sleeps_data['end_date'], self.sleeps_data['awake in bed']) 
		self.current_dates_ab, self.current_out_bed, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'], self.sleeps_data['start_date'], self.sleeps_data['end_date'], self.sleeps_data['out of bed count']) 

		# Unique values for Sleep Apnoea - Graph and Table
		self.current_dates_ss, self.current_apnea, _ = self.data_utils.unique_values_sleep(self.sleeps_data['date'], self.sleeps_data['start_date'], self.sleeps_data['end_date'], self.sleeps_data['apnea']) 
		self.current_dates_ss, self.current_apnea = self.data_utils.data_cleaning(self.current_dates_ss, self.current_apnea)

		self.previous_dates_ss, self.prev_apnea, _ = self.data_utils.unique_values_sleep(prev_sleeps_data['date'], prev_sleeps_data['start_date'], prev_sleeps_data['end_date'], prev_sleeps_data['apnea'])
		self.previous_dates_ss, self.prev_apnea = self.data_utils.data_cleaning(self.previous_dates_ss, self.prev_apnea)

	def daily_dates(self, startdate = None, enddate = None, positions = None):

		start_dates = [startdate[i] for i in positions]
		end_dates = [enddate[i] for i in positions]

		self.wakeup_hours = end_dates[:-1]
		self.fellasleep_hours = start_dates[1:]
		

	def daily_dates_prev(self, startdate = None, enddate = None, positions = None):
		start_dates = [startdate[i] for i in positions]
		end_dates = [enddate[i] for i in positions]

		self.wakeup_hours_prev = end_dates[:-1]
		self.fellasleep_hours_prev = start_dates[1:]

	def intra_sleep(self):

		sleephf_data = []
		sleephf_data_hr = []
		sleephf_data_snoring = []
		sleephf_data_sdnn = []
		sleephf_startdate = []
		sleephf_enddate = []
		sleephf_state = []
		data = []
		data_hr = []
		self.data_snoring = []
		self.data_sdnn = []
		self.data_startdate = []
		self.data_enddate = []
		self.data_states = []
		HR_sleep = []
		starting_day = self.starting_day_c
		ending_day = self.ending_day_c
		mean_hr = []
		mean_rr = []

		week_days = list(range(starting_day, ending_day))
		week_days.append(-1)
		total = abs(starting_day) - abs(ending_day)

		for i in range (len(week_days)):
			all_values = []
			all_values_hr = []
			count_hr = 0
			mean_1 = 0
			count = 0
			mean = 0

			self.get_sleep_1 = self.api.sleep_get(data_fields=GetSleepField,startdate=arrow.utcnow().shift(days= week_days[i]).replace(hour=13, minute=0, second=0), enddate=arrow.utcnow().shift(days = week_days[i]+1).replace(hour=13, minute=0, second=0),)
			try:
				#Respiration rate
				sleephf_data = [x['rr'] for x in self.get_sleep_1['series']]
				all_values = [value for data_dict in sleephf_data for value in data_dict.values()]
				all_dates = [value for data_dict in sleephf_data for value in data_dict.keys()]
				count = len(all_values)  # Get the count of values
				mean = sum(all_values) / count if count > 0 else None
				#Heart rate 
				sleephf_data_hr = [x['hr'] for x in self.get_sleep_1['series']]
				all_values_hr = [value for data_dict in sleephf_data_hr for value in data_dict.values()]
				count_hr = len(all_values_hr)  # Get the count of values
				mean_1 = sum(all_values_hr) / count if count > 0 else None

				#snoring
				sleephf_data_snoring = [x['snoring'] for x in self.get_sleep_1['series']]
				#sdnn_1
				sleephf_data_sdnn = [x['sdnn_1'] for x in self.get_sleep_1['series']]
				#start_date
				sleephf_startdate = [x['startdate'] for x in self.get_sleep_1['series']]
				#end_date
				sleephf_enddate = [x['enddate'] for x in self.get_sleep_1['series']]
				#state
				sleephf_state = [x['state'] for x in self.get_sleep_1['series']]
				
				#Arrays with all the values from each measurement
				data.append(sleephf_data)
				data_hr.append(sleephf_data_hr)
				self.data_snoring.append(sleephf_data_snoring)
				self.data_sdnn.append(sleephf_data_sdnn)
				self.data_startdate.append(sleephf_startdate)
				self.data_enddate.append(sleephf_enddate)
				self.data_states.append(sleephf_state)

				
				mean_rr.append(round(mean))
				mean_hr.append(round(mean_1))

			except:
				mean_rr.append(float('nan'))
				mean_hr.append(float('nan'))
				print("Missing sleep data")

		# This data represent Respiration Rate 'rr' in the withings structure
		data = sum(data,[])
		self.dates_rr = [i for s in [d.keys() for d in data] for i in s]
		self.dates_rr = [int(x) for x in self.dates_rr]
		self.RR = [i for s in [d.values() for d in data] for i in s]


		# This data represent Heart Rate 'hr' in the withings structure
		data_hr = sum(data_hr,[])
		self.dates_hr_sleep = [i for s in [d.keys() for d in data_hr] for i in s]
		self.dates_hr_sleep = [int(x) for x in self.dates_hr_sleep]
		self.HR = [i for s in [d.values() for d in data_hr] for i in s]

		#This data respresent Snoring 'snoring' in the withings structute
		self.data_snoring = sum(self.data_snoring,[])
		self.dates_snoring = [i for s in [d.keys() for d in self.data_snoring] for i in s]
		self.dates_snoring = [int(x) for x in self.dates_snoring]
		self.snoring = [i for s in [d.values() for d in self.data_snoring] for i in s]


		#This data respresent Heart rate variability 'sdnn_1' in the withings structute
		self.data_sdnn = sum(self.data_sdnn,[])
		self.dates_sdnn = [i for s in [d.keys() for d in self.data_sdnn] for i in s]
		self.dates_sdnn = [int(x) for x in self.dates_sdnn]
		self.sdnn_1 = [i for s in [d.values() for d in self.data_sdnn] for i in s]

		#Start dates
		self.data_startdate = sum(self.data_startdate,[])
		self.data_enddate = sum(self.data_enddate,[])
		self.data_states = sum(self.data_states,[])


		# Backup funtion in case sleep summary service is not updating the average of hr and rr per night
		self.rr_mean_bu = self.data_utils.backup_data(value1 = mean_rr, value2 = self.current_rr)
		self.hr_mean_bu = self.data_utils.backup_data(value1 = mean_hr, value2 = self.current_heart_rate)

	#The following function is to generate the images for the PDF files
	def plot_creator(self, type = None):


		#print(self.ending_dates)
		self.graph = graph.Graph_generator(start_date =self.initial_dates,
										   end_date = self.ending_dates,
										   report_type = self.report_type)


		self.graph.plot_bar(self.activity_data['date'],self.activity_data['steps'])
		self.graph.plot_continous(self.monthly_scale_data['date'],self.weight_m,"Scale")
		self.graph.plot_scatter(x = self.dates_hr_1, y = self.HR_watch, k = self.activity_data['date'], j = self.final_hr, name = "HR_ScanWatch")
		
		self.graph.plot_stacked_bar(x = self.current_dates_ss, y = self.current_sleep_time,
									z = self.current_awake_bed, o = self.current_out_bed)
		self.graph.plot_scatter(x = self.dates_rr, y = self.RR , k = self.current_dates_ss, j = self.rr_mean_bu, name = "RR")
		self.graph.plot_scatter(x = self.dates_hr_sleep, y = self.HR , k = self.current_dates_ss,  j = self.hr_mean_bu, name = "HR")

	#The following function is to fill the database with the values from the devices (modules called: db)
	def db_filling(self):
		self.database.SM.load_intra_activity(hr = self.HR_watch, time = self.dates_hr, time_steps = self.dates_steps, steps = self.steps_watch, time_calories = self.dates_calories, calories = self.calories_watch)
		self.database.SM.load_ScanWatch(hr = self.activity_data['heart_rate'], calories = self.activity_data['calories'], steps = self.activity_data['steps'], hr_max = self.activity_data['hr_max'],
								hr_min = self.activity_data['hr_min'],time = self.activity_data['date'] )
		self.database.SM.load_Scale(time = self.scale_data['date'], weight = self.weight, muscle_mass = self.muscle_mass, bone_mass = self.bone_mass, fat_mass = self.fat_mass)
		self.database.SM.load_SleepMat(time = self.sleeps_data['date'], bd = self.sleeps_data['breathing disturbances'], dsd = self.sleeps_data['deep sleep duration'], dts = self.sleeps_data['duration to sleep'],
								 dtw = self.sleeps_data['duration to wakeup'], hr = self.sleeps_data['hr average'], lsd = self.sleeps_data['light sleep duration'], rsd = self.sleeps_data['rem sleep duration'], 
								 rr = self.sleeps_data['rr average'], ss = self.sleeps_data['sleep score'], wpc = self.sleeps_data['wake up count'], wpd = self.sleeps_data['wake up duration'],
								 tst = self.sleeps_data_1['total sleep time'],ttb = self.sleeps_data_1['total timeinbed'], awb = self.sleeps_data_1['awake in bed'], ap = self.sleeps_data_1['apnea'], obc = self.sleeps_data_1['out of bed count'],
								 start_date = self.sleeps_data['start_date'], end_date = self.sleeps_data['end_date'], date_hr_ap = self.current_dates_ss, hr_ap = self.hr_mean_bu , date_rr_ap = self.current_dates_ss, rr_ap =  self.rr_mean_bu,
								 hr_min = self.sleeps_data['hr_min'], hr_max = self.sleeps_data['hr_max'], rr_min = self.sleeps_data['rr_min'] , rr_max = self.sleeps_data['rr_max'], snoring = self.sleeps_data['snoring'], snc = self.sleeps_data['snoring_count'] )
		
		self.database.SM.load_intra_sleep(start_date = self.data_startdate, end_date = self.data_enddate, ss = self.data_states, hr = self.HR, hr_date = self.dates_hr_sleep,
										rr = self.RR, rr_date = self.dates_rr, snoring = self.snoring, snoring_date = self.dates_snoring, sdnn_1 = self.sdnn_1, sdnn_1_date = self.dates_sdnn)
		self.database.SM.close_all_cvs_files()


	def db_cleaning(self):
		self.database.SM.cleaning_cvs_files(cvs_from ='Scan_summary')
		self.database.SM.cleaning_cvs_files(cvs_from ='Sleep_summary')
		self.database.SM.cleaning_cvs_files(cvs_from ='Scale')
		self.database.SM.cleaning_cvs_files(cvs_from ='Intra_watch')
		self.database.SM.cleaning_cvs_files(cvs_from ='Intra_sleep')



	# The following function is to fill the table inf the PDF
	def table_filler(self):

		if self.report_type == 1:
			#Sleep
			self.HR_Sleep_table = ([self.hr_mean_bu, self.prev_heart_rate, []])
			self.RR_Sleep_table = ([self.rr_mean_bu, self.prev_rr, []])
			self.ST_Sleep_table = ([self.current_sleep_time, self.prev_sleep_time, []])
			self.AP_Sleep_table = ([self.current_apnea, self.prev_apnea, []])

			#Scale
			self.Weight_table = (self.weight, [],[])

			#ScanWatch
			self.prev_hr = self.intra_activitydata(type_time = 'prev')
			self.HR_table = ([self.final_hr, self.prev_hr, []]) 
			self.Steps_table = ([self.activity_data['steps'], self.pre_activity_data['steps'], []])

		elif self.report_type == 0:

			# Extracting values from the values since registration (current week)
			self.current_sleep_hr = self.data_utils.values_dates_intersection(dates = self.current_dates_ss, start_date = arrow.utcnow().shift(days = self.starting_day_p) , end_date = arrow.utcnow().shift(days = self.ending_day_p), values = self.hr_mean_bu)
			self.current_sleep_rr = self.data_utils.values_dates_intersection(dates = self.current_dates_ss, start_date = arrow.utcnow().shift(days = self.starting_day_p) , end_date = arrow.utcnow().shift(days = self.ending_day_p), values = self.rr_mean_bu)
			self.current_sleep_time_1 = self.data_utils.values_dates_intersection(dates = self.current_dates_ss, start_date = arrow.utcnow().shift(days = self.starting_day_p) , end_date = arrow.utcnow().shift(days = self.ending_day_p), values = self.current_sleep_time)
			self.current_apnea_1 = self.data_utils.values_dates_intersection(dates = self.current_dates_ss, start_date = arrow.utcnow().shift(days = self.starting_day_p) , end_date = arrow.utcnow().shift(days = self.ending_day_p), values = self.current_apnea)
			self.current_weight = self.data_utils.values_dates_intersection(dates = self.monthly_scale_data['date'], start_date = arrow.utcnow().shift(days = self.starting_day_p).replace(hour=0, minute=0, second=0), end_date = arrow.utcnow().shift(days = self.ending_day_p + 1).replace(hour=0, minute=0, second=0), values = self.weight_m)
			print("FROM Developing section")
			print(self.current_weight)
			self.current_daily_hr = self.data_utils.values_dates_intersection(dates = self.activity_data['date'], start_date = arrow.utcnow().shift(days = self.starting_day_p) , end_date = arrow.utcnow().shift(days = self.ending_day_p), values = self.final_hr)
			self.current_steps = self.data_utils.values_dates_intersection(dates = self.activity_data['date'], start_date = arrow.utcnow().shift(days = self.starting_day_p) , end_date = arrow.utcnow().shift(days = self.ending_day_p), values = self.activity_data['steps'])

			#Sleep
			self.HR_Sleep_table = ([self.current_sleep_hr, self.hr_mean_bu, []])
			self.RR_Sleep_table = ([self.current_sleep_rr, self.rr_mean_bu, []])
			self.ST_Sleep_table = ([self.current_sleep_time_1, self.current_sleep_time,[]])
			self.AP_Sleep_table = ([self.current_apnea_1,self.current_apnea,[]])

			#Scale
			self.Weight_table = (self.current_weight,self.weight,[])

			#ScanWatch
			self.prev_hr = self.intra_activitydata(type_time = 'prev')
			self.HR_table = ([self.current_daily_hr,self.final_hr,[]]) 
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


