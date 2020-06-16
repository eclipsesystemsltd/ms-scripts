import MySQLdb as mdb
import sys

majorModelId = -1
minorModels = ''
year = -1
title = ''
modelsSaved = False
minorModelIds = []

def process(line, cur):
	global majorModelId
	global minorModels
	global year
	global title
	global modelsSaved
	global minorModelIds

	if line.find("*major_model") == 0:
		majorModel = line[13:].strip()
		# get model range id from db
		majorModelId = getMajorModel(cur, majorModel)
		print majorModelId
	elif line.find("*minor_model") == 0:
		models = line[13:].strip()
		minorModels = models.split(',')
		print minorModels
	elif line.find("*year") == 0:
		year = line[5:].strip()
		print year
	elif line.find("*title") == 0:
		title = line[6:].strip()
		saveTitle(cur, title)
		#print title

	if minorModels != '' and year != -1 and modelsSaved == False:
		print 'Saving minorModels ' + year
		saveMinorModels(cur, minorModels, majorModelId, year)
		modelsSaved = True


def saveTitle(cur, title):
	query = 'insert into section(title) values(%s)'
	values = (title)
	cur.execute(query, values)
	titleId = cur.lastrowid
	query = 'insert into model_section(model_id, section_id) values(%s,%s)'
	for minorModelId in minorModelIds:
		values = (minorModelId, titleId)
		cur.execute(query, values)


def saveMinorModels(cur, minorModels, majorModelId, year):
	try:
		query = 'insert into model(name, first_year, last_year, modelrange_id) values(%s,%s,%s,%s)'
		for minorModel in minorModels:
			print minorModel.strip()
			values = (minorModel.strip(), year, year, majorModelId)
			cur.execute(query, values)
			minorModelIds.append(cur.lastrowid)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e


def getMajorModel(cur, majorModel):
	try:
		query = 'select id from modelrange where name = %s'
		values = (majorModel)
		cur.execute(query, values)
		id = [r[0] for r in cur.fetchall()]
		return id[0]
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def main(filename):
	global majorModelId
	global minorModels
	global year
	global title
	global modelsSaved
	global minorModelIds
	majorModelId = -1
	minorModels = ''
	year = -1
	title = ''
	modelsSaved = False
	minorModelIds = []
	conn = None
	f = None
	try:
		f = open(filename)
		conn = mdb.connect('localhost', 'root', 'password', 'msdb')	
		cur = conn.cursor()
		while True:
			line = f.readline()
			if not line: break
			if len(line) > 1 and line[0] == '*':
				line = line.strip()
				process(line, cur)
	except mdb.Error, e:
		print "Error connecting to database"
		sys.exit(1)
	finally:
		if conn: conn.close()
		if f: f.close()

#Main
if __name__ == '__main__':
	filename = raw_input('Enter file name: ')
	if len(filename) > 0:
		main(filename)
	else:
		print 'Filename must be entered!'

