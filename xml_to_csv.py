# This file trasform the xml file in the csv one for the generation of the dataset.
#
# Author: Paolo Ciasco

import os
from xml.etree import ElementTree
import csv

path_to_xml = os.path.join('Files_to_process', 'news_to_be_csved.xml')

xml = ElementTree.parse(path_to_xml) # File's loading
def find_max_number_categories(): # This function finds the max number of categories of the news

    max_categories = 0
    doc_categories = 0

    for doc in xml.findall("doc"):
        for element in doc:
            if (element.tag == 'category'):
                doc_categories = doc_categories + 1
        if(doc_categories > max_categories):
            max_categories = doc_categories
        doc_categories = 0           
               
    return max_categories
                


def create_string(): # This function creates all the categories ready to be written in the header of the csv file
    phrase = ""
    for number in range(find_max_number_categories()):
        phrase = phrase + 'category___'
        
    return phrase[:-3]

def write_categories(doc): # This function writes all the categories of a specific doc
    phrase = ''
    for element in doc:
        if (element.tag == 'category'):
            phrase = phrase  + element.text + '___'
    return phrase[:-3]
    
         

output_csv = os.path.join('Files_to_process', 'news_dataset.csv')
csvfile = open(output_csv,"w", encoding='utf-8') # CSV Creation
csvfile_writer = csv.writer(csvfile)

csvfile.write('\ufeff') # Metadata for the right "utf-8" encoding
header = "title___" + "source___" + "news___" + create_string() + '\n'
csvfile.write(header)


# For all the docs in the input file, retrive the text of the fields (name, source, news, category) and write them in a line of the csv file

for doc in xml.findall("doc"):
    if(doc):
            name = doc.find("title").text
            if(doc.find("source") != None): 
                source = doc.find("source").text
            else:
                source = None
            if(doc.find("news") != None):
                news = doc.find("news").text
            else:
                news = None
            categories = write_categories(doc)
            
            if(name == None or source == None or news == None or categories == None):
                csv_line = ''
            else:
                csv_line =  name + '___'  + source   + '___' + str(news) + '___' + categories  + '\n'
            
            csvfile.write(csv_line)
    


csvfile.close()
        
