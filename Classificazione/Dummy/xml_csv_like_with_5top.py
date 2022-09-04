# This file is used to transform the original news report in a file
# that will be parsable by the handler of Solr, regarding the
# specifics in the Apache Solr Guide.
# Respect the other one, it also takes the 5 top categories (by score) and write them 
# to the xml file ready to be parsed, in case, into the csv.
#
# Author: Paolo Ciasco



import xml.etree.ElementTree as et


## Namespace registration for correct parsing to avoid "ns" tag in the output file

et.register_namespace('emm', "http://emm.jrc.it")
et.register_namespace('iso', "http://www.iso.org/3166")
et.register_namespace('georss', "http://www.georss.org/georss")

#####

oldtree = et.parse("C:/Users/Paolo/OneDrive - Universita' degli Studi di Roma Tor Vergata/Laurea Magistrale/Tesi/Codice/2.Classificazione/Dummy/Data/LargeScale_Report_August2022.xml") # File's loading (beautified version)
myroot = oldtree.getroot() # Root selection

newroot = et.Element("add") # Root creation of the new file to be indexed ready to Solr

doc = [] 
i = 0 
j = 0
z = 0
z1 = 0
array_dict = []
dict_cate = {}

## Every item in the original file is a doc to be indexed
## These loops search for a national news (not in a specified region) and append a new "doc" subelement in the xml output file
## This is a solution for the issue written on the thesis at the end of the 2.0.1 subchapter

for child in myroot:
    if (child.tag == 'section'):
        for child2 in child:
            if (child2.tag == 'item'):
                doc.append(et.SubElement(newroot, "doc"))
              
## These loops search for a regional news and append a new "doc" subelement in the xml output file
            
for child in myroot:
    if (child.tag == 'section'):
        for child2 in child:
            if (child2.tag == 'section'):
                for child3 in child2:
                    if (child3.tag == 'item'):
                        doc.append(et.SubElement(newroot, "doc"))

## Once the "doc" structure is well written in the output file, the script starts to copy the selected information in the output file without the categories
## they will be inserted in a second time from the array of dictionaries

## National News


for child in myroot:
    if (child.tag == 'section'):
        for child2 in child:
            if (child2.tag == 'item'):
                array_dict.append(dict_cate.copy())
                for child3 in child2:
                    if (child3.tag == 'title'):
                        et.SubElement(doc[i], "title").text = child3.text
                    if (child3.tag == 'link'):
                        et.SubElement(doc[i], "source").text = child3.text
                    if (child3.tag == 'description'):
                        et.SubElement(doc[i], "news").text = child3.text.replace("\n", " ") # This will also fix some newline characters unwanted
                    if (child3.tag == 'category' and type(child3.attrib.get("{http://emm.jrc.it}score")) is not type(None) and int(child3.attrib.get("{http://emm.jrc.it}score")) > 0):
                        array_dict[j][child3.text] = child3.attrib.get("{http://emm.jrc.it}score")
                    if (child3.tag == 'pubDate'):
                        et.SubElement(doc[i], "date").text = child3.text
                        i += 1
                j = j + 1    



######

i2 = i # Counter to make sure the fill of the "doc" starts right after the national news
j1 = j # Counter to make sure the fill of the array of dictionaries starts right after the national news one

## Regional News

for child in myroot:
    if (child.tag == 'section'):
        for child2 in child:
            if (child2.tag == 'section'):
                for child3 in child2:
                    if (child3.tag == 'item'):
                        array_dict.append(dict_cate.copy())
                        for child4 in child3:
                            if (child4.tag == 'title' and i2 < len(doc)):
                                et.SubElement(doc[i2], "title").text = child4.text
                            if (child4.tag == 'link' and i2 < len(doc)) :
                                et.SubElement(doc[i2], "source").text = child4.text
                            if (child4.tag == 'description' and i2 < len(doc)):
                                et.SubElement(doc[i2], "news").text = child4.text.replace("\n", " ")
                            if (child4.tag == 'category' and i2 <= len(doc) and type(child4.attrib.get("{http://emm.jrc.it}score")) is not type(None) and int(child4.attrib.get("{http://emm.jrc.it}score")) > 0):
                                array_dict[j1][child4.text] = child4.attrib.get("{http://emm.jrc.it}score")
                            if (child4.tag == 'pubDate' and i2 < len(doc)):
                                et.SubElement(doc[i2], "date").text = child4.text
                                i2 += 1
                        j1 = j1 + 1    
######                           

# Sorting of the categories

for element in array_dict:
     array_dict[z] = dict(sorted(element.items(), key=lambda x:int(x[1]), reverse=True))
     z = z + 1

# Selection of the top 5 (they have been ordered in decrescent order)
 
for element in array_dict:
    array_dict[z1] = list(element.items())[:5]
    z1 = z1 + 1


i = 0 # Reset of the counter

# Fill of the categories in the output file

for element in array_dict:
    for categories in element:
        et.SubElement(doc[i], "category").text = categories[0]
    i = i + 1


tree = et.ElementTree(newroot) # New tree generation for the output file

et.indent(tree, space="\t", level=0) # Correct indentation (needs Python >= 3.9)
tree.write("C:/Users/Paolo/OneDrive - Universita' degli Studi di Roma Tor Vergata/Laurea Magistrale/Tesi/Codice/2.Classificazione/Dummy/Data/LargeScale_Report_August2022_to_be_csved.xml", encoding='utf-8') # Writing of the new xml file to be indexed


