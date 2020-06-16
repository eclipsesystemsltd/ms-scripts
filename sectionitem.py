import MySQLdb as mdb
import sys
import PartClass
import AssemblyClass
import VariantAssemblyClass
from PartClass import *
from AssemblyClass import *
from VariantAssemblyClass import *

minorModels = ''
year = -1
titleId = -1
currentSectionId = -1
currentPartId = -1
modelsFound = False
minorModelIds = []
lineNo = 0
variantStrings = []
assyLinesToGo = []
assemblies = []
variantassemblies = []

def process(line, cur):
	global minorModels
	global year
	global title
	global modelsFound
	global minorModelIds
	global currentSectionId
	global currentPartId
	global lineNo
	global variantStrings
	global assemblyState

	if line.find("*minor_model") == 0:
		models = line[13:].strip()
		minorModels = models.split(',')
		print minorModels
	elif line.find("*year") == 0:
		year = line[5:].strip()
		print year
	elif line.find("*title") == 0:
		title = line[6:].strip()
		currentSectionId = findSection(cur, title, minorModelIds[0])
		lineNo = 1
	elif line.find("*variant_start") == 0:
		variant = line[15:].strip()
		saveDirectiveWithValue(cur, 'variant_start', variant, lineNo, currentSectionId)
		variantStrings.append(variant)
	elif line.find("*variant ") == 0:
		variant = line[9:].strip()
		saveDirectiveWithValue(cur, 'variant', variant, lineNo, currentSectionId)
		variantStrings.pop()
		variantStrings.append(variant)
	elif line.find("*variant_end") == 0:
		saveDirective(cur, 'variant_end', lineNo, currentSectionId)
		variantStrings.pop()
	elif line.find("*variant_quantity ") == 0:
		#TODO sort this out in better way ********
		variantQuantityExpression = line[18:].strip()
		saveDirectiveWithValue(cur, 'variant_quantity', variantQuantityExpression, lineNo, currentSectionId)
	elif line.find("*variant_quantity_end") == 0:
		#TODO sort this out in better way ********
		saveDirective(cur, 'variant_quantity_end', lineNo, currentSectionId)
	elif line.find("*variant_assembly_start") == 0:
		saveDirective(cur, 'variant_assembly_start', lineNo, currentSectionId)
		varassy = VariantAssembly()
		variantassemblies.append(varassy)
	elif line.find("*variant_assembly ") == 0:
		variantAssembly = line[18:].strip()
		variantassemblies[0].setVariant(variantAssembly)
		saveDirectiveWithValue(cur, 'variant_assembly', variantAssembly, lineNo, currentSectionId)
	elif line.find("*in_assembly ") == 0:
		inAssembly = line[13:].strip()
		variantassemblies[0].setIn(inAssembly)
		saveDirectiveWithValue(cur, 'in_assembly', inAssembly, lineNo, currentSectionId)
	elif line.find("*common_assembly") == 0:
		variantassemblies[0].setCommon()
		saveDirective(cur, 'common_assembly', lineNo, currentSectionId)
	elif line.find("*variant_assembly_end") == 0:
		variantassemblies[0].save(cur)
		variantassemblies.pop()
		saveDirective(cur, 'variant_assembly_end', lineNo, currentSectionId)
	elif line.find("*variant_one_of_set") == 0:
		#TODO sort this out in better way ********
		oneOfSet = line[20:].strip()
		saveDirectiveWithValue(cur, 'variant_one_of_set', oneOfSet, lineNo, currentSectionId)
	elif line.find("*end_variant_set") == 0:
		#TODO sort this out in better way ********
		saveDirective(cur, 'end_variant_set', lineNo, currentSectionId)
	# Ignore other directives
	elif line.find("*") == 0:
		None
	else:
		part = processPart(cur, lineNo, line)
		if part.partNumber != None:
			currentPartId = findPart(cur, part.partNumber)
		else:
			currentPartId = None
			
		if part.isAssembly:
			if len(assyLinesToGo) > 0:
				assyLinesToGo[len(assyLinesToGo) - 1] -= 1
			assyLinesToGo.append(part.assemblyLines)
		#print assyLinesToGo
		inAssembly = 0
		if len(assyLinesToGo) > 0:
			inAssembly = 1
		variantString = ','.join(variantStrings)
		#print 'variantString = ' + variantString
		######################
		### Save part here ###
		######################
		savePart(cur, part, variantString, inAssembly, len(assyLinesToGo), lineNo, currentSectionId, currentPartId)
		sectionItemId = cur.lastrowid
		#Update existing assembly...
		if len(assyLinesToGo) > 0 and len(assemblies) > 0:
			assemblies[len(assemblies) - 1].add(currentPartId, sectionItemId, part.quantity)
			#print 'Added ' + str(len(assemblies)) + '   ' + str(sectionItemId)
		#...before appending new assembly
		if part.isAssembly:
			assembly = Assembly(currentPartId, sectionItemId)
			assemblies.append(assembly)
		#Clean up if reached end of assembly definition
		if len(assyLinesToGo) > 0:
			#print assyLinesToGo
			#print assemblies
			assyLinesToGo[len(assyLinesToGo) - 1] -= 1
			i = len(assyLinesToGo) - 1
			while i >= 0:				
				if assyLinesToGo[i] == 0:
					assyLinesToGo.pop()
					assemblies[i].save(cur)
					assemblies.pop()
				i -= 1
			#print assyLinesToGo
		#See if in variant assembly
		if len(variantassemblies) > 0:
			variantassemblies[0].setPartId(currentPartId, sectionItemId, part.quantity)

	if minorModels != '' and year != -1 and modelsFound == False:
		findMinorModels(cur, minorModels, year)
		modelsFound = True

	lineNo += 1

def savePart(cur, part, variantstring, inassembly, assemblylevel, lineNo, sectionId, partId):
	try:
		query1 = 'insert into stockitem(partnumber, description) values(%s,%s)'
		values1 = (part.partNumber, part.description)
		cur.execute(query1, values1)
		id = cur.lastrowid
		query2 = 'insert into sectionitem(id, ref, altpartnumber, altManuPartnumber, altManuName, quantity, referenceonly, optional,      variantstring, isassembly, inassembly, assemblylevel, line, section_id, part_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		values2 = (id, part.refNumber, part.altPartNumber, part.altManuPartNumber, part.altManuName, part.quantity, part.referenceonly, part.optional, variantstring, part.isAssembly, inassembly, assemblylevel, lineNo, sectionId, partId)
#		query2 = 'insert into sectionitem(id, ref, partnumber, altpartnumber, altManuPartnumber, altManuName, description, quantity, referenceonly, optional,      variantstring, isassembly, inassembly, assemblylevel, line, section_id, part_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
#		values2 = (id, part.refNumber, part.partNumber, part.altPartNumber, part.altManuPartNumber, part.altManuName, part.description, part.quantity, part.referenceonly, part.optional, variantstring, part.isAssembly, inassembly, assemblylevel, lineNo, sectionId, partId)
		cur.execute(query2, values2)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def processPart(cur, lineNo, line):
	#print line.strip()
	part = Part(line)
	return part

def saveDirective(cur, directive, lineNo, sectionId):
	try:
#		print directive + '  ' + str(lineNo) + '  ' + str(sectionId)
		query = 'insert into sectionitem (directive, line, section_id) values (%s,%s,%s)'
		values = (directive, lineNo, sectionId)
		cur.execute(query, values)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def saveDirectiveWithValue(cur, directive, value, lineNo, sectionId):
	try:
#		print directive + '  ' + value + '  ' + str(lineNo) + '  ' + str(sectionId)
		query = 'insert into sectionitem (directive, directivevalue, line, section_id) values (%s,%s,%s,%s)'
		values = (directive, value, lineNo, sectionId)
		cur.execute(query, values)
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def findMinorModels(cur, minorModels, year):
	try:
		query = 'select id from model where name=%s and first_year=%s'
		for minorModel in minorModels:
			#print minorModel.strip()
			values = (minorModel.strip(), year)
			cur.execute(query, values)
			id = [r[0] for r in cur.fetchall()]
			minorModelIds.append(id[0])
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def findSection(cur, title, minorModelId):
	try:
		query = 'select s.id from section s join model_section ms on s.id=ms.section_id join model m on m.id=ms.model_id where m.id=%s and s.title=%s'
		values = (minorModelId, title)
		cur.execute(query, values)
		id = [r[0] for r in cur.fetchall()]
		#print title + ' : ' +  str(minorModelId) + ' : ' + str(id)
		return id[0]
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def findPart(cur, part):
	try:
		query = 'select p.id from stockitem p where p.partnumber=%s'
		values = (part)
#		query = 'select p.id from part p where p.partnumber=%s'
#		values = (part)
		cur.execute(query, values)
		id = [r[0] for r in cur.fetchall()]
		return id[0]
	except mdb.DataError, e:
		print e
	except mdb.Error, e:
		print e

def main(filename):
	global minorModels
	global year
	global title
	global modelsFound
	global minorModelIds
	global currentSectionId
	global currentPartId
	global lineNo
	global variantStrings
	global assemblyState
	minorModels = ''
	year = -1
	titleId = -1
	currentSectionId = -1
	currentPartId = -1
	modelsFound = False
	minorModelIds = []
	lineNo = 0
	variantStrings = []
	assyLinesToGo = []
	assemblies = []
	variantassemblies = []
	try:
		f = open(filename)
		conn = mdb.connect('localhost', 'root', 'password', 'msdb')
		cur = conn.cursor()
		while True:
			line = f.readline()
			if not line: break
			# Min line length of 2 to allow for CR/LF
			if len(line) > 2 and line[0] != '/' and line[0] != ' ' and line[0] != '\t':
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
