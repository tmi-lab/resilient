import PyPDF2

class PDF_tools(object):
    def __init__(self, paths: None):
        self.paths = paths

    def merge_pdfs(self, pdf1_path, pdf2_path, output_path):
        # Open the PDF files
        with open(pdf1_path, 'rb') as pdf1_file, open(pdf2_path, 'rb') as pdf2_file:
            # Create PDF reader objects
            pdf1_reader = PyPDF2.PdfFileReader(pdf1_file)
            pdf2_reader = PyPDF2.PdfFileReader(pdf2_file)

            # Create a PDF writer object
            pdf_writer = PyPDF2.PdfFileWriter()

            # Loop through each page of the first PDF and add it to the writer
            for page_num in range(pdf1_reader.numPages):
                page = pdf1_reader.getPage(page_num)
                pdf_writer.addPage(page)

            # Loop through each page of the second PDF and add it to the writer
            for page_num in range(pdf2_reader.numPages):
                page = pdf2_reader.getPage(page_num)
                pdf_writer.addPage(page)

            # Write the merged PDF to the output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

    # Paths to the input PDF files and the output merged PDF file
    pdf1_path = 'file1.pdf'
    pdf2_path = 'file2.pdf'
    output_path = 'merged_file.pdf'

    