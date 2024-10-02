from ...environment_config import EnvironmentConfig
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph

class PDF_Usage(object):
    def __init__(self, path: None,
                 id_user: None,
                 start_date: None,
                 end_date: None,
                 sleepmat_usage: None,
                 sleepmat_battery: None,
                 sleepmat_last: None, 
                 watch_usage: None,
                 watch_battery: None,
                 watch_last: None,
                 scale_usage: None,
                 scale_battery: None,
                 scale_last: None
                 ):
        
        self.id_user = id_user
        self.start_date = start_date
        self.end_date = end_date
        self.sleep_usage = sleepmat_usage
        self.sleep_battery = sleepmat_battery
        self.sleep_last = sleepmat_last
        self.watch_usage = watch_usage
        self.watch_battery = watch_battery
        self.watch_last = watch_last
        self.scale_usage = scale_usage
        self.scale_battery = scale_battery
        self.scale_last = scale_last

        self.configure_pdf_fonts()
        self.create_pdf()

    def configure_pdf_fonts(self):
        self.env = EnvironmentConfig()
        self.normal_font = self.env.get_config('NORMAL_FONT')
        self.bold_font = self.env.get_config('BOLD_FONT')
        self.normal_font_path = self.env.get_config('NORMAL_FONT_PATH')
        self.bold_font_path = self.env.get_config('BOLD_FONT_PATH')
        # Register the Arial font
        pdfmetrics.registerFont(TTFont(self.normal_font, self.normal_font_path))  # Replace with the actual path
        pdfmetrics.registerFont(TTFont(self.bold_font, self.bold_font_path))  # Replace with the actual path


    def conditional_highlight(self,row):
        return row[1] == "Low" or row[4] == "Low" or row[7] == "Low"


    def create_title_page(self, canvas, doc):    
        styles = getSampleStyleSheet()
    
		#Draw the years in the upper part of the report
        
        #text_year = self.current_year
        #canvas.setFont("Arial", 11)
        #canvas.drawString(doc.leftMargin + 16.5 * cm , doc.height + 4.2* cm, text_year)

		# Draw NEWS2 text
        text_scale = 'Scale Usage: ' + str(self.start_date[0]) + ' - ' + str(self.end_date[0]) 
        canvas.setFont("Arial", 11)
        canvas.drawString(doc.leftMargin + 12 * cm , doc.height + 1.6 * cm, text_scale)
        #Draw sd text
        canvas.setFont("Arial", 11)
        text_watch = 'Watch Usage: ' + str(self.start_date[0]) + ' - ' + str(self.end_date[0]) 
        canvas.drawString(doc.leftMargin + 12 * cm , doc.height + 2.2 * cm, text_watch)
                  
        text_sleep = 'Sleepmat Usage: ' + str(self.start_date[0]) + ' - ' + str(self.end_date[0]) 
        canvas.drawString(doc.leftMargin + 12 * cm , doc.height + 2.8* cm, text_sleep)
            
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
        title_text = "RESILIENT: Weekly Usage Report"
        title_style = styles['Title']
        title_style.alignment = 1  # Set alignment to center
        title_style.fontSize = 14 
        title_style.fontName = "Arial-Bold" 
        
        title = Paragraph(title_text, title_style)
        title.wrapOn(canvas, doc.width, doc.height)
        title.drawOn(canvas, doc.leftMargin, doc.height + 3 * cm )

    def create_pdf(self):
        # Create a PDF document
        pdf_filename = "usage_report.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        doc.build([Paragraph("", styles['Normal'])], onFirstPage=self.create_title_page)

        # Create a list to hold data for the table
        data = []
        
        # Add header row to the table
        header_row = ['id', 'Sleepmat \n Usage', 'Sleepmat \n  Battery', 'Sleepmat \n Last \n  Reading', 'Watch \n Usage', 'Watch \n Battery', 'Watch \n Last \n  Reading', 'Scale \n Usage', 'Scale \n Battery', 'Scale \n Last \n Reading']
        print(len(header_row))
        data.append(header_row)
        # Add rows with images to the table
        for x,z,m,n,l, o, p,j,i,q in zip(self.id_user, self.sleep_usage, self.sleep_battery, self.sleep_last, 
                                       self.watch_usage, self.watch_battery, self.watch_last, self.scale_usage, self.scale_battery, self.scale_last
                                        ):
            row = [x, z, m, n, l, o, p,j,i,q]

            if m == 'low':
                row[2] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/low_battery.jpg', width = 10, height = 10)
            elif m == 'medium':
                row[2] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/medium_battery.jpg', width = 10, height = 10)             
            elif m == 'high':
                row[2] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/high_battery.jpg', width = 10, height = 10)

            if o == 'low':
                row[5] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/low_battery.jpg', width = 10, height = 10)
            elif o == 'medium':
                row[5] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/medium_battery.jpg', width = 10, height = 10)    
            elif o == 'high':
                row[5] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/high_battery.jpg', width = 10, height = 10)

            if i == 'low':
                row[8] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/low_battery.jpg', width = 10, height = 10)
            elif i == 'medium':
                row[8] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/medium_battery.jpg', width = 10, height = 10)    
            elif i == 'high':
                row[8] = Image('/home/nathalia/Withings_ScanWatch/Withings_ScanWatch/img/high_battery.jpg', width = 10, height = 10)

            
            data.append(row)
        
        # Create the table and apply styles
        table = Table(data)
        table.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                ]))
        spacing = 0.9*cm
        spacer1 = Spacer(5, spacing)
        # Define a style with the desired font size
        
        styles = getSampleStyleSheet()
        style = styles['Normal']
        style.fontSize = 3  # Set font size to 12
        
        # Apply the style to the table
        for i in range(len(data)):
            for j in range(len(data[i])):
                table.setStyle([('FONT', (j, i), (j, i), 'Arial', 10.5)])

        # Conditional Highlighting styles

        # Apply additional style to highlighted rows
        for i, row in enumerate(data):
            #print(row)
            print(self.conditional_highlight(row))
            if self.conditional_highlight(row):
                table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.orange)]))
    
        
        # Add the table to the PDF document
        doc.build([spacer1,table])

    @classmethod
    def main(cls):
        
        a = cls( path = None,
            id_user = None,
            start_date =None,
            end_date = None,
            sleepmat_usage = None,
            sleepmat_battery = None,
            sleepmat_last = None, 
            watch_usage = None,
            watch_battery = None,
            watch_last = None,
            scale_usage =None,
            scale_battery = None,
            scale_last = None)
        
        a.create_pdf([1,2,3,4,5,6,7,8], ['10 Feb', '10 Feb', '10 Feb', '10 Feb', '10 Feb', '10 Feb', '10 Feb'])
    
if __name__ == "__main__":
    PDF_Usage.main()


        

        
        
