__metaclass__ = type	#To ensure use of new class type

import MySQLdb as mdb

class VariantAssembly:
	
	def __init__(self):
		self.varAssyRef = 0
		self.variants = {}
		self.state = 0
		self.currentVariantLabel = ''
		
	def setVariant(self, variant):
		self.variants[variant] = []
		self.currentVariantLabel = variant
		self.state = 1
		
	def setIn(self, variant):
		self.currentVariantLabel = variant
		self.state = 2

	def setCommon(self):
		self.state = 3
		self.currentVariantLabel = ''

	def setPartId(self, partId, sectionItemId, quantity):
		spec = (partId, sectionItemId, quantity)
		if self.state == 1:
			#Note that first id will be that of assembly itself
			self.variants[self.currentVariantLabel].append(spec)
			self.state = 0
		elif self.state == 2:
			self.variants[self.currentVariantLabel].append(spec)
		elif self.state == 3:
			for key in self.variants:
				self.variants[key].append(spec)

	def save(self, cur):
		try:
			query = 'select max(variant_tag) from assemblypart'
			cur.execute(query)
			tag = cur.fetchone()[0]
			if tag == None:
				tag = 1
			else:
				tag += 1			
			for key in self.variants:
				assemblyPartId = self.variants[key][0][0]
				assemblySectionItemId = self.variants[key][0][1]
				iteration = 0
				for spec in self.variants[key]:
					if iteration > 0:
						query = 'insert into assemblypart(assembly_part_id, part_id, assembly_sectionitem_id, sectionitem_id, quantity, variant_tag, variant_label) values (%s,%s,%s,%s,%s,%s,%s)'
						values = (assemblyPartId, spec[0], assemblySectionItemId, spec[1], spec[2], tag, key)
						cur.execute(query, values)
					iteration += 1
		except mdb.DataError, e:
			print e
		except mdb.Error, e:
			print e
			
			
			
			
			