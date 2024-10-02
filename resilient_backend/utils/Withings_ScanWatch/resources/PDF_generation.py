from ...environment_config import EnvironmentConfig
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
import datetime
import math
import numpy as np

class PDF_generation(object):
	def __init__(self, day_hr: None, 
					night_hr: None, 
					night_rr: None,
					steps: None, 
					sleep_duration: None, 
					sleep_apnoea: None,
					weight: None,
					c_date : None,
					e_date: None,
					path: None,
					id_nhs : None, 
					report_type : None
					):

		#creating the database object
		self.path = path

		# Values for building the table
		self.report_type = report_type
		self.day_hr = day_hr
		self.night_hr = night_hr
		self.night_rr = night_rr
		self.steps = steps
		self.sleep_duration = sleep_duration
		self.sleep_apnoea = sleep_apnoea
		self.weight = weight
		self.c_date = c_date
		self.e_date = e_date

		self.configure_pdf_fonts()

		#Current year
		self.current_year =str(datetime.datetime.now().year)
		#NHS
		self.id = self.id_string(id_nhs)

		self.document_generation()
		return

	def configure_pdf_fonts(self):
		self.env = EnvironmentConfig()
		self.normal_font = self.env.get_config('NORMAL_FONT')
		self.bold_font = self.env.get_config('BOLD_FONT')
		self.normal_font_path = self.env.get_config('NORMAL_FONT_PATH')
		self.bold_font_path = self.env.get_config('BOLD_FONT_PATH')
		# Register the Arial font
		pdfmetrics.registerFont(TTFont(self.normal_font, self.normal_font_path))  # Replace with the actual path
		pdfmetrics.registerFont(TTFont(self.bold_font, self.bold_font_path))  # Replace with the actual path
		return
		
	def id_string(self, x):
		if x.endswith('s'):
			base_id = x.rstrip('s')
		else:
			base_id = x
		formatted_id = '{:03d}'.format(int(base_id))
		if x.endswith('s'):
			formatted_id += 's'
		else:
			formatted_id += 'p'
		return formatted_id


	def averages_data(self, val1, val2, val3, type_d):
		val1 = np.array(val1, dtype=float)
		val1[np.isnan(val1)] = np.nan

		val2 = np.array(val2, dtype=float)
		val2[np.isnan(val2)] = np.nan

		val3 = np.array(val3, dtype=float)
		val3[np.isnan(val3)] = np.nan

		if val1 == [] or (np.all(np.isnan(val1))) or (np.all(val1==0)) or np.all(np.logical_or(val1 == 0, np.isnan(val1))):
			self.mean_val1 = 'N/A'
			self.sd_val1 = ''
			self.var_1 = self.mean_val1
		else:

			val1 = [value for value in val1 if value is not None and value != 0 and not math.isnan(value)]
			self.mean_val1 = math.floor(np.mean(val1))
			#self.mean_val1 = str("{:.2f}".format(self.mean_val1))
			#self.mean_val11 = str(int(self.mean_val1))
			self.sd_val1 = (np.std(val1))
			self.sd_val1 = str("{:.1f}".format(self.sd_val1))
			#self.var_1 = self.mean_val1 + " ± "+ self.sd_val1
			if type_d == "hr" or type_d =="nhr":
				if self.mean_val1 > 90 or self.mean_val1 <51:
					self.mean_val1 = str(self.mean_val1) + '*'
				else:
					self.mean_val1 = str(self.mean_val1)
			if type_d == "rr":
				if self.mean_val1 > 20 or self.mean_val1 < 12:
					self.mean_val1 = str(self.mean_val1) + '*'
				else:
					self.mean_val1 = str(self.mean_val1)
			if type_d == "sa":
				if self.mean_val1 > 0 and self.mean_val1 <= 15:
					self.mean_val1 = str(self.mean_val1) + '\n Normal'
				elif self.mean_val1 > 15 and self.mean_val1 <= 30:
					self.mean_val1 = str(self.mean_val1) + '\n Moderate'
				elif self.mean_val1 > 30 :
					self.mean_val1 = str(self.mean_val1) + '\n Severe'
			self.var_1 = self.mean_val1

		if val2 == [] or (np.all(np.isnan(val2))) or (np.all(val2==0)):
			self.mean_val2 = 'N/A'
			self.sd_val2 = ''
			self.var_2 = self.mean_val2
		else:
			val2 = [value for value in val2 if value is not None and value != 0 and not math.isnan(value)]
			self.mean_val2 = math.floor(np.mean(val2))
			#self.mean_val2 = str("{:.2f}".format(self.mean_val2))
			#self.mean_val2 = str(int(self.mean_val2))
			self.sd_val2 = (np.std(val2))
			self.sd_val2 = str("{:.1f}".format(self.sd_val2))
			#self.var_2 = self.mean_val2 + " ± "+ self.sd_val1
			if type_d == "hr" or type_d =="nhr":
				if self.mean_val2 > 90 or self.mean_val2 < 51:
					self.mean_val2 = str(self.mean_val2) + '*'
				else:
					self.mean_val2 = str(self.mean_val2)
			if type_d == "rr":
				if self.mean_val2 > 20 or self.mean_val2 < 12:
					self.mean_val2 = str(self.mean_val2) + '*'
				else:
					self.mean_val2 = str(self.mean_val2)
			if type_d == "sa":
				if self.mean_val2 > 0 and self.mean_val2 <= 15:
					self.mean_val2 = str(self.mean_val2) + '\n Normal'
				elif self.mean_val2 > 15 and self.mean_val2 <= 30:
					self.mean_val2 = str(self.mean_val2) + '\n Moderate'
				elif self.mean_val2 > 30 :
					self.mean_val2 = str(self.mean_val2) + '\n Severe'
			self.var_2 = self.mean_val2

		if val3 == [] or (np.all(np.isnan(val3))) or (np.all(val3==0)):
			self.mean_val3 = 'N/A'
			self.sd_val3 = ''
			self.var_3 = self.mean_val3
		else:
			val3 = [value for value in val3 if value is not None and value != 0 and not math.isnan(value)]
			self.mean_val3 = (np.mean(val3))
			self.mean_val3 = str(math.floor(self.mean_val3))
			self.sd_val3 = str((np.std(val3)))
			self.var_3 = self.mean_val3 + " ± "+ self.sd_val3
			#self.var_2 = self.mean_val2

		return(self.var_1, self.var_2, self.var_3)

	def sd_comparisson(self, val1, val2, col, row):
		highlight_styles = []

		val1 = [value for value in val1 if value is not None and value != 0 and not math.isnan(value)]
		val2 = [value for value in val2 if value is not None and value != 0 and not math.isnan(value)]
		
		if val1 == [] or val2 == []:
			print('Empty values: No sd sd_comparisson')
		else:
			if (np.mean(val1)) > (np.mean(val2)) + 2 * (np.std(val2)):
				highlight_styles.append(('BACKGROUND', (col, row), (col, row), colors.lightsalmon))
			if (np.mean(val1)) < (np.mean(val2)) - 2 * (np.std(val2)):
				highlight_styles.append(('BACKGROUND', (col, row), (col, row), colors.lightsalmon))
			# Comparison with 1 SD difference
			if (np.mean(val1)) > (np.mean(val2)) + 1 * (np.std(val2)):
				highlight_styles.append(('BACKGROUND', (col, row), (col, row), colors.gold))
			if (np.mean(val1)) < (np.mean(val2)) - 1 * (np.std(val2)):
				highlight_styles.append(('BACKGROUND', (col, row), (col, row), colors.gold))

		return(highlight_styles)

	def conditional_highlighting(self,val1, val2, val3, val4,val5, val6, val7):
		highlight_styles = []
		dayhr_highlight = self.sd_comparisson(val1[0],val1[1], row = 1, col = 1)
		nighthr_highlight = self.sd_comparisson(val2[0],val2[1], row = 1, col = 2)
		nightrr_highlight = self.sd_comparisson(val3[0],val3[1], row = 1, col = 3)
		steps_highlight = self.sd_comparisson(val4[0],val4[1], row = 1, col = 4)
		weight_highlight = self.sd_comparisson(val5[0],val5[1], row = 1, col = 5)
		sleepdur_highlight = self.sd_comparisson(val6[0],val6[1], row = 1, col = 6)
		highlight_styles = (dayhr_highlight + nighthr_highlight + nightrr_highlight + steps_highlight + weight_highlight + sleepdur_highlight)
		return(highlight_styles)

	def create_title_page(self, canvas, doc):
		styles = getSampleStyleSheet()

		# Draw additional text
		text = "Study ID: " + self.id + "                       "+ "Date: "+ self.c_date +" - "+ self.e_date 
		canvas.setFont("Arial", 11)
		canvas.drawString(doc.leftMargin + 8 * cm , doc.height + 2.3 * cm, text)

		#Draw the years in the upper part of the report

		text_year = self.current_year
		canvas.setFont("Arial", 11)
		canvas.drawString(doc.leftMargin + 16.5 * cm , doc.height + 4.2* cm, text_year)

		# Draw NEWS2 text
		text1 = '* indicates a value that would be flagged by the NEWS2'
		canvas.setFont("Arial", 7.3)
		if self.report_type == 1:
			canvas.drawString(doc.leftMargin + 10.5 * cm , doc.height - 3.8* cm, text1)
		if self.report_type == 0:
			canvas.drawString(doc.leftMargin + 10.5 * cm , doc.height - 2.4* cm, text1)
		#Draw sd text

		canvas.setFont("Arial", 7.3)
		if self.report_type == 1:
			text_sd = 'A value highlighted in orange indicates a change of 1 SD from the previous week'
			canvas.drawString(doc.leftMargin - 1.5 * cm , doc.height - 3.8* cm, text_sd)
			
		if self.report_type == 0:
			text_sd = 'A value highlighted in orange indicates a change of 1 SD from the average of the previous 3 months.' 
			canvas.drawString(doc.leftMargin - 1.5 * cm , doc.height - 2.4* cm, text_sd)
		
		canvas.setFont("Arial", 7.3)
		if self.report_type == 1:
			text_2sd = 'A value highlighted in red indicates a change of 2 or more SD from the previous week'
			canvas.drawString(doc.leftMargin - 1.5 * cm , doc.height - 4.1* cm, text_2sd)
			
		if self.report_type == 0:
			text_sd = 'A value highlighted in red indicates a change of 2 or more SD from the average of the previous 3 months.'
			canvas.drawString(doc.leftMargin - 1.5 * cm , doc.height - 2.8* cm, text_sd)
			
		# Add the watermark image
		if self.id.endswith("s"):
			watermark_image = Image("img/surrey_logo_sp.jpg", width = 7*cm, height = 4*cm)
			watermark_image.drawOn(canvas, doc.leftMargin - 2.6*cm , doc.height + 1.5*cm)
		else:
			watermark_image = Image("img/sabp.jpg", width = 10*cm, height = 7*cm)
			watermark_image.drawOn(canvas, doc.leftMargin - 2.6*cm , doc.height + 2.2*cm)

		#Add the Surrey logo project watermark
		surrey_image = Image("img/surrey_logo.jpg", width = 2.143*cm, height = 1.058*cm)
		surrey_image.drawOn(canvas, doc.leftMargin - 0.5*cm , 1*cm)

		#Add the Imperial logo project watermark
		imperial_image = Image("img/Imperial_logo.jpg", width = 4.021*cm, height = 1.058*cm)
		imperial_image.drawOn(canvas, doc.leftMargin + 1.943*cm , 1*cm)

		#Add the NIHR project watermark
		nihr_image = Image("img/nihr_logo.jpg", width = 5.979*cm, height = 1.058*cm)
		nihr_image.drawOn(canvas, doc.leftMargin + 6.264*cm , 1*cm )

		#Add the EPSCR project watermark
		epscr_image = Image("img/epsrc_logo.jpg", width = 4.233*cm, height = 1.058*cm)
		epscr_image.drawOn(canvas, doc.leftMargin + 12.543*cm , 1*cm )

		#Semi-transparent white rectangle to simulate opacity in the EPSCR logo
		canvas.setFillColorRGB(1, 1, 1, 0)  # White with specified opacity (0.5)
		canvas.rect(doc.leftMargin + 8*cm , 1*cm, 9.5*cm , 2.2*cm, fill=True, stroke=False)

		#doc.height - 25.2*cm
		title_text = "RESILIENT: Weekly Health Report"
		title_style = styles['Title']
		title_style.alignment = 1  # Set alignment to center
		title_style.fontSize = 14 
		title_style.fontName = "Arial-Bold" 

		title = Paragraph(title_text, title_style)
		title.wrapOn(canvas, doc.width, doc.height)
		title.drawOn(canvas, doc.leftMargin, doc.height + 3 * cm )

	def document_generation(self):
		# Path where saving the reports
		document_file = self.path + "/"+ (self.id +"_report.pdf")
		
		# Data for the table
		hr_c, hr_p, hr_m = self.averages_data(self.day_hr[0],self.day_hr[1], self.day_hr[2], type_d = 'hr')
		nhr_c, nhr_p, nhr_m = self.averages_data(self.night_hr[0],self.night_hr[1], self.night_hr[2], type_d = 'nhr' )
		rr_c, rr_p, rr_m = self.averages_data(self.night_rr[0],self.night_rr[1], self.night_rr[2], type_d = 'rr' )
		steps_c, steps_p, steps_m = self.averages_data(self.steps[0],self.steps[1], self.steps[2], type_d = 'steps' )
		sd_c,sd_p, sd_m = self.averages_data(self.sleep_duration[0],self.sleep_duration[1], self.sleep_duration[2], type_d = 'sd')
		sa_c,sa_p, sa_m  = self.averages_data(self.sleep_apnoea[0],self.sleep_apnoea[1],self.sleep_apnoea[2], type_d = 'sa')
		w_c, w_p, w_m = self.averages_data(self.weight[0], self.weight[1], self.weight[2], type_d = 'weight')

		if self.report_type == 1:
			# Create a list of data for the table
			data = [
	    	["Overview", "Day Heart \n  Rate \n [bpm]", "Sleep \n Heart Rate \n [bpm]", "Sleep \n Respiration \n Rate", "Steps",  "Weight \n [kg]", "Sleep \n Duration \n [hours]", " Sleep \n Apnoea Index \n [AHI] "],
	    	["Current Week \n Average",hr_c , nhr_c , rr_c , steps_c, w_c , sd_c , sa_c],
	    	["Last Week \n Average",hr_p , nhr_p  ,rr_p , steps_p , w_p , sd_p  , sa_p],
	    	["Monthly values \n (Mean. +/- 1 SD)", hr_m, nhr_m, rr_m , steps_m, w_m , sd_m, sa_m]
					]
		elif self.report_type ==0:
			# Create a list of data for the table
			data = [
	    	["Overview", "Day Heart \n  Rate \n [bpm]", "Sleep \n Heart Rate \n [bpm]", "Sleep \n Respiration \n Rate", "Steps",  "Weight \n [kg]", "Sleep \n Duration \n [hours]", " Sleep \n Apnoea Index \n [AHI] "],
	    	["Current Week \n Average",hr_c , nhr_c , rr_c , steps_c, w_c , sd_c , sa_c],
	    	[f"Average since \n {self.c_date}",hr_p , nhr_p  ,rr_p , steps_p , w_p , sd_p  , sa_p]
	    			]

		# Create a list of images for the matrix plot
		images = [
    		"HR_ScanWatchScatter.png",
    		"HRScatter.png",
    		"RRScatter.png",
    		"Steps_curvedbar.png",
    		"Scale.png",
    		"sleep_summary.png",
			]

		# Define the size and positioning of the table and images
		table_width = 8 * inch
		table_height = 1.68 * inch
		image_width = 3.5 * inch
		image_height = 2.17 * inch
		spacing = 0.4 * cm

		# Create a canvas and set the size
		doc = SimpleDocTemplate(document_file, pagesize = A4, title="Resilient")

		# Add the title page to the document
		styles = getSampleStyleSheet()
		doc.build([Paragraph("", styles['Normal'])], onFirstPage=self.create_title_page)

		# Create a table object and set its properties
		table = Table(data)
		table.setStyle(TableStyle([
    		('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
    		('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
    		('TEXTCOLOR', (0, 0), (0, -1), colors.black),
    		('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    		('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
    		('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    		('GRID', (0, 0), (-1, -1), 1, colors.black),
		]))

		# Changing the font size for row 1
		table_style = TableStyle([('FONTSIZE', (0, 0), (-1, 0), 10)])
		table.setStyle(table_style)

		# Changing the font size for column 1
		for i in range(1, len(data)):
			table_style = TableStyle([('FONTSIZE', (0, i), (0, i), 10)])
			table.setStyle(table_style)

		#conditionals for the table
		m = self.conditional_highlighting(self.day_hr, self.night_hr, self.night_rr,
										  self.steps, self.weight, self.sleep_duration, self.sleep_apnoea,
										  )
		highlight_table_style = TableStyle(m)
		table.setStyle(highlight_table_style)

		spacer1 = Spacer(3, spacing)
		spacer2 = Spacer(10, spacing)

		# Create a list to hold the images
		image_list = []

		# Add the images to the list
		for image_path in images:
			image = Image(image_path, width=image_width, height=image_height)
			image_list.append(image)

		# Create a table for the images in a matrix-like plot
		image_table = Table([image_list[i:i+2] for i in range(0, len(image_list), 2)])

		# Build the PDF document
		elements = [spacer1,table, spacer2, spacer2, spacer1, image_table]
		doc.build(elements)

	@classmethod
	def main(cls):
		a = cls(day_hr = None, 
					night_hr = None, 
					night_rr = None,
					steps = None, 
					sleep_duration = None, 
					sleep_apnoea =None,
					weight = None)
	
if __name__ == "__main__":
    PDF_generation.main()

