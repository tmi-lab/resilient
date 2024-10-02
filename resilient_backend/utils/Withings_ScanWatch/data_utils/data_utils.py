#Module description: This module is in charge of data preprocessing:
#Cleaning 'Nan' values, filtering the data and filling data when is missing with the intraday activity
from datetime import timedelta, datetime
from withings_api.common import MeasureType
import arrow
import numpy as np

class Data_Handler(object):
	def __init__(self):
		print('Data Utils module loaded')

	def initial_day(self):
		#Function to calculat the ending date (latest date for acquisition) for the request with the Withings API
		today = datetime.today() - timedelta(weeks=1)
		days_difference = today.isoweekday() % 7
		return (-days_difference)

	def data_cleaning(self, x, y):
		y = np.array(y, dtype=float)
		y[np.isnan(y)] = np.nan

		#This function is to clean the data from none or 0 values and convert x to timestamps
		#As withings has different ways to format the dates this function will set all dates to datetime variables
		y[y == None] = np.nan
		y[y == 0] = np.nan
		y[y == -1] = np.nan

		# Check if all elements in the array are of Arrow type

		all_are_arrows = all(isinstance(variable, arrow.Arrow) for variable in x)

		if all_are_arrows:

			x = [arrow_datetime.datetime for arrow_datetime in x]

		return(x,y)

	def hr_filtering(self, x, y):
		# Create a dictionary to aggregate y-values for each unique x-value
		data_dict = {}

		for i in range(len(x)):
			if x[i] not in data_dict:
				data_dict[x[i]] = []
			data_dict[x[i]].append(y[i])

		# Calculate the average y-values for each unique x-value
		timestamps = list(data_dict.keys())
		values = [np.mean(data_dict[x_val]) for x_val in timestamps]

		# Convert timestamps to integers
		timestamps = [int(ts_str) for ts_str in timestamps]

		#Deleting HR values at higher frequencies than 9min
		try:
			# Find the minimum timestamp
			min_timestamp = min(timestamps)

		except ValueError:
			# Handle the case when the timestamps list is empty
			min_timestamp = None

		# Create new arrays for filtered timestamps and values
		filtered_timestamps = []
		filtered_values = []

		if min_timestamp is not None:
			filtered_timestamps = [min_timestamp]
			filtered_values = [values[0]]

		for i in range(1, len(timestamps)):
			time_diff = (timestamps[i] - filtered_timestamps[-1])  # Calculate time difference in seconds
			if time_diff >= 540:  # 9 minutes in seconds
				filtered_timestamps.append(timestamps[i])
				filtered_values.append(values[i])

		return(filtered_timestamps, filtered_values)

	def unique_values_scale(self, dates, y):
		# Initialize variables to track daily sums and counts
		daily_sums = {}
		daily_counts = {}

		new_d = []
		new_weights = []

		# Iterate through the dates and values
		for date, weight in zip(dates, y):

			# Extract the date part without the time
			date_key = date.date()

			if date_key in daily_sums:
				# Add the weight to the daily sum
				if weight is not None and daily_sums.get(date_key) is not None:
					print(daily_sums[date_key])
					daily_sums[date_key] += weight
					daily_counts[date_key] += 1
				else:
					daily_counts[date_key] = float('nan')
			else:
				# Initialize the daily sum and count for a new date
				daily_sums[date_key] = weight
				daily_counts[date_key] = 1

			# Only add the date to the new list if it's the first occurrence of the day
			if daily_counts[date_key] == 1:
				new_d.append(date)
				try:
					new_weights.append(daily_sums[date_key] / daily_counts[date_key])
				except:
					new_weights.append(float('nan'))

		# If you have NaN values, you can replace them in the new_weights list
		new_weights = [np.nan if np.isnan(x) else round(x, 2) for x in new_weights]
		return(new_d, new_weights)

	def unique_values_sleep(self, dates, start_date, end_date, values):
		dates = [datetime.fromtimestamp(a.timestamp()) for a in dates]
		start_date = [arrow_datetime.datetime for arrow_datetime in start_date]
		end_date = [arrow_datetime.datetime for arrow_datetime in end_date]
		
		# Convert date strings to NumPy datetime64
		x = np.array(dates, dtype='datetime64')
		x1 = np.array(start_date, dtype='datetime64')
		x2 = np.array(end_date, dtype='datetime64')

		# Convert values to NumPy array
		y = np.array(values)
		# Calculate the difference between the startdate and enddate
		m = (x2 - x1)

		# Leave the values where the difference is the higher one
		max_m_per_date = {}
		positions = []
		for i in range(len(x)):
			date = x[i]
			if date not in max_m_per_date or m[i] > m[max_m_per_date[date]]:
				max_m_per_date[date] = i
		# Create new arrays with unique dates and corresponding maximum m values
		unique_dates = []
		unique_y = []
		for date, max_m in max_m_per_date.items():
			unique_dates.append(date)
			unique_y.append(values[max_m])

		positions = list(max_m_per_date.values())
		return(unique_dates, unique_y, positions)

	def hr_average_basedon_sleep(self, dates = None, HR = None, startdates = None, enddates = None):
		# Initialize a dictionary to store mean HR values for each key
		mean_hr_dict = {}
		try:
			if len(startdates) < len(dates):

				missing_days = len(dates) - len(startdates)

				for i in range(missing_days):

					wakeup_fill = startdates[0].shift(days = -(i+1), hours=0, minutes=0, seconds=0)
					sleep_fill = enddates[0].shift(days = -(i+1), hours=0, minutes=0, seconds=0)

					startdates.insert(missing_days-(i+1), wakeup_fill)
					enddates.insert(missing_days-(i+1), sleep_fill)

			# Iterate through keys in the 'dates' dictionary
			for key in dates:
				timestamps = [int(ts) for ts in dates[key]]
				hr_values = HR[key]
				#print(key)

				# Get the corresponding start and end dates for this key using the key index
				#startdate = startdates[key] #.replace(tzinfo='UTC')
				#enddate = enddates[key]#.replace(tzinfo='UTC')
				# Doing calculations between 6 am - 6 pm 
				
				startdate = startdates[key].replace(hour=6, minute=0, second=0)
				enddate = enddates[key].replace(hour=18, minute=0, second=0)

				# Convert startdate and enddate to timestamps
				startdate_ts = startdate.timestamp()
				enddate_ts = enddate.timestamp()

				# Initialize a list to store HR values within the date range for this key
				hr_values_within_range = []
				timestamps_within_range = []
				
				# Iterate through timestamps and HR values for this key
				for timestamp, hr in zip(timestamps, hr_values):
					
					if startdate_ts <= timestamp <= enddate_ts:
						hr_values_within_range.append(hr)
						timestamps_within_range.append(timestamp)

				# Calculate the mean of HR values within the date range for this key
				if hr_values_within_range:
					mean_hr_dict[key] = sum(hr_values_within_range) / len(hr_values_within_range)
					#mean_hr_dict[key] = average
				else:
					# If no HR values found within the specified date range, set the mean to None
					mean_hr_dict[key] = None
			
				rounded_values_list = [round(value)  if value is not None else None for value in mean_hr_dict.values()]
		except IndexError:
			
			print("Warning ! : Startdates list list is empty.")
			rounded_values_list = np.full(7, np.nan)

		return(rounded_values_list)

	def package_halfhour_calculation(self, timestamps,values):
		if not timestamps:
			return float('nan')

		# Convert timestamps to integers
		timestamps = [int(ts_str) for ts_str in timestamps]

		# Create a dictionary to store values in half-hour intervals
		half_hour_intervals = {}

		# Define the interval duration (30 minutes) in seconds
		interval_duration = 30 * 60

		# Initialize the first interval's start time
		#try:
		#print('Here')
		current_interval_start = timestamps[0]
		#print(current_interval_start)
		#except:
		#current_interval_start = None

		# Initialize variables to calculate the sum and count within each interval
		interval_sum = 0
		interval_count = 0

		if current_interval_start is not None:

			for timestamp, value in zip(timestamps, values):

				while timestamp >= current_interval_start + interval_duration:
					# Calculate the average for the current interval and store it
					if interval_count > 0:
						interval_average = interval_sum / interval_count
						half_hour_intervals[current_interval_start] = interval_average


					# Move to the next interval
					current_interval_start += interval_duration
					interval_sum = 0
					interval_count = 0

				interval_sum += value
				interval_count += 1


			# Calculate the average for the last interval

			if interval_count > 0:
				interval_average = interval_sum / interval_count
				half_hour_intervals[current_interval_start] = interval_average



			total_sum = sum(half_hour_intervals.values())
			num_values = len(half_hour_intervals)

			# Step 3: Calculate the average
			average = total_sum / num_values

		return(average)

	def halfhour_calculation(self, timestamps,values):
		if not timestamps:
			return float('nan')
		
		# Find the earliest timestamp
		earliest_timestamp = min(timestamps)

		# Define the 30-minute interval in seconds
		interval_seconds = 30 * 60  # 30 minutes * 60 seconds/minute

		# Initialize a list to store values at intervals
		values_at_intervals = []
		timestamps_at_intervals = []

		# Iterate through timestamps and extract values at 30-minute intervals
		current_timestamp = earliest_timestamp
		current_index = 0

		while current_index < len(timestamps):
			if timestamps[current_index] >= current_timestamp:
				values_at_intervals.append(values[current_index])
				timestamps_at_intervals.append(timestamps[current_index])
				current_timestamp += interval_seconds

			else:
				current_index += 1

		timestamps_at_intervals, values_at_intervals = self.hr_filtering(timestamps_at_intervals,values_at_intervals)

		#print('val at intervals', values_at_intervals)
		timestamps_repti = [arrow.get(ts) for ts in timestamps_at_intervals]
		#print('timestamps',timestamps_repti)

		if values_at_intervals:
			mean_hr = sum(values_at_intervals) / len(values_at_intervals)
			#print(mean_hr)
		else:
			print('Not available data')

		return(mean_hr)


	def scale_data_extractor(self, data):
		# Initialize dictionaries for each measurement type
		measurement_types = {
		"weight": [],
		"fat_mass": [],
		"muscle_mass": [],
		"hydration": [],
		"bone_mass": [],}

		for data_tuple in data:
			weight_value = None
			fat_mass_value = None
			muscle_mass_value = None
			hydration_value = None
			bone_mass_value = None

			for measure in data_tuple:
				if measure.type == MeasureType.WEIGHT:
					weight_value = measure.value * (10 ** measure.unit)
				elif measure.type == MeasureType.FAT_MASS_WEIGHT:
					fat_mass_value = measure.value * (10 ** measure.unit)
				elif measure.type == MeasureType.MUSCLE_MASS:
					muscle_mass_value = measure.value * (10 ** measure.unit)
				elif measure.type == MeasureType.HYDRATION:
					hydration_value = measure.value * (10 ** measure.unit)
				elif measure.type == MeasureType.BONE_MASS:
					bone_mass_value = measure.value * (10 ** measure.unit)

			# Append values to their respective lists or np.nan if missing
			measurement_types["weight"].append(weight_value)
			measurement_types["fat_mass"].append(fat_mass_value)
			measurement_types["muscle_mass"].append(muscle_mass_value)
			measurement_types["hydration"].append(hydration_value)
			measurement_types["bone_mass"].append(bone_mass_value)

		# List for measurements
		weight = np.array(measurement_types["weight"])
		fat_mass = np.array(measurement_types["fat_mass"])
		muscle_mass = np.array(measurement_types["muscle_mass"])
		hydration = np.array(measurement_types["hydration"])
		bone_mass = np.array(measurement_types["bone_mass"])
		return(weight, muscle_mass, bone_mass, fat_mass, hydration)

	def str_to_float(self, number, unit):
		number = str(number)
		number = number[:unit] + "." + number[unit:] 
		number = float(number)
		return(number)

	# The following function is called when there are higher granularity data but not averages
	def backup_data(self, value1 = None, value2 = None):
		value = [v1 if (v2 is None or np.isnan(v2) or v2 == 0) else v2 for v1, v2 in zip(value1, value2)]
		return(value)

	#The following function is to extract the data of the last week from all the values since registration
	def values_dates_intersection(self, dates = None, start_date = None, end_date = None, values = None):
		dates =  np.array(dates, dtype='datetime64')

		start_date = np.datetime64(start_date.format('YYYY-MM-DD'))
		end_date = np.datetime64(end_date.format('YYYY-MM-DD'))

		# Create a boolean mask for filtering
		mask = [(start_date <= date <= end_date) for date in dates]
		#print('Printing the mask for usage')
		#print(mask)

		# Apply the mask to get filtered values
		filtered_values = [value for value, m in zip(values, mask) if m]
		return(filtered_values)
	
	# The following function is to understand the weekly devices usage during the week
	def usage_understanding(self, start_date = None, end_date = None, start_date_scale = None, sleep_u = None, watch_u = None, scale_u = None):
		usage = {}

		day_diff = (end_date - start_date).days + 1
		day_diff_scale = (end_date - start_date_scale).days + 1

		print(sleep_u)
		print(watch_u)
		print(scale_u)
		print(day_diff)
		print(day_diff_scale)

		# Counting values None and NaN values
		total_sleep_nan = [value for value in sleep_u if value is None or np.isnan(value) or value == 0]
		total_watch_nan = [value for value in watch_u if value is None or np.isnan(value) or value == 0]
		total_scale_nan = [value for value in scale_u if value is None or np.isnan(value) or value == 0]

		# Total of existant values

		total_sleep = len(sleep_u) - len(total_sleep_nan)
		total_watch = len(watch_u) - len(total_watch_nan)
		total_scale = len(scale_u) - len(total_scale_nan)

		rule_sleep = day_diff - total_sleep
		rule_watch = day_diff - total_watch
		rule_scale = day_diff_scale - total_scale

		# Usage understanding for sleep
		if rule_sleep <= 1:
			usage['Sleep Mat'] = 'High'
		elif rule_sleep >1 and rule_sleep <=2:
			usage['Sleep Mat'] = 'Medium'
		else:
			usage['Sleep Mat'] = 'Low'

		if rule_watch <= 1:
			usage['Watch'] = 'High'
		elif rule_watch >1 and rule_watch <=2:
			usage['Watch'] = 'Medium'
		else:
			usage['Watch'] = 'Low'

		if rule_scale <= 12:
			usage['Scale'] = 'High'
		elif rule_scale >12 and rule_scale <= 13:
			usage['Scale'] = 'Medium'
		else:
			usage['Scale'] = 'Low'

		print(usage)
		return(usage)