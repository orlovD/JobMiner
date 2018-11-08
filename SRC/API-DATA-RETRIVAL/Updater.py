

from Parser import Parser
from JobPostDetails import JobPostDetails

import json
import pymysql
import unicodedata
		
global DB_Conn
global parser	
global cur


class Updater:
 
	""" Obj to update DB """
	
	
#========================================================================================		
		
	def __init__(self, db_conn):
		global DB_Conn
		global parser	
		global cur	
	
		DB_Conn = db_conn;
		parser = Parser(db_conn)
		cur = db_conn.cursor()
		
		
#=============================================================================================		

	
	def UpdatePost(self, DictPostJson, facebook_group_id):
		global DB_Conn
		global parser	
		global cur	
		
		
		
		try:
			message = unicodedata.normalize('NFKD', DictPostJson['message']).encode('ascii','ignore')
		
		except KeyError:
			return
		
		
		JP_Details = parser.parse(message)
		
		post_id = self.Update_JobPost(JP_Details, DictPostJson)
		
		self.Update_JobPostGroup(post_id, facebook_group_id)
		self.Update_JobPostCompany(post_id, JP_Details)
		self.Update_JobPostCity(post_id, JP_Details)
		self.Update_JobPostState(post_id, JP_Details)
				
		
#=============================================================================================		
		
		
	def Update_JobPost(self, JP_Details, DictPostJson):
		global DB_Conn
		global parser	
		global cur	
		

		#The post id taken from facebook
		post_story_id = unicodedata.normalize('NFKD', DictPostJson['id']).encode('ascii','ignore') 
		
		publish_date = unicodedata.normalize('NFKD', DictPostJson['created_time']).encode('ascii','ignore')
		
		
		employment_form = JP_Details.emp_form   #full-time / part-time / temp
		working_manner = JP_Details.work_manner #home/ company_or_unspecified
		email = JP_Details.email
		
		full_post_body = unicodedata.normalize('NFKD', DictPostJson['message']).encode('ascii','ignore')


		#cur.execute("SELECT COUNT(*) FROM JobPost WHERE post_story_id = \'" + post_story_id + "\'")
		#num = cur.fetchone();
		
		
		cur.execute("SELECT post_id FROM JobPost WHERE post_story_id = \'" + post_story_id + "\'")
		post_id = cur.fetchone();
		
		
		if(post_id == None):	

			if(employment_form != None):
				emp_str1 = ", employment_form"
				emp_str2 = ",\'" +str(employment_form) + "\'"
			else:
				emp_str1 = ""
				emp_str2 = ""
				
				
			if(working_manner != None):
				work_str1 = ", working_manner"
				work_str2 = ",\'" +str(working_manner) + "\'"  		
			else:
				work_str1 = ""
				work_str2 = ""  
				
				
			if(email != None):
				email_str1 = ", email"
				email_str2 = ",\'" +str(email) + "\'"	
			else:
				email_str1 = ""
				email_str2 = ""
			
			
			cur.execute("INSERT INTO JobPost (post_story_id, publish_date" + emp_str1 + work_str1 + email_str1 +", full_post_body) VALUES (\'" + 
			post_story_id + "\',\'" + 
			publish_date + "\'" + 
			emp_str2 + 
			work_str2 + 
			email_str2 
			+",\'" + pymysql.escape_string(full_post_body) + "\')")
			
			cur.execute("SELECT post_id FROM JobPost WHERE post_story_id = \'" + post_story_id + "\'")
			post_id = cur.fetchone();
			

		"""else:
				
			if(employment_form != None):
				employment_form_str = ",employment_form=\'" + str(employment_form) + "\'"		
			else:
				employment_form_str = ""
				
				
			if(working_manner != None):
				working_manner_str = ",working_manner=\'" + str(working_manner) + "\'"    		
			else:
				working_manner_str = ""
				
				
			if(email != None):
				email_str = ",email=\'" + str(email) + "\'"	
			else:
				email_str = ""
				
			
			
			print("UPDATE JobPost SET post_story_id=\'" + str(post_story_id) +
				"\',publish_date=\'" + str(publish_date) + employment_form_str + working_manner_str + email_str +
				",full_post_body=\'" + pymysql.escape_string(full_post_body) + 
				"\' WHERE post_id=\'" + str(post_id[0]) + "\'")
			
			
			
			
			cur.execute("UPDATE JobPost SET post_story_id=\'" + str(post_story_id) +
				"\',publish_date=\'" + str(publish_date) + employment_form_str + working_manner_str + email_str +
				",full_post_body=\'" + (pymysql.escape_string(full_post_body)).replace("\/", "\\\/") + 
				"\' WHERE post_id=\'" + str(post_id[0]) + "\'" )	"""
				

			 
		return (post_id[0])
	
	
		
#=============================================================================================		


	def Update_JobPostGroup(self, post_id, facebook_group_id):
		global DB_Conn
		global parser	
		global cur	
			
		cur.execute("SELECT group_id FROM Groups WHERE group_fb_id = \'" + str(facebook_group_id) + "\'");
		group_id =cur.fetchone()[0];
		cur.execute("SELECT post_id FROM JobPostGroup WHERE post_id = \'" + str(post_id) + "\'")
		post_id_fetch = cur.fetchone();
		

		if(post_id_fetch == None):	
			cur.execute("INSERT INTO JobPostGroup (post_id, group_id) VALUES (\'" + str(post_id) + "\',\'" + str(group_id) + "\')")
		
		"""else:
			cur.execute("UPDATE JobPostGroup SET group_id=\'" + str(group_id) + "\' WHERE post_id=\'" + str(post_id) + "\'" )"""
		
		
#=============================================================================================		

	
	def Update_JobPostCompany(self, post_id, JP_Details):
		global DB_Conn
		global parser	
		global cur	
			
		company_id = JP_Details.company_id
		
		cur.execute("SELECT post_id FROM JobPostCompany WHERE post_id = \'" + str(post_id) + "\'")
		post_id_fetch = cur.fetchone();
		

		if( (post_id_fetch == None) and (company_id != None) and (company_id != 0) ):	
			cur.execute("INSERT INTO JobPostCompany (post_id, company_id) VALUES (\'" + str(post_id) + "\',\'" + str(company_id) + "\')")
		
		"""else:
			cur.execute("UPDATE JobPostCompany SET company_id=\'" + str(company_id) + "\' WHERE post_id=\'" + str(post_id) + "\'" )"""
			
	
#=============================================================================================		

		
	def Update_JobPostCity(self, post_id, JP_Details):
		global DB_Conn
		global parser	
		global cur	
			
		city_id = JP_Details.city_id 

		cur.execute("SELECT post_id FROM JobPostCity WHERE post_id = \'" + str(post_id) + "\'")
		post_id_fetch = cur.fetchone();
		

		if( (post_id_fetch == None) and (city_id != None) ):	
			cur.execute("INSERT INTO JobPostCity (post_id, city_id) VALUES (\'" + str(post_id) + "\',\'" + str(city_id) + "\')")
		
		"""else:
			cur.execute("UPDATE JobPostCity SET city_id=\'" + str(city_id) + "\' WHERE post_id=\'" + str(post_id) + "\'" )"""


#=============================================================================================		
	
	
	def Update_JobPostState(self, post_id, JP_Details):
		global DB_Conn
		global parser	
		global cur	
		
		state_id = JP_Details.state_id
	
		cur.execute("SELECT post_id FROM JobPostState WHERE post_id = \'" + str(post_id) + "\'")
		post_id_fetch = cur.fetchone();
		

		if( (post_id_fetch == None) and (state_id != None) ):	
			cur.execute("INSERT INTO JobPostState (post_id, state_id) VALUES (\'" + str(post_id) + "\',\'" + str(state_id) + "\')")
		
		"""else:
			cur.execute("UPDATE JobPostState SET state_id=\'" + str(state_id) + "\' WHERE post_id=\'" + str(post_id) + "\'" )"""
	
	
	
#=============================================================================================			
	

	
	
	
	
	
		
		
