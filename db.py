import MySQLdb as mdb
import sys

conn = None

try:
	conn = mdb.connect('localhost', 'root', 'password', 'msdb')
	cur = conn.cursor()
	cur.execute("select version()")
	data = cur.fetchone()
	print "Database version : %s " % data
	
	cur = conn.cursor()
	cur.execute("insert into part(part_number, description, alt_part_number, alt_part_manufacturer) values('12-1234', 'Some part', '123/456', 'Amal')")
	cur.execute("insert into part(part_number, description, alt_part_number, alt_part_manufacturer) values('22-1234', 'Some part', '123/456', 'Amal')")
	cur.execute("insert into part(part_number, description, alt_part_number, alt_part_manufacturer) values('32-1234', 'Some part', '123/456', 'Amal')")

except mdb.Error, e:
	print "Error occured...."
	sys.exit(1)
finally:
	if conn:
		conn.close()
