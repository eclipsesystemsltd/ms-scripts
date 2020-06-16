__metaclass__ = type	#To ensure use of new class type

class Part:
	
	def __init__(self, line):
		self.processLine(line)
	
	def processLine(self, line):
#		print line
		self.refNumber = None
		self.partNumber = None
		self.altPartNumber = None
		self.altManuPartNumber = None
		self.altManuName = None
		self.description = None
		self.quantity = None
		self.referenceonly = False
		self.optional = False
		self.isAssembly = False
		self.assemblyLines = 0
		self.assemblyComponents = 0
		#Split line into fields as first pass
		elements = line.split()		
		#Get reference number
		if elements[0] != '--':
			self.refNumber = elements[0].strip()
#			print self.refNumber
		#Get part number
		if elements[1] != '-------':
			self.partNumber = elements[1].strip()
#			print self.partNumber
		#Get description
		desc = line[11:]
		endOfLine = len(desc)
		specialChars = ["*","$","#","~","^","`","\\"]
		for char in specialChars:
			position = desc.find(char)
			if position < endOfLine and position > -1:
				endOfLine = position
		self.description = desc[0:endOfLine].strip()
#		print self.description
		#Get quantity
		position = line.find('$')
		quantityPosition = position
		if position > -1:
			str = line[position + 1:]
			elements = str.split()
			self.quantity = elements[0]
#			print self.quantity
		#Get assembly information
		position = line.find('#')
		if position > -1:
			str = line[position:]
			elements = str.split()
			res = self.processAssembly(elements[0])
			self.assemblyLines = res[0]
			self.assemblyComponents = res[1]
			self.isAssembly = True
#			print str(self.assemblyLines) + "   " + str(self.assemblyComponents)
		#Get alternative manufacturer information
		position = line[1:].find('*')
		if position < quantityPosition and position > -1:
			str = line[position + 2:]
			elements = str.split()
			altManuInfo = elements[0].split('_')
			self.altManuName = altManuInfo[0].strip()
			self.altManuPartNumber = altManuInfo[1].strip()
#			print self.altManuName + "   " + self.altManuPartNumber
		#Get reference only information
		position = line.find('~reference_only')
		if position < quantityPosition and position > -1:
			self.referenceonly = True
#			print "Reference only item found"
		#Get alternative information
		position = line.find('^alternative_')
		if position < quantityPosition and position > -1:
			str = line[position + 13:]
			elements = str.split()
			self.altPartNumber = elements[0].strip()
#			print self.altPartNumber
		#Get long part number information
		position = line.find('`')
		if position < quantityPosition and position > -1:
			str = line[position + 1:]
			elements = str.split()
			self.partNumber = elements[0].strip()
#			print self.partNumber
		#Get optional information
		position = line.find('\\optional')
		if position < quantityPosition and position > -1:
			self.optional = True
#			print "Optional item found"

	def processAssembly(self, assyStr):
		# Eg #3@3+ or #2+
		elements = assyStr[1:].split('@')
		re = []
		if len(elements) == 1:
			res = self.processAssyLineCountShort(elements[0])
		else:
			res = self.processAssyLineCount(assyStr[1:])
		return res
	
	def processAssyLineCount(self, str):
		# Eg 3@3+ or 3@4-
		lth = len(str);
		elements = str.split('@')
		lines = int(elements[0])
		if str[lth - 1] == '-':
			lines += 1
		components = self.processAssyLineCountShort(elements[1])	
		return [lines, components[1]]
		
	def processAssyLineCountShort(self, str):
		# Eg 2+ or 10-
		lth = len(str);
		components = int(str[0:lth - 1])
		lines = components
		if str[lth - 1] == '-':
			lines += 1
		return [lines, components]
	
		
			
		
		
		
