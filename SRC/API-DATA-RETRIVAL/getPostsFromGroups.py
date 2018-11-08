#!/usr/bin/python

import pymysql as mdb
from JobPostDetails import JobPostDetails
from datetime import datetime, timedelta
import urllib
import urllib2
import pprint
import json
from Updater import *
from Parser import Parser
DEBUG = True
count = 0
ACCESS_TOKEN='EAAOoVLA1RdUBAIDY2WwedUx8c1SEjxYAL32jNPceEENN3kZC0xZBxzVpDkZAZARn8vy2X8eVJ6C9bOeF20wZBGirNRG6ASQrXOROvVSWHMkkAEY9i9GXaDGJln9rVm7wNJDbaY5Qulj5khymZBE6JnZBD8BgRSqff4ZD'        


global upd


def startUpdate():
	global count
	global upd
	
	 		
	con = mdb.connect(host="mysqlsrv.cs.tau.ac.il", user="DbMysql15", passwd="DbMysql15", db="DbMysql15",autocommit=True)
	
	upd = Updater(con)
	
	with con:
	    	cur = con.cursor()    
	    	cur.execute("SELECT group_fb_id, group_id FROM Groups")
	    	ls = cur.fetchall()
			
	    	for row in ls:
				gfid = row[0]
				gid = row[1]
				getGroupFeed(gfid)
				cur.execute("UPDATE Groups SET update_date = ( SELECT MAX(publish_date) FROM JobPost,JobPostGroup WHERE JobPost.post_id = JobPostGroup.post_id AND JobPostGroup.group_id = " + str(gid) + ")" + " WHERE Groups.group_id = " + str(gid))
					
				
		
	if DEBUG:
		#print count
		print gid

def getGroupFeed(group_id):
	if DEBUG:
		print group_id
	#gets jsons chunks and passes them to getPosts() which will pass the posts to UpdatePost()
	
	url = 'https://graph.facebook.com/v2.6/'+group_id+'/feed?fields=message,created_time,id&since='
	#get date 2 months back:
	TwoDaysBack = datetime.now()-timedelta(days=2)
	sinceDate = str(TwoDaysBack.year)+'-'+str(TwoDaysBack.month)+'-'+str(TwoDaysBack.day)
	url += 	sinceDate + '&access_token='+ACCESS_TOKEN
	resp = urllib2.urlopen(url)
	#open the URL and read the response
	the_page = resp.read()

	getPosts(the_page, group_id)
	jsonDict = json.loads(the_page)
	while (len(jsonDict['data']) > 0):  #while the dictionary is not empty
		
		nextUrl = jsonDict['paging']['next']
		resp = urllib2.urlopen(nextUrl)
		the_page = resp.read()
		getPosts(the_page, group_id)
		jsonDict = json.loads(the_page)	
		if DEBUG:
			print nextUrl	

def getPosts(jsonChunk,group_id):

	global upd	
	jsonDict = json.loads(jsonChunk)
	for post in jsonDict['data']:
		upd.UpdatePost(post, group_id)
		
	
def mainDebug():

	global upd
	con = mdb.connect(host="mysqlsrv.cs.tau.ac.il", user="DbMysql15", passwd="DbMysql15", db="DbMysql15" , autocommit=True)
	
	upd = Updater(con)
	getGroupFeed('626511234087342')
	getGroupFeed('694416243907967')	
	
'''
if __name__ == "__main__":
    main()
   '''
    
    
    
    
    
    
    
    
    
    
    

