# This file trasform the xml file in the csv one for the generation of the dataset.
#
# Author: Paolo Ciasco


from xml.etree import ElementTree
import csv

xml = ElementTree.parse("C:/Users/Paolo/Documents/to_be_csved.xml") # File's loading

csvfile = open("C:/Users/Paolo/Documents/data.csv", "w", encoding='utf-8') # CSV Creation
csvfile_writer = csv.writer(csvfile)

csvfile.write('\ufeff') # Metadata for the right "utf-8" encoding
csvfile_writer.writerow(["title", "source", "news", "category"]) # Writing of the csv header

# For all the docs in the input file, retrive the text of the fields (name, source, news, category) and write them in a line of the csv file

for doc in xml.findall("doc"):
    if(doc):
            name = doc.find("title").text 
            source = doc.find("source").text
            news = doc.find("news").text
            category = doc.find("category").text
            csv_line = [name,source,news,category]

            csvfile_writer.writerow(csv_line)

csvfile.close()
        