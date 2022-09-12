# This file is used to merge all the xml files in a single one
# with the same root.
#
# Author: Paolo Ciasco


import xml.etree.ElementTree as et
import os

path = "" # Path where all the files are
paths = []

dirs = os.listdir(path)
for name in dirs:
    paths.append(path + name)

tree_list = []
root_list = []


for element in paths:
    tree_list.append(et.parse(element))

for element in tree_list:
    root_list.append(element.getroot())

for element in root_list:
    root_list[0].extend(element)

tree_list[0].write("") # Output's path
