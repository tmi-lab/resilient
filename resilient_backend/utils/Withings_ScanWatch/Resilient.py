#This is the code to run all the participant reports
from ..environment_config import EnvironmentConfig
from datetime import datetime
from os import path 
from PyPDF2 import PdfMerger
import os 
import pandas as pd
import shutil
import utils.Withings_ScanWatch.db.database as database
import utils.Withings_ScanWatch.db.database_django as database_api
import utils.Withings_ScanWatch.Devices_OAuth2flow as reports
import utils.Withings_ScanWatch.resources.PDF_usage_generation as usage_pdf

class Resilient(object):
    def __init__(self):
        # Database calling
        self.database_api = database_api.Database_API()
        self.database = database.General(db_type = None)
        self.general = 'db/General'
        self.current_path = os.getcwd()
        self.load_withings_credentials()
        return
    
    def load_withings_credentials(self):
        self.env = EnvironmentConfig()
        self.__client_id = self.env.get_config('WITHINGS_CLIENT_ID')
        self.__costumer_secret = self.env.get_config('WITHINGS_COSTUMER_SECRET')
        self.__callback_url = self.env.get_config('WITHINGS_CALLBACK_URL')
        return
        
    def create_credentials(self, code = None, user_uid = None, username = None, role = None):
        #Patch the withings credentials in the application
        m = reports.Devices_OAuth2flow(client_id = self.__client_id, 
		                            costumer_secret = self.__costumer_secret,
		                            callback_uri = self.__callback_url,
		                            report_type = 0,
                                    id_participant = username,
                                    running_type = None)
        path = m.CREDENTIALS_FILE
        self.database_api.register_update(user_uid = user_uid, path = path)
        m.create_credentials(code = code)
        m.register_devices()
    
    def report_generation(self, report_type = None, username = None):
        users = self.current_users()
        self.gen_type = report_type
        if self.gen_type == 'all':
            self.id_available = users
            try:
                self.run_all_participants()
                return({'status': 'success', 'path': 'withings_reports'})
            except Exception as e:
                # You can log the error or print it if needed
                print(f"An error occurred: {e}")
                return({'status': 'failed', 'path': None})
        
        elif self.gen_type == 'one':
            self.id_available = [] 
            id_user = username 
            if id_user in users:
                try:
                    self.id_available.append(id_user)
                    self.run_all_participants()
                    return({'status': 'success', 'path':'one'})
                except Exception as e:
                    # You can log the error or print it if needed
                    print(f"An error occurred: {e}")
                    return({'status': 'failed', 'path': None})
            else:
                print("Participant not in the database")

    #This function uses the csv files 
    def read_users_path(self):
        #Current path for the Main class
        self.current_path = os.getcwd()
        #User's file path
        users = 'db/Users.csv'

        self.users_path = path.abspath(path.join(self.current_path, users))
        # Check if the file exists
        if os.path.exists(self.users_path):
            # Open the CSV file in read mode
            with open(self.users_path, 'r', newline='') as csv_file:
                df = pd.read_csv(self.users_path, header = 0, delimiter=';')
                if "Id" in df.columns:
                    self.id_available = df['Id'].values
                    print(self.id_available)

                else:
                    print('The id colum does not exists ')
        else:
            self.id_available = None
            print(f"The file '{self.users_path}' does not exist.")

    def current_users(self):
        data = self.database_api.get_users()
        usernames = [list(item.values())[0] for item in data]
        return(usernames)

    def run_all_participants(self):
        if self.id_available is not None:
            print(self.id_available)
            
            total_participants = len(self.id_available)
            for i in range (total_participants):

                id_report = self.id_available[i]
                reports_resilient = reports.Devices_OAuth2flow(client_id = self.__client_id, 
                                    costumer_secret = self.__costumer_secret,
                                    callback_uri = self.__callback_url,
                                    report_type = 0,
                                    id_participant = id_report,
                                    running_type = self.db_type)
                reports_resilient.get_user_credentials()
                reports_resilient.register_devices()
                reports_resilient.devices_info()
                #reports_resilient.scale_data()
                #reports_resilient.sleep()
                #reports_resilient.sleep_daily()
                reports_resilient.scale_data_v2()
                #reports_resilient.sleep_v2()
                #reports_resilient.intra_sleep_v2()
                #reports_resilient.intra_activitydata_watch_v2()
                #reports_resilient.activity_data_watch_v2()
                #reports_resilient.plot_creatorV2()
                reports_resilient.activity_data_watch()
                reports_resilient.plot_creator()
                reports_resilient.db_filling()
                reports_resilient.doc_generation()
                reports_resilient.usage_levels()
                reports_resilient.remove_images()
                reports_resilient.db_cleaning()
            
    def sort_files(self, files):
        return sorted(files, key=lambda x: x[3]) 

    def merge_pdf(self):
        reports_folder = '/Withings_reports'
        pdfs_path = self.current_path + reports_folder
        pdf_files = [f for f in os.listdir(pdfs_path) if f.endswith('.pdf')]
        
        # Organize PDFs by the first three characters of their name
        pdf_groups = {}
        for pdf_file in pdf_files:
            prefix = pdf_file[:3]
            if prefix not in pdf_groups:
                pdf_groups[prefix] = []
            pdf_groups[prefix].append(pdf_file)
            
        # Merge PDFs in each group
        for prefix, files in pdf_groups.items():
            if len(files) > 1:  # Only merge if there are at least two files to merge
                sorted_files = self.sort_files(files)
                merger = PdfMerger()
                for filename in sorted_files:
                    merger.append(os.path.join(pdfs_path, filename))
                
                # Define the merged PDF's name and save path
                merged_pdf_path = os.path.join(pdfs_path, f"{prefix}p_{prefix}s_report.pdf")
                merger.write(merged_pdf_path)
                merger.close()

    def delete_files(self, folder_path):
        if os.path.exists(folder_path):
            # List all files in the directory
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    # Check if it's a file and then delete it
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)               
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        else:
            print(f"The folder {folder_path} does not exist.")

    def create_folder_reports(self):
        folder_path =  'Withings_reports'
        self.general = 'db/General'
        #source_folder = path.abspath(path.join(self.current_path,
        users = self.current_users()
        self.id_available = users
        
        if os.path.exists(folder_path):
            self.delete_files(folder_path)
        else:
            try:
                os.mkdir(folder_path)
                print('Folder created correctly')
            except OSError as error:
                print('Failed to create folder in the path')

        for i in range (len(self.id_available)):
            #General database path for the users folders
            new_path = path.abspath(path.join(self.current_path, self.general, self.id_available[i]))
            # Latest directory on the file
            latest = self.latest_directory(directory_path = new_path)
            # General path + latest directory
            latest_user_directory = path.abspath(path.join(new_path, latest))
            # pdf files
            pdf_file = self.pdf_file_search(latest_user_directory)
            # General path + latest directory + pdf
            pdf_file_user = path.abspath(path.join(latest_user_directory, str(pdf_file[0])))
            self.copy_pdf(source_path = pdf_file_user, destination_path = folder_path)
            #source_path = os.path.join()
    
    def latest_directory(self, directory_path = None):
        directories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
        if not directories:
            latest_directory = None  # If there are no directories in the path, return None
    
        # Get the latest directory based on modification time
        latest_directory = max(directories, key=lambda d: os.path.getmtime(os.path.join(directory_path, d)))
        return(latest_directory)
    
    def pdf_file_search(self, directory_path = None):
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        # Filter out PDF files
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        return pdf_files
    
    def copy_pdf(self, source_path = None, destination_path = None):
        try:
            shutil.copy(source_path, destination_path)
            print("PDF file copied successfully from.")
        except FileNotFoundError:
            print("Source file not found.")
        except PermissionError:
            print("Permission denied.")
        except Exception as e:
            print(f"Error: {e}")
    
    def usage_reports(self):
        usage_users = []
        self.usage = 'Usage.csv'
        for i in range (len(self.id_available)):
            #General database path for the users folders
            new_path = path.abspath(path.join(self.current_path, self.general, self.id_available[i], self.usage))
            if os.path.exists(new_path):
                # Open the CSV file in read mode
                with open(new_path, 'r', newline='') as csv_file:
                    print(self.id_available[i])
                    df = pd.read_csv(new_path, header = 0, delimiter=',')
                    last_row_values = df.iloc[-1].tolist()
                    usage_users.append(last_row_values)
        # Transpose the dat
        usage_data = list(zip(*usage_users))
        
        # Convert each tuple to a list
        result_usage = [list(column) for column in usage_data]
        start_dates_str = [str(x) for x in result_usage[1]]
        end_dates_str = [str(x) for x in result_usage[2]]
        sleep_last = [str(x) for x in result_usage[6]]
        watch_last = [str(x) for x in result_usage[9]]
        scale_last = [str(x) for x in result_usage[12]]

        #print(sleep_last[-1])
        formatted_start_dates = [(' ' if date_str == 'nan' else datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%b %d')) for date_str in start_dates_str]
        formatted_end_dates = [(' ' if date_str == 'nan' else datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%b %d')) for date_str in end_dates_str]
        formatted_sleeplast_dates = [(' ' if date_str == 'nan'  else datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%b %d')) for date_str in sleep_last]
        formatted_watchlast_dates = [(' ' if date_str == 'nan' else datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%b %d')) for date_str in watch_last]
        formatted_scalelast_dates = [(' ' if date_str == 'nan' else datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%b %d')) for date_str in scale_last]

        usage_reports = usage_pdf.PDF_Usage(id_user = self.id_available,
                                            path = None,
                                            start_date = formatted_start_dates,
                                            end_date = formatted_end_dates,
                                            sleepmat_usage = result_usage[4],
                                            sleepmat_battery = result_usage[5],
                                            sleepmat_last = formatted_sleeplast_dates,
                                            watch_usage = result_usage[7],
                                            watch_battery = result_usage[8],
                                            watch_last = formatted_watchlast_dates,
                                            scale_usage = result_usage[10],
                                            scale_battery = result_usage[11],
                                            scale_last = formatted_scalelast_dates
                                            )
        
    @classmethod
    def main(cls):
        a = cls()
        a.report_generation()
        a.create_folder_reports()
        a.usage_reports()
        a.merge_pdf()

if __name__ == "__main__":
    Resilient.main()