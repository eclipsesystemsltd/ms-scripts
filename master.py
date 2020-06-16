import os
import model
import part
import sectionitem
#from model import *
#from part import *
#from sectionitem import *

#Main
directory = raw_input("Enter directory : ")
if directory == "":
	directory = '.'
for file in os.listdir(directory):
	filename = file.lower()
	if filename.endswith('.lst') or filename.endswith('.int'):
		print filename
		filename = '/home/user/meriden/scripts/' + filename
		model.main(filename)
		part.main(filename)
		sectionitem.main(filename)
