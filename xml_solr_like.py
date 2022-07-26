import xml.etree.ElementTree as et

## Namespace registration for correct parsing to avoid "ns" tag in the output file

et.register_namespace('emm', "http://emm.jrc.it")
et.register_namespace('iso', "http://www.iso.org/3166")
et.register_namespace('georss', "http://www.georss.org/georss")

#####

oldtree = et.parse('C:/Users/Paolo/Documents/Report_Fixed.xml') # File's loading (beautified version)
myroot = oldtree.getroot() # Root selection

newroot = et.Element("add") # Root creation of the new file to be indexed ready to Solr

doc = [] 
i = 0 # Counter to scan the "doc" elements

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

## Once the "doc" structure is well written in the output file, the script starts to copy the selected information in the output file

## National News

for child in myroot:
    if (child.tag == 'section'):
        for child2 in child:
            if (child2.tag == 'item'):
                for child3 in child2:
                    if (child3.tag == 'title'):
                        et.SubElement(doc[i], "field", name="title").text = child3.text
                    if (child3.tag == 'link'):
                        et.SubElement(doc[i], "field", name="source").text = child3.text
                    if (child3.tag == 'description'):
                        et.SubElement(doc[i], "field", name="news").text = child3.text
                    if (child3.tag == 'pubDate'):
                        et.SubElement(doc[i], "field", name="date").text = child3.text
                        et.SubElement(doc[i], "field", name = "category").text = child.attrib.get("title")
                        i += 1

######

i2 = i # Counter to make sure the fill of the "doc" starts right after the national news

## Regional News

for child in myroot:
    if (child.tag == 'section'):
        for child2 in child:
            if (child2.tag == 'section'):
                for child3 in child2:
                    if (child3.tag == 'item'):
                        for child4 in child3:
                            if (child4.tag == 'title'):
                                et.SubElement(doc[i2], "field", name="title").text = child4.text
                            if (child4.tag == 'link'):
                                et.SubElement(doc[i2], "field", name="source").text = child4.text
                            if (child4.tag == 'description'):
                                et.SubElement(doc[i2], "field", name="news").text = child4.text
                            if (child4.tag == 'pubDate'):
                                et.SubElement(doc[i2], "field", name="date").text = child4.text
                                et.SubElement(doc[i2], "field", name = "category").text = child.attrib.get("title")
                                i2 += 1

######                           



tree = et.ElementTree(newroot) # New tree generation for the output file

et.indent(tree, space="\t", level=0) # Correct indentation (needs Python >= 3.9)
tree.write('C:/Users/Paolo/Documents/to_be_indexed.xml', encoding='utf-8') # Writing of the new xml file to be indexed


