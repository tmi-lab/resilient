from collections import defaultdict
from datetime import timedelta, datetime
from itertools import chain
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline
import arrow
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

class Graph_generator(object):
	def __init__(self,start_date : None,
					  end_date: None,
					  report_type: None):

		self.start_date = start_date
		self.end_date = end_date
		self.complete_dates = [self.start_date.shift(days=i) for i in range((self.end_date - self.start_date).days + 1)]
		self.complete_dates = [a.format('DD-MM') for a in self.complete_dates]
		self.font = {'family': 'Arial'}

		self.report_type = report_type

	def unique_values(self, dates, values):
		# Convert date strings to NumPy datetime64
		x = np.array(dates, dtype='datetime64')
		# Convert values to NumPy array
		y = np.array(values)

		# Get unique dates
		unique_dates = np.unique(x)

		# Calculate average value for each unique date
		averaged_values = []
		for date in unique_dates:
			mask = x == date
			avg_value = np.mean(y[mask])
			averaged_values.append(avg_value)


		# Convert back to NumPy arrays
		x_unique = np.array(unique_dates, dtype='datetime64')
		y_avg = np.array(averaged_values)

		return(x_unique, y_avg)


	def truncate_time(self,date):
		return date.replace(hour=0, minute=0, second=0, microsecond=0)

	def weekly_average(self,x, y):
		weekly_data = defaultdict(list)

		#x = [datetime.strptime(date.strftime('%Y-%m-%d'), '%Y-%m-%d') for date in x]

		for date, value in zip(x, y):

			if isinstance(date, np.datetime64):

				date = np.datetime64(date).astype(datetime)

			# Truncate time information
			truncated_date = self.truncate_time(date)

			# Calculate the start of the week for the truncated date
			week_start = truncated_date - timedelta(days=truncated_date.weekday())
			weekly_data[week_start].append(value)

		weekly_average = {
			week_start:  np.nanmean(values) if len(values) > 0 else np.nan for week_start, values in weekly_data.items()
			}

		# Extract keys and values from the weekly_average dictionary
		week_avg_dates = list(weekly_average.keys())
		week_avg_weights = list(weekly_average.values())
		
		return(week_avg_dates, week_avg_weights)

	def smooth_lines(self,x,y):
		# Convert datetime objects to matplotlib date numbers
		x = mdates.date2num(x)
		y = y

		if len(x) > 3:
			# Interpolate y values using the new x values
			try:
				# Create interpolation function
				interpolation_function = make_interp_spline(x, y)

				# Generate new x values for smooth curve
				new_x = np.linspace(min(x), max(x), num=50)
				smooth_y = interpolation_function(new_x)
				# Convert matplotlib date numbers back to datetime objects
				smooth_dates = mdates.num2date(new_x)

				return(smooth_dates,smooth_y)

			except:
				return(x,y)
		else:
			return(x,y)


	def plot_scatter(self, x, y, k, j, name):
		fig, ax = plt.subplots()

		index_0 = [index for index, value in enumerate(y) if value is None or value == 0]
		index_1 = [index for index, value in enumerate(j) if value is None or value == 0]

		y = [value for value in y if value is not None and value != 0]
		j = [value for value in j if value is not None and value != 0]

		# X is a character to represent the timestamp ( e.g., '16782892902')
		x = [datetime.fromtimestamp(timestamp) for timestamp in x] 
		x = [value for index, value in enumerate(x) if index not in index_0]
		
		# k, start_date and end_date are arroe types (e.g.,  <Arrow [2023-08-27T01:00:00+01:00]>)
		k = [value for index, value in enumerate(k) if index not in index_1]
		#print(name)
		#if name != 'RR':
			#k = np.array([np.datetime64(date.datetime) for date in k]) #ESTA EN LA V2 +D

		plt.clf()

		# Create a scatter plot
		sns.set_style("whitegrid",{ "grid.linewidth":0.5, "grid.color": ".8", "grid.linestyle": ":", "ytick.left": True})

		if y == [] and j == []:
			fig, ax = plt.subplots()
			# Step 3 (Optional): Add labels and titles to the plot
			ax.set_xlabel('Date', fontdict = self.font)
			ax.set_ylabel('value', fontdict = self.font)
		else:
			# Smooth lines
			date_avg, val_avg = self.weekly_average(k, j)
			#k_s,j_s = self.smooth_lines(k,j)
			k_s = k
			j_s = j

			if self.report_type == 1:
				if name == 'RR':
					#scatter.set_label('Respiration Rate')
					label_scatter = "Respiration Rate Values per Minute"
					label_lineplot = "Respiration Rate Average"
					plt.gca().set_title('Sleep Respiration Rate', fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
					plt.ylabel("Breaths per minute", fontsize = 11, fontdict = self.font)
				elif name == 'HR':
					label_scatter = "Sleep Heart Rate Values per Minute"
					label_lineplot = "Sleep Heart Rate Average"
					plt.gca().set_title('Sleep Heart Rate', fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
					plt.ylabel("Heart Rate (bpm)", fontsize = 11, fontdict = self.font)			
				elif name == 'HR_ScanWatch':
					label_scatter = "Daily Heart Rate Values per Minute"
					label_lineplot = "Daily Heart Rate Average"
					plt.gca().set_title('Daily Heart Rate', fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
					plt.ylabel("Heart Rate (bpm)", fontsize = 11, fontdict = self.font)
				
				sns.scatterplot( x= x, y = y, color = "cornflowerblue", label = label_scatter)
				sns.lineplot(x = k_s, y = j_s, color = "darkblue",label = label_lineplot)

				fig_size = fig.get_size_inches()

				for t, t1 in zip(k, j):
					if math.isnan(t1):
						plt.text(t, t1-(0.1* fig_size[1]), t1, ha='center', va='center', size = 11.2, color = "black")
						plt.gca().set_xticks([])
					else:
						#circle = patches.Ellipse((t, t1), width= 0.045 * fig_size[0], height= 0.3* fig_size[1], facecolor= "white")
						#circle.set_zorder(5)
						#plt.gca().add_patch(circle)
						plt.text(t, t1-(0.1* fig_size[1]), math.floor(t1), size = 11.5,  rotation = 45, fontdict = self.font, bbox=dict(boxstyle='circle', facecolor='white', edgecolor='white'))				
				try:
					plt.gca().set_xlim((self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)).shift(hours = -5), self.end_date)
				except TypeError as e:
					print("TypeError caught:", e)

				plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
				# Set the locator for x-axis labels
				plt.gca().xaxis.set_major_locator(mdates.DayLocator())	
				plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
				try:
					plt.ylim(min(y)-5, max(y)+5)
				except:
					print('Empty data')

			if self.report_type == 0:
				if name == 'RR':
					#scatter.set_label('Respiration Rate')
					label_scatter = "Respiration Rate Daily Average"
					label_lineplot = "Respiration Rate Weekly Average"
					plt.gca().set_title('Sleep Respiration Rate', fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
					plt.ylabel("Breaths per minute", fontsize = 11, fontdict = self.font)
					if j:
						try:
							plt.yticks(np.arange(min(y), max(y) + 0.5, 0.5))
							
						except ValueError as e:
							# Handle the ValueError
							print("Caught ValueError:", e)
							print("The sequence is empty. Provide a non-empty sequence.")
				elif name == 'HR':
					label_scatter = "Sleep Heart Rate Daily Average"
					label_lineplot = "Sleep Heart Rate Weekly Average"
					plt.gca().set_title('Sleep Heart Rate', fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
					plt.ylabel("Heart Rate (bpm)", fontsize = 11, fontdict = self.font)
					if j:
						print(j)
						j = np.array(j)
						j_ticks = j[~np.isnan(j)]
						plt.yticks(range(int(np.min(j_ticks)), int(np.max(j_ticks )) + 1, 5))					
				elif name == 'HR_ScanWatch':
					label_scatter = "Day Heart Rate Daily Average"
					label_lineplot = "Day Heart Rate Weekly Average"
					plt.gca().set_title('Day Heart Rate', fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
					plt.ylabel("Heart Rate (bpm)", fontsize = 11, fontdict = self.font)
					if j:
						print(j)
						j = np.array(j)
						j_ticks = j[~np.isnan(j)]
						try:
							plt.yticks(range(int(np.min(j_ticks)), int(np.max(j_ticks )) + 1, 5))
						except:
							print('None ticks')

				if len(j_s) < 2:
					scatter = sns.scatterplot( x= k_s, y = j_s, label = label_scatter, color = "darkblue")
				else:
					max_thresh = np.nanmean(j_s) + np.nanstd(j_s)
					min_thresh = np.nanmean(j_s) - np.nanstd(j_s)
					aver_thresh = np.nanmean(j_s)
					sns.lineplot(x = k, y = j, color = "cornflowerblue", linestyle =':', label = label_scatter)
					sns.lineplot(x = date_avg, y = val_avg, color = "darkblue",linestyle = '-', label = label_lineplot)
					# Threshold calculations
					plt.axhline(y=max_thresh, color='darkorange', linestyle='--', label='Upper limit', linewidth = 1)
					plt.text(self.end_date.shift(days= 1), max_thresh, f'{max_thresh:.2f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='darkorange'))
					plt.axhline(y=min_thresh, color='darkorange', linestyle='--', label=f'Lower limit', linewidth = 1)
					plt.text(self.end_date.shift(days= 1), min_thresh, f'{min_thresh:.2f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='darkorange'))
					plt.axhline(y=aver_thresh, color='mediumseagreen', linestyle='-', label= f'Average', linewidth = 2)
					plt.text(self.end_date.shift(days= 1), aver_thresh, f'{aver_thresh:.2f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='mediumseagreen'))
					plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
					plt.gca().xaxis.set_major_locator((MaxNLocator(nbins=7)))
					plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
					#plt.gca().set_xlim((self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)).shift(days = -7), self.end_date.shift(days = 2 ))

					for index in range(len(date_avg)):
						if not np.isnan(val_avg[index]):
							plt.text(date_avg[index], val_avg[index], math.floor(val_avg[index]), size = 11,  rotation = 45, fontdict = self.font, bbox=dict(boxstyle='circle', facecolor='lightblue', edgecolor='white'))

			plt.grid(axis = "x")
			plt.gca().spines['top'].set_visible(False)
			plt.gca().spines['right'].set_visible(False)

		plt.legend(loc= 'upper center', bbox_to_anchor = (0.5,1.09), ncol = 3 , frameon=False)
		# Remove the border around the legend box
		plt.savefig(name + 'Scatter.png', dpi = 500)

	def plot_min_max_av(self,x_values,y_average,y_min,y_max,device,type_d):
		x_values = [datetime.fromtimestamp(a.timestamp()) for a in x_values]

		# Calculate the range (difference between min and max)
		y_range = []

		y_average = [float('nan') if element is None else element for element in y_average]
		y_min = [float('nan') if element is None else element for element in y_min]
		y_max = [float('nan') if element is None else element for element in y_max]

		y_average = [float('nan') if x == 0 else x for x in y_average]
		y_min = [float('nan') if x == 0 else x for x in y_min]
		y_max = [float('nan') if x == 0 else x for x in y_max]

		x_values1, y_average = self.unique_values(x_values, y_average)
		x_values1, y_min = self.unique_values(x_values, y_min)
		x_values1, y_max = self.unique_values(x_values, y_max)

		plt.clf()

		for i, j, z in zip(y_average,y_min,y_max):

			y_range.append([i-j, z-i])

		y_range = np.transpose(y_range)

		# Create the figure and axis
		sns.set_style("whitegrid",{ "grid.linewidth":0.5, "grid.color": ".8", "grid.linestyle": ":", "ytick.left": True})

		# Plot the average line
		sns.scatterplot(x = x_values1, y = y_average, color='green', label='Heart Rate Average')

		# Plot the error bars (range)
		plt.errorbar(x_values1, y_average, yerr= y_range, fmt='o', color='green', ecolor='mediumseagreen', capsize=5)

		if device == "ScanWatch":
			plt.gca().set_title('ScanWatch: Heart Rate',fontsize = 14, loc = 'left',pad = 30, fontweight = 600)
		elif device == "SleepMat" and type_d == "HR":
			plt.gca().set_title('SleepMat: Heart Rate',fontsize = 14, loc = 'left',pad = 30, fontweight = 600, fontdict = self.font)
		elif device == "SleepMat" and type_d == "RR":
			plt.gca().set_title('SleepMat: Respiration Rate',fontsize = 14, loc = 'left',pad = 30, fontweight = 600, fontdict = self.font)

		# Add legend
		plt.legend(loc= 'upper center', bbox_to_anchor = (0.5,1.09), ncol =2)
		# Remove the border around the legend box
		plt.legend().set_frame_on(False)

		# Set the x-axis format as dates
		plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
		# Set the locator for x-axis labels
		plt.gca().xaxis.set_major_locator(mdates.DayLocator())

		# Add average value as text
		for x, y in zip(x_values1, y_average):
			if math.isnan(y):
				plt.text(x, y, y, ha='center', va='bottom', size = 11.5, fontdict = self.font)
			else:
				plt.text(x, y, math.floor(y), ha='center', va='bottom', size = 11.5, fontdict = self.font)

		# Show the plot
		#plt.savefig('my_plot.png')
		plt.gca().yaxis.set_label_coords(-0.1,0.5)
		plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
		plt.grid(axis = "x")
		# Remove the top and right spines
		plt.gca().spines['top'].set_visible(False)
		plt.gca().spines['right'].set_visible(False)
		plt.savefig(device+"_"+type_d, dpi = 500)
		plt.close()

	def plot_continous(self,date_weight, weight, date_muscle_mass, muscle_mass, date_bone_mass,
							bone_mass, date_fat_mass, fat_mass, date_hydration, hydration, st_date, ed_date, device):
		# Create a scatter plot
		sns.set_style("whitegrid",{ "grid.linewidth":0.5, "grid.color": ".8", "grid.linestyle": ":", "ytick.left": True})

		index_0 = [index for index, value in enumerate(weight) if value is None or value == 0 or math.isnan(value)]
		index_1 = [index for index, value in enumerate(muscle_mass) if value is None or value == 0 or math.isnan(value)]
		index_2 = [index for index, value in enumerate(bone_mass) if value is None or value == 0 or math.isnan(value)]
		index_3 = [index for index, value in enumerate(fat_mass) if value is None or value == 0 or math.isnan(value)]
		index_4 = [index for index, value in enumerate(hydration) if value is None or value == 0 or math.isnan(value)]

		#x = [datetime.fromtimestamp(a.timestamp()) for a in x]
		#print(x)
		weight = [value for value in weight if value is not None and value != 0 and not math.isnan(value)]
		muscle_mass = [value for value in muscle_mass if value is not None and value != 0 and not math.isnan(value)]
		bone_mass = [value for value in bone_mass if value is not None and value != 0 and not math.isnan(value)]
		fat_mass = [value for value in fat_mass if value is not None and value != 0 and not math.isnan(value)]
		hydration = [value for value in hydration if value is not None and value != 0 and not math.isnan(value)]
		
		date_weight = [value for index, value in enumerate(date_weight) if index not in index_0]
		date_muscle_mass = [value for index, value in enumerate(date_muscle_mass) if index not in index_1]
		date_bone_mass = [value for index, value in enumerate(date_bone_mass) if index not in index_2]
		date_fat_mass = [value for index, value in enumerate(date_fat_mass) if index not in index_3]
		date_hydration = [value for index, value in enumerate(date_hydration) if index not in index_4]

		weight_date_avg, weight_avg = self.weekly_average(date_weight, weight)
		mm_date_avg , mm_avg = self.weekly_average(date_muscle_mass, muscle_mass)
		bm_date_avg, bm_avg = self.weekly_average(date_bone_mass, bone_mass)
		fm_date_avg, fm_avg = self.weekly_average(date_fat_mass, fat_mass)
		hydration_date_avg, hydration_avg = self.weekly_average(date_hydration, hydration)

		# Smooth lines
		#x_s,y_s = self.smooth_lines(date_weight,weight)
		x_s = date_weight
		y_s = weight
		#y_s = [round(elem) for elem in y_s]
		x_s2,z_s = self.smooth_lines(date_muscle_mass,muscle_mass)
		x_s3,w_s = self.smooth_lines(date_bone_mass,bone_mass)
		x_s4,t_s = self.smooth_lines(date_fat_mass,fat_mass)
		x_s5,l_s = self.smooth_lines(date_hydration,hydration)

		max_thresh = np.mean(y_s) + np.std(y_s)
		min_thresh = np.mean(y_s) - np.std(y_s)
		aver_thresh = np.mean(y_s)
		
		plt.clf()

		if device == "Scale":	
			# Create a scatter plot
			sns.set_style("whitegrid",{ "grid.linewidth":0.5, "grid.color": ".8", "grid.linestyle": ":", "ytick.left": True})
			
			if len(date_weight) < 2:
				sns.scatterplot( x= date_weight, y = weight, label = "Weight readings", color = "darkblue")
			else:
				#print(date_weight)
				sns.lineplot(x = date_weight, y = weight, label = "Weight readings", color = "cornflowerblue", linestyle=':', linewidth = 2)
				sns.lineplot(x= weight_date_avg, y = weight_avg, color = "darkblue", linestyle='-', linewidth = 2, label = "Weight Weekly Average")
				# Threshold calculations
				#print(weight_date_avg)
				w_date = arrow.get(weight_date_avg[0])
				#print(w_date)
				plt.text(w_date.shift(days= 4), max_thresh, f'{max_thresh:.2f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='darkorange'))
				plt.axhline(y=max_thresh, color='darkorange', linestyle='--', label=f'Upper limit', linewidth = 1)
				plt.text(w_date.shift(days= 4), min_thresh, f'{min_thresh:.2f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='darkorange'))
				plt.axhline(y=min_thresh, color='darkorange', linestyle='--', label=f'Lower limit', linewidth = 1)
				plt.text(w_date.shift(days= 4), aver_thresh, f'{aver_thresh:.2f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='mediumseagreen'))
				plt.axhline(y=aver_thresh, color='mediumseagreen', linestyle='-', label= f'Average', linewidth = 2)

			#sns.lineplot(x = x_s2, y = z_s, label = "Muscle mass", linestyle='--',  color = "mediumseagreen", linewidth = 2)
			#sns.lineplot(x = x_s3, y = w_s, label = "Bone mass",linestyle='--',  color = "yellow", linewidth = 2)
			#sns.lineplot(x = x_s4, y = t_s, label = "Fat mass", linestyle='--', color = "mediumpurple", linewidth = 2)
			#sns.lineplot(x = x_s5, y = l_s, label = "Hydration (%)", linestyle='--', color = "cornflowerblue", linewidth = 2)
			# Set x-axis tick locations and labels
			# Make specific ticks transparent or not display them
			#plt.gca().set_xticks([])

			for index in range(len(weight_date_avg)):
				if not np.isnan(weight_avg[index]):
					plt.text(weight_date_avg[index], weight_avg[index], math.floor(weight_avg[index]), size = 11,  rotation = 45, fontdict = self.font, bbox=dict(boxstyle='circle', facecolor='lightblue', edgecolor='white'))

			#for index in range(len(mm_date_avg)):
				#plt.text(mm_date_avg[index], mm_avg[index], math.floor(mm_avg[index]), size = 11.5,  rotation = 45, fontdict = self.font)
				#plt.text(bm_date_avg[index], bm_avg[index], math.floor(bm_avg[index]), size = 11.5,  rotation = 45, fontdict = self.font)
				#plt.text(fm_date_avg[index], fm_avg[index], math.floor(fm_avg[index]), size = 11.5,  rotation = 45, fontdict = self.font)
				#plt.text(hydration_date_avg[index], hydration_avg[index], math.floor(hydration_avg[index]), size = 11.5,  rotation = 45, fontdict = self.font)
			#if len(z_s) == 0:
				#plt.ylim(min(y_s)-0.5, max(y_s)+0.5)

			plt.gca().set_title('Weight',fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
			plt.ylabel("kg", fontdict = self.font)
			#plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
			#plt.gca().xaxis.set_major_locator(mdates.DayLocator())
			plt.gca().xaxis.set_major_locator((MaxNLocator(nbins=7)))
			plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
			#plt.gca().set_xlim((self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)).shift(hours = -5), self.end_date.shift(days= 1))
			plt.legend(loc= 'upper center', bbox_to_anchor = (0.5,1.09), ncol = 4, fontsize = 8.5,frameon=False)
			# Setting y-axis ticks to integer values

			if not y_s:
				print('Scale values not available')
			else:
				plt.yticks(range(int(min(y_s))-1, int(max(y_s))+3))
			# Set the x-axis format as dates
			plt.gca().spines['top'].set_visible(False)
			plt.gca().spines['right'].set_visible(False)

			# Display the plot
			plt.grid(axis = "x")


		plt.savefig(device, dpi = 500)
		plt.close()

	def plot_bar(self,x,y):
		# Create a scatter plot
		sns.set_style("whitegrid",{ "grid.linewidth":0.5, "grid.color": ".8", "grid.linestyle": ":", "ytick.left": True})
		plt.clf()

		check = np.array(y)
		if (y == [] or (np.all(check == 0))):
			# Step 3 (Optional): Add labels and titles to the plot
			plt.ylabel('Hours', fontsize = 11, fontdict = self.font)
			plt.xlabel('Dates', fontsize = 11, fontdict = self.font)
			plt.grid(axis = "x")
			plt.gca().set_xticks([])
			plt.gca().set_title('Steps', fontsize = 14, loc = 'left',pad = 30, fontweight=600, fontdict = self.font)
		else:
			x = [datetime.fromtimestamp(a.timestamp()) for a in x]
			y = [0 if element is None else element for element in y]
			x, y = self.unique_values(x,y)

			if self.report_type == 1:
				# Create a bar plot
				plt.bar(x, y, color = 'lightgreen', label = "Steps", width = 0.4)
				plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
				plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
				# Set the locator for x-axis labels
				plt.gca().set_ylim(0, max(y[~np.isnan(y)])+250)
				plt.gca().xaxis.set_major_locator(mdates.DayLocator())
				plt.gca().set_xlim((self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)).shift(hours = -5), self.end_date)

			if self.report_type == 0:
				date_avg, val_avg = self.weekly_average(x, y)
				if len(y) < 2:
						sns.scatterplot( x= x, y = y, label = "Steps", color = "darkblue")
				else:
					max_thresh = np.nanmean(y) + np.nanstd(y)
					print(max_thresh)
					min_thresh = np.nanmean(y) - np.nanstd(y)
					print(min_thresh)
					aver_thresh = np.nanmean(y)
					print(aver_thresh)

					sns.lineplot(x = x, y = y, color = "cornflowerblue", linestyle = ':', label = "Steps")
					sns.lineplot(x = date_avg, y = val_avg, color = "darkblue", linestyle = '-')
					self.v_date = arrow.get(date_avg[-1])
					# Threshold calculations
					plt.axhline(y=max_thresh, color='darkorange', linestyle='--', label= 'Upper limit', linewidth = 1)
					plt.text(self.v_date.shift(days= 1), max_thresh, f'{max_thresh:.1f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='darkorange'))
					plt.axhline(y=min_thresh, color='darkorange', linestyle='--', label= 'Lower limit', linewidth = 1)
					plt.text(self.v_date.shift(days= 1), min_thresh, f'{min_thresh:.1f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='darkorange'))
					plt.axhline(y=aver_thresh, color='mediumseagreen', linestyle='-', label= 'Average', linewidth = 2)
					plt.text(self.v_date.shift(days= 1), aver_thresh, f'{aver_thresh:.1f}', fontdict = self.font, bbox=dict(boxstyle='square', facecolor='white', edgecolor='mediumseagreen'))

					plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
					plt.gca().xaxis.set_major_locator((MaxNLocator(nbins=7)))
					plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

					for index in range(len(date_avg)):
						if not np.isnan(val_avg[index]):
							plt.text(date_avg[index], val_avg[index], (math.floor(val_avg[index]) if not np.isnan(val_avg[index]) else np.nan), size = 11,  rotation = 45, fontdict = self.font, bbox=dict(boxstyle='circle', facecolor='lightblue', edgecolor='white'))

			plt.gca().set_title('Daily Step Count',fontsize = 14, loc = 'left',pad = 30, fontweight= 600, fontdict = self.font)
			plt.grid(axis = "x")
			plt.legend(loc= 'upper center', bbox_to_anchor = (0.5,1.09), ncol = 4, fontsize = 8.5,frameon=False)
			plt.gca().spines['top'].set_visible(False)
			plt.gca().spines['right'].set_visible(False)

		plt.savefig('Steps_curvedbar', dpi = 500)
		#plt.close()

	def plot_stacked_bar(self,x,y,z,o):
		# Create a scatter plot
		sns.set_style("whitegrid",{ "grid.linewidth":0.5, "grid.color": ".8", "grid.linestyle": ":", "ytick.left": True})

		# Create a figure and axes
		check = np.array(y)
		check1 = np.array(z)
		check2 = np.array(o)

		if (y == [] or (np.all(check == 0))) and (z == [] or (np.all(check1 == 0))) and (o == [] or (np.all(check2 == 0))):
			# Step 3 (Optional): Add labels and titles to the plot
			plt.ylabel('Hours', fontsize = 11, fontdict = self.font)
			plt.xlabel('Dates', fontsize = 11, fontdict = self.font)
			plt.grid(axis = "x")
			plt.gca().set_xticks([])
			plt.gca().set_title('Sleep Summary', fontsize = 14, loc = 'left',pad = 30, fontweight=600, fontdict = self.font)
		else:
			x1 = x
			x_u = x1
			o_u = o
			#x_u, l_u = self.unique_values(x,l)
			x_soft, o_soft= self.smooth_lines(x_u,o_u)
			x_soft_1, o_soft_1= self.smooth_lines(x_u,y)
			#x_soft, l_soft = self.smooth_lines(x_u,l_u)

			plt.clf()
			plt.bar(x1, y, label='Hours Asleep', color = "cornflowerblue")
			plt.bar(x1, z, label='Hours Awake in bed', bottom = y, color = "lightblue")			

			if self.report_type == 1:
				sns.lineplot(x = x_soft, y = o_soft, color = "darkblue", markersize = 14, label = "Times out of bed", linewidth = 2 )
				for index in range(len(x_u)):
					if self.report_type == 1:
						#plt.text(x_u[index], o_u[index], math.floor(o_u[index]), size = 11.5, color = "black", ha = 'center', va = 'center', zorder = 11,fontdict = self.font)
						plt.text(x_u[index], o_u[index], math.floor(o_u[index]), size = 11.5,  rotation = 45, fontdict = self.font, bbox=dict(boxstyle='circle', facecolor='lavender', edgecolor='white'))
			if self.report_type == 0:
				sns.lineplot(x = x_soft_1, y = o_soft_1, color = "darkblue", markersize = 14, label = "Hours asleep in bed weekly average", linewidth = 2 )
				date_avg, val_avg = self.weekly_average(x_u,o_u)
				print(val_avg)
				sns.lineplot(x = date_avg, y = val_avg, color = "lavender", markersize = 14, label = "Times out of bed weekly average",  linestyle='--', linewidth = 2 )
				for date, val in zip(date_avg, val_avg):
					if not np.isnan(val):
						plt.text(date, val, math.floor(val), size=11, rotation=45, fontdict= self.font, bbox=dict(boxstyle='circle', facecolor='lavender', edgecolor='white'))
				max_value_stacked = max(chain(y, z, val_avg))
				plt.ylim(top= max_value_stacked + 2)
			# Add labels, title, and legend
			#print(max(y+z))
			plt.grid(axis = "x")
			plt.ylim(bottom = -1)
			
			plt.tick_params(axis = 'x', which = 'major', labelsize = 11)
			plt.ylabel('Hours', fontsize = 11, fontdict = self.font)
			plt.gca().set_title('Sleep Summary', fontsize = 14, loc = 'left',pad = 30, fontweight=600, fontdict = self.font)
			#plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
			plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
			plt.gca().xaxis.set_major_locator((MaxNLocator(nbins=7)))
			#plt.gca().set_xlim((self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)).shift(days = -7), self.end_date)
			# Set the locator for x-axis labels
			plt.gca().spines['top'].set_visible(False)
			plt.gca().spines['right'].set_visible(False)
			#plt.gca().xaxis.set_major_locator(mdates.DayLocator())
			plt.legend(loc= 'upper center', bbox_to_anchor = (0.5,1.09), ncol =3, fontsize = 8.5, frameon=False)

		plt.savefig('sleep_summary', dpi = 500)

	def plot_events(self,start_times, end_times, amplitudes):
		# Create a figure and axis
		fig, ax = plt.subplots()
		rect2 = []
		# x_limit calculation
		x_lim_min = min(start_times)
		#print('Min date', x_lim_min)
		x_lim_max = max(end_times)
		#print('Min date', x_lim_max)

		legend_handles = {}
		# Loop through each event and plot the colored rectangle
		for start_time, end_time, amplitude in zip(start_times, end_times, amplitudes):
			# Convert start and end times to datetime objects
			start_datetime = start_time.datetime
			start_datetime = mdates.date2num(start_datetime)

			end_datetime = end_time.datetime
			end_datetime = mdates.date2num(end_datetime)

			# Calculate the duration of the event in minutes (as an integer)
			width = end_datetime - start_datetime

			# Create a rectangle patch for the event
			#print(amplitude)
			if amplitude == 1:
				color = 'blue'
				label = 'Light Sleep'
			elif amplitude == 2:
				color = 'cyan'
				label = 'Deep Sleep'
			elif amplitude == 3:
				color = 'gray'
				label = 'REM Sleep'
			else:
				color = 'white'
				label = 'Awake'

			rect = Rectangle((start_datetime, 0), width, amplitude, color = color)
			if label not in legend_handles:
				legend_handles[label] = rect

			# Add the rectangle to the plot
			ax.add_patch(rect)

		locator = mdates.AutoDateLocator(minticks = 3)
		formatter = mdates.DateFormatter(fmt = "%m-%d %H:%M" )

		ax.xaxis.set_major_locator(locator)
		ax.xaxis.set_major_formatter(formatter)

		ax.set_xlim(mdates.date2num(x_lim_min.datetime), mdates.date2num(x_lim_max.datetime))
		ax.set_ylim(0, 4)

		ax.set_ylabel('State', rotation = 0, fontdict = self.font)
		ax.set_title('Sleep states', fontsize = 18, fontdict = self.font)
		
		handles = list(legend_handles.values())
		labels = list(legend_handles.keys())

		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)

		# Display the plot
		plt.legend(handles= handles, labels = labels, loc = "upper right", frameon=False)
		plt.show()
		plt.close()