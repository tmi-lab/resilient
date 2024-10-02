# This code allows to pass all the existing data (from csv files) to the db server in postgres

import pandas as pd
import os
import requests
import math
import numpy as np
from datetime import datetime, timezone
from dateutil import parser, relativedelta

#from database_backend.api.models import User

class DatabaseServer_csv(object):

    def __init__(self, path = None):

        self.users_path = path
    
    # POST THE EXISTING USERS TO THE DATABASE
    def import_users_from_csv(self):
        
        #User = models_api.User()
            
        if os.path.exists(self.users_path):
            # Open the CSV file in read mode
            with open(self.users_path, 'r', newline='') as csv_file:
                df = pd.read_csv(self.users_path, header = 0, delimiter=';')
                print(df)
            


        # Define values for the new columns
        
        role = 'study-participant'
        password_hash = 'NONEYET'

        custom_headers = ['username', 'role', 'password_hash', '']

        # Add new columns with constum headers
        df = pd.DataFrame(df, columns=['Id', 'Date of Registration'] + custom_headers)
        df[custom_headers[0]] = df['Id'].values
        self.id_available = df['Id'].values
        df[custom_headers[1]] = role
        df[custom_headers[2]] = password_hash

        columns_to_remove = ['Id', 'Date of Registration']
        df = df.drop(columns=columns_to_remove)

        data = df.to_dict(orient='records')

        

        for i in range (len(data)):
            # Make POST request to Django server
            url = 'http://127.0.0.1:8000/api/users/'
            response = requests.post(url, json=data[i])
            
            if response.status_code == 200:
                print('Data updated successfully')
            else:
                print('Failed to update data:', response.text)


    


        

    # GET ALL THE USERS

    def get_users(self):
        self.id_available = []
        url = 'http://127.0.0.1:8000/api/users'
        response = requests.get(url)
        # Checking the status code of the response
        if response.status_code == 200:
            # Successful response
            print('GET request successful')
            # Accessing the response data
            self.user_data = response.json()  # Assuming the response is JSON data
            #print(self.user_data)
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)
        
        self.user_data = {user['username']: user for user in self.user_data['users']}
        self.id_available =  list(self.user_data.keys())
        print(self.id_available)
        #print(self.id_username_dict)

    #Extract User data
    def extract_user_data(self,username):
        user = self.user_data.get(username)
        if user:
            return user['id'], user['scale_device'], user['scanwatch_device'], user['sleepmat_device'] 
        return None, None, None, None

    #UPLOAD DEVICES FOR EACH USER
            
    def upload_device_info(self):
        url= 'http://127.0.0.1:8000/api/devices/'
        current_users = {key: value for key, value in self.id_username_dict.items() if value in self.id_available }
        print(current_users)
        #print(HOla)
        for i in range(len(self.id_available)):
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/Devices.csv'
           
            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')
                    

                    for j in range(len(dict)):

                        user_key = [key for key, val in current_users.items() if val == self.id_available[i]]

                        print(self.id_available[i])    
                    
                        data ={
                            "user": user_key[0],
                            "device_hash": dict[j]['Hash_deviceid'],
                            "device_type": {'Activity Tracker': 'scan_watch', 'Sleep Monitor': 'sleep_mat','Scale':'scale'}.get(dict[j]['Device'], 'default_value'),
                            "mac_address": dict[j]['MAC_address'],
                            "is_active": True
                            }
                        #print(data)
                        response = requests.post(url, json=data)

    def get_device_info(self):
        
        self.devices_dict = {}

        for i in range(len(self.id_available)):
            url = 'http://127.0.0.1:8000/api/devices/' + '?username=' + str(self.id_available[i])
            response = requests.get(url)
            # Checking the status code of the response
            if response.status_code == 200:
                # Successful response
                #print('GET request successful')
                # Accessing the response data
                data = response.json()  # Assuming the response is JSON data
                print(data)
            else:
                # Unsuccessful response
                print('GET request failed:', response.status_code)
        
        #print(self.devices_dict)

    def upload_scale_summary_data(self):

        url = 'http://127.0.0.1:8000/api/scales/'

        for i in range(len(self.id_available)):
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/Scale.csv'
            id,scale_id,_,_= self.extract_user_data(self.id_available[i])

            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')

                    #print(dict)

                    if scale_id is not None:

                        for j in range(len(dict)):
                            date_s = dict[j]['date']
                            date_s = parser.parse(date_s)
                            date_s= date_s.isoformat()
                           

                            print(type(dict[j]['Muscle mass'])) 
                            # Convert 'nan' values to None
                            weight = None if math.isnan(float(dict[j]['Weight'])) else float(dict[j]['Weight']) 
                            muscle_mass = None if math.isnan(float(dict[j]['Muscle mass'])) else float(dict[j]['Muscle mass'])
                            bone_mass = None if math.isnan(float(dict[j]['Bone mass'])) else float(dict[j]['Bone mass'])
                            fat_mass = None if math.isnan(float(dict[j]['Fat mass Weight'])) else float(dict[j]['Fat mass Weight'])

                            print(muscle_mass)
                   
                            data ={
                                "device": scale_id,
                                "user": id, 
                                "date": date_s,
                                "weight": weight,
                                "muscle_mass": muscle_mass,
                                "bone_mass": bone_mass,
                                'fat_mass': fat_mass, 
                                }
                            

                            print(data)
                            response = requests.post(url, json=data)
    
    def upload_scanwatch_summary_data(self):

        url = 'http://127.0.0.1:8000/api/scanwatches/summary/'
        
        for i in range(len(self.id_available)):
            print(self.id_available)
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/ScanWatch_summary.csv'
            id,_,watch_id,_= self.extract_user_data(self.id_available[i])
            print(id)
            #print(scale_id)
            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')
                    #print(dict)
                    if watch_id is not None:

                        for j in range(len(dict)):
                            date_s = dict[j]['date'][:-6]
                            date_s = datetime.strptime(date_s, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

                            # Convert 'nan' values to None
                            average_heart_rate = None if math.isnan(float(dict[j]['HR_Average'])) else float(dict[j]['HR_Average']) 
                            calories = None if math.isnan(float(dict[j]['Calories'])) else float(dict[j]['Calories'])
                            steps = None if math.isnan(float(dict[j]['Steps'])) else float(dict[j]['Steps'])
                            hr_max = None if math.isnan(float(dict[j]['HR_max'])) else float(dict[j]['HR_max'])
                            hr_min = None if math.isnan(float(dict[j]['HR_min'])) else float(dict[j]['HR_min'])
                   
                            data ={
                                "device": watch_id,
                                "user": id,
                                "date": date_s,
                                "average_heart_rate": average_heart_rate,
                                "calories": calories,
                                "steps": steps,
                                "hr_max": hr_min,
                                "hr_min": hr_max,
                            }
                            
                            print(data)
                            print('*********************')
                            print(self.id_available[i])
                            response = requests.post(url, json=data)

    def get_report_id(self, username = None):

        self.devices_dict = {}

        for i in range(len(self.id_available)):
            url = 'http://127.0.0.1:8000/api/reports/?username=' + str(username) 
            response = requests.get(url)
            # Checking the status code of the response
            if response.status_code == 200:
                # Successful response
                #print('GET request successful')
                # Accessing the response data
                data = response.json()  # Assuming the response is JSON data
                #print(data)
            else:
                # Unsuccessful response
                print('GET request failed:', response.status_code)
        
        print(data)
        
        return(data)


    def upload_usage_data(self):
        #url = 'http://127.0.0.1:8000/api/usage/'
        #current_users = {key: value for key, value in self.id_username_dict.items() if value in self.id_available }
        #print(current_users)
        for i in range(len(self.id_available)):
            url = 'http://127.0.0.1:8000/api/usages/' 
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/Usage.csv'
            id,_,_,_= self.extract_user_data(self.id_available[i])
            reports = self.get_report_id(username = self.id_available[i])
            #print(hola)
            #print(scale_id)
            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')
         
                    for j in range(len(dict)):
                        print(str(dict[j]['Watch Last reading']))
                        print(type(dict[j]['Watch Last reading']))
                        watch = dict[j]['Watch Last reading']
                        watch = watch[:-6] if isinstance(watch, float) and not np.isnan(watch) else 'nan'
                        date_scanwatch = self.convert_to_iso_format(watch)
                        #date_scanwatch = datetime.strptime(date_scanwatch, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                        sleep = dict[j]['SleepMat Last reading']
                        sleep = sleep[:-6] if isinstance(sleep, float) and not np.isnan(sleep) else 'nan'
                        date_sleepmat = self.convert_to_iso_format(sleep)
                        #date_sleepmat = datetime.strptime(date_sleepmat, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                        scale = dict[j]['Scale Last reading']
                        scale = scale[:-6] if isinstance(scale, float) and not np.isnan(scale) else 'nan'
                        date_scale = self.convert_to_iso_format(scale)
                        #date_scale  = datetime.strptime(date_scale, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                        
                        data ={
                            "user": id,
                            "report": reports['reports'][0]['id'],
                            "scanwatch_usage_level": '-1' if str(dict[j]['Watch Usage']) == 'nan' else dict[j]['Watch Usage'],
                            "scanwatch_battery": '-1' if str(dict[j]['Watch Battery'] == 'nan') else dict[j]['Watch Battery'],
                            "scanwatch_last_date": date_scanwatch,
                            "sleepmat_usage_level": '-1' if str(dict[j]['SleepMat Usage'] == 'nan') else dict[j]['SleepMat Usage'],
                            "sleepmat_battery": '-1' if dict[j]['SleepMat Battery'] else dict[j]['SleepMat Battery'],
                            "sleepmat_last_date": date_sleepmat,
                            "scale_usage_level": '-1' if str(dict[j]['Scale Usage'] == 'nan') else dict[j]['Scale Usage'],
                            "scale_battery": '-1' if str(dict[j]['Scale Battery'] == 'nan') else dict[j]['Scale Battery'],
                            "scale_last_date": date_scale
                                            }
                        
                        print(data)
                        response = requests.post(url, json=data)




    def upload_intra_scanwatch_summary_data(self):

        url = 'http://127.0.0.1:8000/api/scanwatches/intra_activity/'
        for i in range(len(self.id_available)):
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/ScanWatch_intra_activity.csv'
            #watch_id = self.get_device_id(id_user = str(self.id_available[i]), devices_dict = self.devices_dict, device_type = 'scan_watch')
            id,_,watch_id,_= self.extract_user_data(self.id_available[i])
            #print(scale_id)
            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')
                    #print(dict)
                    if watch_id is not None:
                        for j in range(len(dict)):
                            heart_rate = None if math.isnan(float(dict[j]['Heart Rate'])) else float(dict[j]['Heart Rate']) 
                            date_heart_rate = None if math.isnan(float(dict[j]['date HR'])) else float(dict[j]['date HR']) 
                            steps = None if math.isnan(float(dict[j]['Steps'])) else float(dict[j]['Steps']) 
                            date_steps = None if math.isnan(float(dict[j]['date Steps'])) else float(dict[j]['date Steps']) 
                            calories = None if math.isnan(float(dict[j]['Calories'])) else float(dict[j]['Calories']) 
                            date_calories = None if math.isnan(float(dict[j]['date Calories'])) else float(dict[j]['date Calories']) 
                            data ={
                                "user":id,
                                "device": watch_id,
                                "heart_rate": heart_rate,
                                "date_heart_rate": date_heart_rate,
                                "steps": steps,
                                "date_steps": date_steps,
                                "calories": calories,
                                "date_calories": date_calories
                                }
                            
                            print(data)
                           
                            response = requests.post(url, json=data)
        
    
    def upload_sleep_summary_data(self):

        url = 'http://127.0.0.1:8000/api/sleepmats/summary/'
        for i in range(len(self.id_available)):
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/SleepMat_summary.csv'
            id,_,_,sleep_id= self.extract_user_data(self.id_available[i])
            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')
                    #print(df)
                    #print(dict)
                    if sleep_id is not None:

                        for j in range(len(dict)):
                            date_s = dict[j]['date'][:-6]
                            print(date_s)
                            print(type(date_s))
                            date_s = datetime.strptime(date_s, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')

                            start_date = dict[j]['start_date']
                            start_date = parser.parse(start_date)
                            start_date = start_date.isoformat()

                            end_date = dict[j]['end_date']
                            end_date = parser.parse(end_date)
                            end_date = end_date.isoformat()
                            #start_date = start_date.date()
                            #start_date = datetime.strptime(date_s, '%Y-%m-%d %H:%M:%S')

                            # Convert 'nan' values to None
                            breathing_disturbances = None if math.isnan(float(dict[j]['Breathing disturbances'])) else float(dict[j]['Breathing disturbances']) 
                            deep_sleep_duration = None if math.isnan(float(dict[j]['Deep sleep duration'])) else float(dict[j]['Deep sleep duration'])
                            duration_to_sleep = None if math.isnan(float(dict[j]['Duration to sleep'])) else float(dict[j]['Duration to sleep'])
                            duration_to_wakeup = None if math.isnan(float(dict[j]['Duration to wakeup'])) else float(dict[j]['Duration to wakeup'])
                            average_heart_rate = None if math.isnan(float(dict[j]['HR average'])) else float(dict[j]['HR average'])
                            light_sleep_duration = None if math.isnan(float(dict[j]['Light sleep duration'])) else float(dict[j]['Light sleep duration'])
                            rem_sleep_duration = None if math.isnan(float(dict[j]['Rem sleep duration'])) else float(dict[j]['Rem sleep duration'])
                            average_rr = None if math.isnan(float(dict[j]['RR average'])) else float(dict[j]['RR average'])
                            sleep_score = None if math.isnan(float(dict[j]['Sleep score'])) else float(dict[j]['Sleep score'])
                            wakeup_count = None if math.isnan(float(dict[j]['Wake up count'])) else float(dict[j]['Wake up count'])
                            wakeup_duration = None if math.isnan(float(dict[j]['Wake up duration'])) else float(dict[j]['Wake up duration'])
                            total_sleep_time = None if math.isnan(float(dict[j]['Total sleep time'])) else float(dict[j]['Total sleep time'])
                            total_time_in_bed = None if math.isnan(float(dict[j]['Total time in bed'])) else float(dict[j]['Total time in bed'])
                            awake_in_bed = None if math.isnan(float(dict[j]['Awake in bed'])) else float(dict[j]['Awake in bed'])
                            apnea = None if math.isnan(float(dict[j]['Apnea'])) else float(dict[j]['Apnea'])
                            out_of_bed_count = None if math.isnan(float(dict[j]['Out of bed count'])) else float(dict[j]['Out of bed count'])
                   
                            data ={
                                "device": sleep_id,
                                "user":id,
                                "date": date_s,
                                "breathing_disturbances" : breathing_disturbances,
                                "deep_sleep_duration" : deep_sleep_duration,
                                "duration_to_sleep" : duration_to_sleep,
                                "duration_to_wakeup" : duration_to_wakeup,
                                "average_heart_rate" : average_heart_rate,
                                "light_sleep_duration" : light_sleep_duration,
                                "rem_sleep_duration" : rem_sleep_duration,
                                "average_rr" : average_rr,
                                "sleep_score" : sleep_score,
                                "wakeup_count" : wakeup_count,
                                "wakeup_duration" : wakeup_duration,
                                "total_sleep_time": total_sleep_time,
                                "total_time_in_bed": total_time_in_bed,
                                "awake_in_bed":awake_in_bed,
                                "apnea": apnea,
                                "out_of_bed_count":out_of_bed_count,
                                "start_date":start_date,
                                "end_date":end_date
                                }
                            
                            #print(data)
                            response = requests.post(url, json=data)

    def upload_report_data(self):
        url = 'http://127.0.0.1:8000/api/reports/'
        for i in range(len(self.id_available)):
            id,_,_,_= self.extract_user_data(self.id_available[i])
            start_date = (datetime.now() - relativedelta.relativedelta(months=3)).strftime('%Y-%m-%d')
            end_date = (datetime.now()).strftime('%Y-%m-%d')
            data ={
                "user": id,
                "path": "path",
                "type" : "agreggated",
                "start_date": start_date,
                "end_date": end_date
                                }
            response = requests.post(url, json=data)
            




    def upload_intra_sleep_summary_data(self):

        
        url = 'http://127.0.0.1:8000/api/sleepmats/intraactivity/'
        for i in range(len(self.id_available)):
            path = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/General/'+ str(self.id_available[i]) + '/Sleepmat_intra_activity.csv'
            id,_,_,sleep_id= self.extract_user_data(self.id_available[i])
            #print(scale_id)
            if os.path.exists(path):
                # Open the CSV file in read mode
                with open(path, 'r', newline='') as csv_file:
                    df = pd.read_csv(path, header = 0, delimiter=',')
                    dict = df.to_dict(orient = 'records')
                    #print(df)
                    #print(dict)
                    if sleep_id is not None:

                        for j in range(len(dict)):
                            # Convert 'nan' values to None
                            start_date = None if math.isnan(float(dict[j]['startdate'])) else float(dict[j]['startdate']) 
                            end_date = None if math.isnan(float(dict[j]['enddate'])) else float(dict[j]['enddate']) 
                            sleep_state = None if math.isnan(float(dict[j]['Sleep state'])) else int(dict[j]['Sleep state']) 
                            date_heart_rate = None if math.isnan(float(dict[j]['Heart Rate date'])) else float(dict[j]['Heart Rate date'])
                            heart_rate = None if math.isnan(float(dict[j]['Heart Rate'])) else float(dict[j]['Heart Rate'])
                            date_respiration_rate = None if math.isnan(float(dict[j]['Respiration rate date'])) else float(dict[j]['Respiration rate date'])
                            respiration_rate = None if math.isnan(float(dict[j]['Respiration rate'])) else float(dict[j]['Respiration rate'])
                            date_snoring = None if math.isnan(float(dict[j]['Snoring date'])) else float(dict[j]['Snoring date'])
                            snoring = None  if math.isnan(float(dict[j]['Snoring'])) else float(dict[j]['Snoring'])
                            date_sdnn_1 = None  if math.isnan(float(dict[j]['sdnn_1 date'])) else float(dict[j]['sdnn_1 date'])
                            sdnn_1 = None  if math.isnan(float(dict[j]['sdnn_1'])) else float(dict[j]['sdnn_1'])
                            print(start_date)
                            print(type(start_date))
                   
                            data ={
                                "user": id, 
                                "device": sleep_id,
                                "start_date": start_date,
                                "end_date":end_date, 
                                "sleep_state": sleep_state, 
                                "date_heart_rate": date_heart_rate, 
                                "heart_rate": heart_rate,
                                "date_respiration_rate": date_respiration_rate,
                                "respiration_rate": respiration_rate,
                                "date_snoring": date_snoring,
                                "snoring" : snoring,
                                "date_sdnn_1" : date_sdnn_1,
                                "sdnn_1": sdnn_1
                                }
                            
                            print(data)
                            response = requests.post(url, json=data) 


    def organized_dict(self, original_dict):
        converted_dict = {}
        for device in original_dict['devices']:
            user = device['user']
            device_type = device['device_type']
            #print(device_type)
            device_id = device['id']
            if user not in converted_dict:
                converted_dict[user] = {}
            
            converted_dict[user][device_type] = device_id
                
                
        return(converted_dict)
    
    def get_device_id(self, id_user = None, devices_dict = None, device_type = None):
        
        # Ensure the user ID is a string
        if id_user in devices_dict:
            user_devices = devices_dict[id_user]
            if device_type in user_devices:
                return user_devices[device_type]
            else:
                return f"Device type '{device_type}' not found for user '{id_user}'."
        else:
            return f"User ID '{id_user}' not found."
    
    def convert_to_iso_format(self, date_string):
        # Handle both formats: '2024-03-30 00:00:00' and '2024-03-30T00:00:00'
        if date_string != 'nan':
            try:
                # Try parsing with the space separator
                parsed_datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')      
            except ValueError:
                # If parsing fails, try with the 'T' separator
                parsed_datetime = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
            
            parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S')
            return datetime.strptime(parsed_datetime, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        else:
            return('nan')
                
        

            

                        
                        
                    
                    
                    
        



    
   
path_user = '/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/db/Users.csv'
db_csv = DatabaseServer_csv(path = path_user)
#db_csv.import_users_from_csv()
db_csv.get_users()
#db_csv.upload_device_info()
db_csv.get_device_info()
#db_csv.upload_scale_summary_data()
#db_csv.upload_scanwatch_summary_data()
#db_csv.upload_sleep_summary_data()
#db_csv.upload_intra_sleep_summary_data()
#db_csv.upload_usage_data()
db_csv.upload_intra_scanwatch_summary_data()
#db_csv.upload_report_data()
#db_csv.get_report_id(username = 1)
    





    

    

                
    


    

    
            

   
    

            
  



            


        
      