import MySQLdb as mdb
import sys
import PartClass
from PartClass import *

def process(line, cur):
	partObj = Part(line)
	if partObj.partNumber != None and partObj.altManuPartNumber == None:
		savePart2(cur, partObj.partNumber, partObj.description)
	elif partObj.partNumber != None and partObj.altManuPartNumber != None:
		savePart4(cur, partObj.partNumber, partObj.description, partObj.altManuPartNumber, partObj.altManuName)
	elif partObj.partNumber == None and partObj.altManuPartNumber != None:
		savePart3(cur, partObj.description, partObj.altManuPartNumber, partObj.altManuName)

def savePart4(cur, partNumber, description, altPartNumber, altPartNumberManufacturer):
	try:
		query1 = 'insert into stockitem(partnumber, description) values(%s,%s)'
		values1 = (partNumber, description)
		cur.execute(query1, values1)
		id = cur.lastrowid
		query2 = 'insert into part(id, altpartnumber, altpartmanufacturer) values(%s,%s,%s)'
#		query2 = 'insert into part(id, partnumber, description, altpartnumber, altpartmanufacturer) values(%s,%s,%s,%s,%s)'
		values2 = (id, altPartNumber, altPartNumberManufacturer)
#		values2 = (id, partNumber, description, altPartNumber, altPartNumberManufacturer)
		cur.execute(query2, values2)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def savePart2(cur, partNumber, description):
	try:
		query1 = 'insert into stockitem(partnumber, description) values(%s,%s)'
		values1 = (partNumber, description)
		cur.execute(query1, values1)
		id = cur.lastrowid
		query2 = 'insert into part(id) values(%s)'
#		query2 = 'insert into part(id, partnumber, description) values(%s,%s,%s)'
		values2 = (id)
#		values2 = (id, partNumber, description)
		cur.execute(query2, values2)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e
		
def savePart3(cur, description, altPartNumber, altPartNumberManufacturer):
	try:
		query1 = 'insert into stockitem(description) values(%s)'
		values1 = (description)
		cur.execute(query1, values1)
		id = cur.lastrowid
		query2 = 'insert into part(id, altpartnumber, altpartmanufacturer) values(%s,%s,%s)'
#		query2 = 'insert into part(id, description, altpartnumber, altpartmanufacturer) values(%s,%s,%s,%s)'
		values2 = (id, altPartNumber, altPartNumberManufacturer)
#		values2 = (id, description, altPartNumber, altPartNumberManufacturer)
		cur.execute(query2, values2)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def main(filename):
	try:
		f = open(filename)
		conn = mdb.connect('localhost', 'root', 'password', 'msdb')		
		cur = conn.cursor()
		while True:
			line = f.readline()
			if not line: break
			# Min line length of 2 to allow for CR/LF
			if len(line) > 2 and line[0] != '*' and line[0] != '/' and line[0] != ' ' and line[0] != '\t':
				line = line.strip()
				process(line, cur)
	except mdb.Error, e:
		print "Error connecting to database"
		sys.exit(1)
	finally:
		if conn: conn.close()
		f.close()

#Main
if __name__ == '__main__':
	filename = raw_input('Enter file name: ')
	if len(filename) > 0:
		main(filename)
	else:
		print 'Filename must be entered!'

