from ...environment_config import EnvironmentConfig
from datetime import datetime, timezone
import arrow
import math
import numpy as np
import requests

class Database_API(object):
    def __init__(self):
        self.env = EnvironmentConfig()
        self.backend_url = self.env.get_config('BACKEND_URL')
    
    def register(self, user = None, role = None, password_hash = None, credential_path = None,
                scale_device_id = None, scanwatch_device_id = None, sleepmat_device_id = None):

        url = self.backend_url + '/api/users/'
        data = {
                "username": user,
                "role": role,
                "password_hash": password_hash,
                "withings_credentials_path": credential_path
                }
        print(data)

        response = requests.post(url, json = data)
        print('HIII')
        if response.status_code == 400:
            print('Not working')
           
    def register_update(self, user_uid = None, path = None):
        url = self.backend_url + '/api/user/' + user_uid +'/'
        data = {
             "withings_connected": True,
             "active": True,
             "withings_credentials_path": path
        }
        response = requests.patch(url,json=data)
        if response.status_code == 200:
             print("PATCH request successful")
        else:
             print(f"PATCH request failed with status code {response.status_code}")

    def get_users(self):
        url = self.backend_url + '/api/users'
        response = requests.get(url)
        
        # Checking the status code of the response
        if response.status_code == 200:
            # Successful response
            print('GET request successful')
            # Accessing the response data
            self.user_data = response.json()  # Assuming the response is JSON data
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)

        # Filter by participant and study participant
        self.filtered_data = [{entry['id']: entry['username']} for entry in self.user_data['users'] if entry['role'] in ['study-participant', 'study-partner-participant']]
        
        return(self.filtered_data)
    
    def get_unique_id(self, id_user = None):
        url = self.backend_url + '/api/users/?username='+ str(id_user)
        response = requests.get(url)
        
        # Checking the status code of the response
        if response.status_code == 200:
            # Successful response
            print('GET request successful')
            # Accessing the response data
            unique_id = response.json()  # Assuming the response is JSON data
            #print(data)
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)
        
        return(unique_id)
    
    #PATCH users table
    def update_devices_in_user(self, user_uid = None, scale_id = None, scanwatch_id = None, sleepmat_id = None):
        url = self.backend_url + '/api/user/' + user_uid +'/'
        print(scale_id)
        data = {
             "scale_device": scale_id,
             "scanwatch_device":scanwatch_id,
             "sleepmat_device": sleepmat_id
        }
        response = requests.patch(url,json=data)
        if response.status_code == 200:
             print("PATCH request successful")
        else:
             print(f"PATCH request failed with status code {response.status_code}")


    def upload_device_info(self, dict = None):
        url = self.backend_url + '/api/devices/'

        for j in range(len(dict)):
            
            data ={
                "device_hash": dict[j]['Hash_deviceid'],
                "device_type": {'Activity Tracker': 'scan_watch', 'Sleep Monitor': 'sleep_mat','Scale':'scale'}.get(dict[j]['Device'], 'default_value'),
                "mac_address": dict[j]['MAC_address'],
                "is_active": True
                }
            #print(data)
            response = requests.post(url, json=data)
            #print(response)

    def get_device_info(self, device_hash = None):
        url = self.backend_url + '/api/devices/' + '?device_hash=' + device_hash
        response = requests.get(url)
        self.devices_dict = {}
        # Checking the status code of the response
        if response.status_code == 200:
                print('GET request successful')
                # Accessing the response data
                data = response.json()  # Assuming the response is JSON data
                #print(data)
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)

        extracted_id = {device['device_type']: device['id'] for device in data['devices']}
        return(extracted_id)
    
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
    
    def get_scale_data(self, user = None, start_date = None, end_date = None):
        url = self.backend_url + '/api/scales/' + '?username=' + user
        response = requests.get(url)
        scale_dict = {}
        # Checking the status code of the response
        if response.status_code == 200:
            print('GET request successful')
            # Accessing the response data
            scale_dict = response.json()  # Assuming the response is JSON data
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)
        filtered_data = {'scales': [item for item in scale_dict['scales'] if start_date <= arrow.get(item['date']).datetime <= end_date]}
        return(filtered_data)

    def get_scanwatch_summary_data(self,user = None, start_date = None, end_date = None):
        url = self.backend_url + '/api/scanwatches/summary/' + '?username=' + user
        
        response = requests.get(url)
        scanwatch_dict = {}
        # Checking the status code of the response
        if response.status_code == 200:
            print('GET request successful')
            # Accessing the response data
            scanwatch_dict = response.json()  # Assuming the response is JSON data
            #print(scanwatch_dict)
                
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)

        # Filter data based on start_date and end_date
        filtered_data = {'scanwatches_summary': [item for item in scanwatch_dict['scanwatches_summary'] if start_date <= arrow.get(item['date']).datetime <= end_date]}
        
        return(filtered_data)
    
    def get_scanwatch_intra_activity_data(self, user = None, start_date = None, end_date = None):
        url = self.backend_url + '/api/scanwatches/intra_activity/' + '?username=' + user
        response = requests.get(url)
        scanwatch_intra_dict = {}
        # Checking the status code of the response
        if response.status_code == 200:
                print('GET request successful')
                # Accessing the response data
                scanwatch_intra_dict = response.json()  # Assuming the response is JSON data      
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)
        # Filter data based on start_date and end_date
        filtered_data = [{'date_heart_rate': item['date_heart_rate'], 
                          'heart_rate': item['heart_rate']} 
                          for item in scanwatch_intra_dict["scanwatches_intraactivity"] 
                          if item['date_heart_rate'] is not None and start_date <= item['date_heart_rate'] <= end_date]        
        return(filtered_data)
    
    def get_sleep_summary_data(self, user = None, start_date = None, end_date = None):
        url = self.backend_url + '/api/sleepmats/summary/' + '?username=' + user
        response = requests.get(url)
        sleep_summary_dict = {}
        # Checking the status code of the response
        if response.status_code == 200:
                print('GET request successful')
                # Accessing the response data
                sleep_summary_dict = response.json()  # Assuming the response is JSON data
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)
        # Filter data based on start_date and end_date
        filtered_data = [{'date': item['date'],
                          'breathing_disturbances': item['breathing_disturbances'],
                          'deep_sleep_duration': item['deep_sleep_duration'],
                          'duration_to_sleep': item['duration_to_sleep'],
                          'duration_to_wakeup': item['duration_to_wakeup'],
                          'average_heart_rate': item['average_heart_rate'],
                          'light_sleep_duration': item['light_sleep_duration'],
                          'rem_sleep_duration': item['rem_sleep_duration'],
                          'average_rr': item['average_rr'],
                          'sleep_score': item['sleep_score'],
                          'wakeup_count': item['wakeup_count'],
                          'wakeup_duration': item['wakeup_duration'],
                          'total_sleep_time': item['total_sleep_time'],
                          'total_time_in_bed': item['total_time_in_bed'],
                          'awake_in_bed': item['awake_in_bed'],
                          'apnea':item['apnea'],
                          'out_of_bed_count':item['out_of_bed_count'],
                          'start_date': item['start_date'],
                          'end_date': item['end_date'],
                          'hr_date_af': item['hr_date_af'],
                          'hr_date_rr': item['hr_date_rr'],
                          'hr_af': item['hr_af'],
                          'hr_rr': item['hr_rr']
                          } for item in sleep_summary_dict["sleepmats_summary"] if start_date <= arrow.get(item['date']).datetime <= end_date] 
        return(filtered_data)
    
    def get_sleep_intra_activity_data(self, user = None, start_date = None, end_date = None):
        url = self.backend_url + '/api/sleepmats/intraactivity/' + '?username=' + user
        response = requests.get(url)
        sleep_intra_day_dict = {}
        # Checking the status code of the response
        if response.status_code == 200:
                print('GET request successful')
                # Accessing the response data
                sleep_intra_day_dict = response.json()  # Assuming the response is JSON data
        else:
            # Unsuccessful response
            print('GET request failed:', response.status_code)
        # Filter data based on start_date and end_date
        filtered_data = [{'start_date': item['start_date'],
                          'end_date': item['end_date'],
                          'sleep_state': item['sleep_state'],
                          'date_heart_rate': item['date_heart_rate'],
                          'heart_rate': item['heart_rate'],
                          'date_respiration_rate': item['date_respiration_rate'],
                          'respiration_rate': item['respiration_rate'],
                          'date_snoring': item['date_snoring'],
                          'snoring': item['snoring'],
                          'date_sdnn_1': item['date_sdnn_1'],
                          'sdnn_1': item['sdnn_1'],
                          'device': item['device'],
                          } for item in sleep_intra_day_dict["sleepmats_intraactivity"] if start_date <= item['date_heart_rate']<= end_date]
        return(filtered_data)
    
    def upload_scanwatch_summary_data(self, user = None, watch_id= None, date = None, hr_i = None,
                                      cal_i = None, steps_i = None, hr_max_i = None, hr_min_i = None):
        url = self.backend_url + '/api/scanwatches/summary/'
        if watch_id is not None:
            for j in range(len(date)):
                date_s = date[j].isoformat()
                date_s = date_s[:-15]
                # Convert 'nan' values to None
                average_heart_rate = hr_i[j]
                calories = cal_i[j]
                steps = steps_i[j]
                hr_max = hr_max_i[j]
                hr_min = hr_min_i[j]
        
                data ={
                    "device": watch_id,
                    "user": user,
                    "date": date_s,
                    "average_heart_rate": None if math.isnan(float(average_heart_rate)) else float(average_heart_rate),
                    "calories": None if math.isnan(float(calories)) else float(calories),
                    "steps": None if math.isnan(float(steps)) else float(steps),
                    "hr_max": None if math.isnan(float(hr_max)) else float(hr_max),
                    "hr_min": None if math.isnan(float(hr_min)) else float(hr_min)
                }
                
                response = requests.post(url, json=data)

    def upload_intra_scanwatch_summary_data(self,  user = None, watch_id= None, date_hr_i = None, hr_i = None,
                                      date_calories_i = None,cal_i = None, date_steps_i= None, steps_i = None):

        url = self.backend_url + '/api/scanwatches/intra_activity/'
        
        #Convert to homogenous lists
        max_size = max(len(date_hr_i), len(date_steps_i), len(date_calories_i))
        if len(date_hr_i) < max_size:
            date_hr_i = np.append(date_hr_i , [np.nan] * (max_size - len(date_hr_i)))
            hr_i = np.append(hr_i, [np.nan] * (max_size - len(hr_i)))
        # Fill time_steps and steps with NaN until they reach max_size
        if len(date_steps_i) < max_size:
            date_steps_i = np.append(date_steps_i, [np.nan] * (max_size - len(date_steps_i)))
            steps_i = np.append(steps_i, [np.nan] * (max_size - len(steps_i)))
        # Fill time_calories and calories with NaN until they reach max_size
        if len(date_calories_i) < max_size:
            date_calories_i = np.append(date_calories_i, [np.nan] * (max_size - len(date_calories_i)))
            cal_i = np.append(cal_i, [np.nan] * (max_size - len(cal_i)))
        
        if watch_id is not None:
            for j in range(len(date_hr_i)):
                heart_rate = None if math.isnan(float(hr_i[j])) else float(hr_i[j]) 
                date_heart_rate = None if math.isnan(float(date_hr_i[j])) else float(date_hr_i[j]) 
                date_steps = None if math.isnan(float(date_steps_i[j])) else float(date_steps_i[j]) 
                steps = None if math.isnan(float(steps_i[j])) else float(steps_i[j]) 
                calories = None if math.isnan(float(cal_i[j])) else float(cal_i[j]) 
                date_calories = None if math.isnan(float(date_calories_i[j])) else float(date_calories_i[j]) 
                data ={
                    "user":user,
                    "device": watch_id,
                    "heart_rate": heart_rate,
                    "date_heart_rate": date_heart_rate,
                    "steps": steps,
                    "date_steps": date_steps,
                    "calories": calories,
                    "date_calories": date_calories
                    }
                
                #print(data)
                response = requests.post(url, json=data)
                
    def upload_sleep_summary_data(self, user = None, sleep_id = None, date = None, bd = None, dsd = None, dts = None,
                                   dtw = None, hr = None, lsd = None, rsd = None, rr = None, ss = None, wc = None,
                                   wd = None, tst = None, tib = None, ab = None, apn = None, obc = None, start_date = None,
                                   end_date = None, hr_date_ap = None, hr_ap = None, rr_date_ap = None, rr_ap = None):
        url = self.backend_url + '/api/sleepmats/summary/'
        max_size = max(len(hr_date_ap), len(rr_date_ap), len(date))
        if len(hr_date_ap) < max_size:
            hr_date_ap = np.append(hr_date_ap, [None] * (max_size - len(hr_date_ap)))
            rr_date_ap = np.append(rr_date_ap, [None] * (max_size - len(rr_date_ap)))
            hr_ap = np.append(hr_ap, [np.nan] * (max_size - len(hr_ap)))
            rr_ap = np.append(rr_ap, [np.nan] * (max_size - len(rr_ap)))
      
        if sleep_id is not None:

            for j in range(len(date)):
                date_s = date[j].isoformat()
                date_s = date_s[:-15]
                start_date_s = start_date[j].isoformat() if start_date[j] is not None else None
                end_date_s = end_date[j].isoformat() if end_date[j] is not None else None
                date_hr_sleep_ap = hr_date_ap[j].isoformat() if hr_date_ap[j] is not None else None
                date_rr_sleep_ap = rr_date_ap[j].isoformat() if rr_date_ap[j] is not None else None

                breathing_disturbances = bd[j] 
                deep_sleep_duration = dsd[j]
                duration_to_sleep = dts[j]
                duration_to_wakeup = dtw[j]
                average_heart_rate = hr[j]
                light_sleep_duration = lsd[j]
                rem_sleep_duration = rsd[j]
                average_rr = rr[j]
                sleep_score = ss[j]
                wakeup_count = wc[j]
                wakeup_duration = wd[j]
                total_sleep_time = tst[j]
                total_time_in_bed = tib[j]
                awake_in_bed = ab[j]
                apnea = apn[j]
                out_of_bed_count = obc[j]
                hr_af = hr_ap[j]
                rr_af = rr_ap[j]

                data ={
                    "device": sleep_id,
                    "user": user,
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
                    "start_date":start_date_s,
                    "end_date":end_date_s,
                    "hr_date_af": date_hr_sleep_ap,
                    "hr_af": None if np.isnan(hr_af) else hr_af, 
                    "hr_date_rr": date_rr_sleep_ap,
                    "hr_rr":None if np.isnan(rr_af) else rr_af
                    }
                response = requests.post(url, json=data)
                print(response)


    def upload_intra_sleep_summary_data(self, user = None, sleep_id = None, start_date = None, end_date = None, ss = None,
                                        date_hr = None, hr = None, date_rr = None, rr = None, date_s = None, sn = None, date_sddn = None, sdnn_1 = None):
        url = self.backend_url + '/api/sleepmats/intraactivity/'
        
        max_size = max(len(start_date), len(date_hr))
        
        if len(start_date) < max_size:
            start_date = np.append(start_date, [np.nan] * (max_size - len(start_date)))
            end_date = np.append(end_date, [np.nan] * (max_size - len(end_date)))
            ss = np.append(ss, [np.nan] * (max_size - len(ss)))
            
        if sleep_id is not None:
            for j in range(max_size):
                print(start_date[j])
                # Convert 'nan' values to None
                start_date_s = None if math.isnan(start_date[j]) else float(start_date[j]) 
                end_date_s = None if math.isnan(float(end_date[j])) else float(end_date[j]) 
                sleep_state_s = None if math.isnan(float(ss[j])) else int(ss[j]) 
                date_heart_rate = None if math.isnan(float(date_hr[j])) else float(date_hr[j])
                heart_rate = None if math.isnan(float(hr[j])) else float(hr[j])
                date_respiration_rate = None if math.isnan(float(date_rr[j])) else float(date_rr[j])
                respiration_rate = None if math.isnan(float(rr[j])) else float(rr[j])
                date_snoring = None if math.isnan(float(date_s[j])) else float(date_s[j])
                snoring = None  if math.isnan(float(sn[j])) else float(sn[j])
                date_sdnn_1 = None  if math.isnan(float(date_sddn[j])) else float(date_sddn[j])
                sdnn_1_1 = None  if math.isnan(float(sdnn_1[j])) else float(sdnn_1[j])
                data ={
                    "user": user, 
                    "device": sleep_id,
                    "start_date": start_date_s,
                    "end_date":end_date_s, 
                    "sleep_state": sleep_state_s, 
                    "date_heart_rate": date_heart_rate, 
                    "heart_rate": heart_rate,
                    "date_respiration_rate": date_respiration_rate,
                    "respiration_rate": respiration_rate,
                    "date_snoring": date_snoring,
                    "snoring" : snoring,
                    "date_sdnn_1" : date_sdnn_1,
                    "sdnn_1": sdnn_1_1
                    }
                
                response = requests.post(url, json=data)
    
    def upload_scale_data(self, user = None, scale_id = None, date = None, weight = None, muscle_mass= None,
                          bone_mass = None, fat_mass = None):
        url = self.backend_url + '/api/scales/'

        if scale_id is not None:
            for j in range(len(date)):
                date = date[j].isoformat()
                # Convert 'nan' values to None
                weight_s = None if math.isnan(weight[j]) else float(weight[j])  
                muscle_mass_s = None if math.isnan(muscle_mass[j]) else float(muscle_mass[j]) 
                bone_mass_s = None if math.isnan(bone_mass[j]) else float(bone_mass[j]) 
                fat_mass_s = None if math.isnan(fat_mass[j]) else float(fat_mass[j])

                print(muscle_mass)
        
                data ={
                    "device": scale_id,
                    "user": user, 
                    "date": date,
                    "weight": weight_s,
                    "muscle_mass": muscle_mass_s,
                    "bone_mass": bone_mass_s,
                    'fat_mass': fat_mass_s, 
                    }
                print(data)
                response = requests.post(url, json=data)
                print(response)
    