__metaclass__ = type	#To ensure use of new class type

import MySQLdb as mdb

class Assembly:
	
	def __init__(self, partId, sectionItemId):
		self.assemblyPartId = partId
		self.assemblySectionItemId = sectionItemId
		self.componentIds = []

	def add(self, partId, sectionItemId, quantity):
		spec = (partId, sectionItemId, quantity)
		self.componentIds.append(spec)
		#print 'Assembly ' + str(len(self.componentIds))

	def save(self, cur):
		try:			
			for spec in self.componentIds:
				query = 'insert into assemblypart(assembly_part_id, part_id, assembly_sectionItem_id, sectionItem_id, quantity) values (%s,%s,%s,%s,%s)'
				values = (self.assemblyPartId, spec[0], self.assemblySectionItemId, spec[1], spec[2])
				cur.execute(query, values)
		except mdb.DataError, e:
			print e
		except mdb.Error, e:
			print e
