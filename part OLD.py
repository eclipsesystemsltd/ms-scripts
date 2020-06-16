import MySQLdb as mdb
import sys

def process(line, cur):
	f = line.split()
	#refNumber = f[0]
	partNumber = f[1].strip()
	if partNumber == "-------": partNumber = "NULL"
	desc = line[11:]
	
	#Work out description
	endOfLine = len(desc)
	specialChars = ["*","$","#","~","^","`","\\"]
	for char in specialChars:
		position = desc.find(char)
		if position < endOfLine and position > -1:
			endOfLine = position
	description = desc[0:endOfLine].strip()
	
	#See if alternative part number defined
	altPartNumber = "NULL"
	altPartNumberManufacturer = "NULL"
	qPosn = desc.find("$")
	altPartNoPosn = desc.find("*")
	if altPartNoPosn > -1 and altPartNoPosn < qPosn:
		altPartNoPlus = desc[altPartNoPosn + 1:]
		altPartNo = altPartNoPlus.split()[0]
		constituents = altPartNo.split("_")
		altPartNumberManufacturer = constituents[0].strip()
		altPartNumber = constituents[1].strip()
	
	if partNumber != "NULL" and altPartNumber == "NULL":
		savePart2(cur, partNumber, description)
	elif partNumber != "NULL" and altPartNumber != "NULL":
		savePart4(cur, partNumber, description, altPartNumber, altPartNumberManufacturer)
	elif partNumber == "NULL" and altPartNumber != "NULL":
		savePart3(cur, description, altPartNumber, altPartNumberManufacturer)

def savePart4(cur, partNumber, description, altPartNumber, altPartNumberManufacturer):
	try:
		query = 'insert into part(part_number, description, alt_part_number, alt_part_manufacturer) values(%s,%s,%s,%s)'
		values = (partNumber, description, altPartNumber, altPartNumberManufacturer)
		cur.execute(query, values)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def savePart2(cur, partNumber, description):
	try:
		query = 'insert into part(part_number, description) values(%s,%s)'
		values = (partNumber, description)
		cur.execute(query, values)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e
		
def savePart3(cur, description, altPartNumber, altPartNumberManufacturer):
	try:
		query = 'insert into part(description, alt_part_number, alt_part_manufacturer) values(%s,%s,%s)'
		values = (description, altPartNumber, altPartNumberManufacturer)
		cur.execute(query, values)
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
			line.strip()
			if len(line) > 1 and line[0] != '*' and line[0] != '/' and line[0] != ' ' and line[0] != '\t':
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

