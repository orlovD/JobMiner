from JobPostDetails import JobPostDetails
import re
import string

class Parser:
    'class for parsing messages of posts'
    #dictionary for cities
    cities = {}
    #dictionary for states
    states = {}
    #dictionary for companies
    companies = {}
    
    #constructor
    def __init__(self, conn):
        #get query stream
        cur = conn.cursor()
        #get city list from DB
        cur.execute("SELECT city_id, city_name FROM Cities")
        #fill city dictionary
        self.fillDictionaryWithDBData(cur, self.cities)
        #get state list from DB
        cur.execute("SELECT state_id, state_name FROM States")
        #fill state dictionary
        self.fillDictionaryWithDBData(cur, self.states)
        #get company list from DB
        cur.execute("SELECT company_id, company_name FROM Companies")
        #fill company dictionary
        self.fillDictionaryWithDBData(cur, self.companies)
        #close query stream
        cur.close()     
        
    #fill dictionary with data from DB
    def fillDictionaryWithDBData(self, db_data, dictionary):
        for row in db_data:
            #get id from tuple
            _id = row[0]
            #get name from tuple
            _name = row[1].lower()
            #add to dictionary key: _name, value: _id
            #for each _id there can be more than one _name
            dictionary[_name] = _id

    #split message from facebook post into list of words
    def stringToList(self, message):
        #list of stripped words
        return [word.strip(string.punctuation) for word in message.split()]

    #receives message and word to look for
    #returns index of a word if found
    #otherwise returns -1
    def findWordIndex(message, word):
        message_to_lower = message.lower()
        index = message_to_lower.find(word)
        if(index == -1):
            print(word + " is not found")
        else:
            print(word + " found at index " + str(index))
        return index

    #search message for presense of any names from dictionary
    #if name is present in the message - get it id
    def findIdByName(self, message, dictionary):
        found_name = None
        found_id = None
        for name in dictionary:
            name_w_spaces = " " + name.lower()
            #if name is found
            if(message.lower().find(name_w_spaces) != -1):
                #get name
                found_name = name
                #get id for found name
                found_id = dictionary[name]
                #exit loop
                break
        return (found_name, found_id)

    #search dictionary for presense of any words from splitted message
    #return dictionary entry if it's present
    def findInDictionary(self, word_list, dictionary):
        found_name = None
        found_id = None
        found = 0
        for i in range(len(word_list) - 2):
            triple_key = word_list[i] + " " + word_list[i+1] + " " + word_list[i+2]
            if triple_key.lower() in dictionary:
                #get name
                found_name = triple_key
                #get id for found name
                found_id = dictionary[triple_key.lower()]
                found = 1
                return (found_name, found_id)
        for i in range(len(word_list) - 1):
            double_key = word_list[i] + " " + word_list[i+1]
            if double_key.lower() in dictionary:
                #get name
                found_name = double_key
                #get id for found name
                found_id = dictionary[double_key.lower()]
                return (found_name, found_id) 
        for word in word_list:
            if word.lower() in dictionary:
                #get name
                found_name = word
                #get id for found name
                found_id = dictionary[word.lower()]
                return (found_name, found_id)
            
    #search message for presense of employment form
    #returns 0 if not found and 1 or 2 if found
    def findEmploymentForm(self, message):
        #int for employment form
        found_employment_form = 0
        #if work manner is found
        if(message.lower().find(" part") != -1):
                #get work manner
                found_employment_form = 1
        else:
            if(message.lower().find(" temp") != -1):
                #get work manner
                found_employment_form = 2
        return found_employment_form

    #search message for presense of work manner description
    #returns 0 if not found and 1 if found
    def findWorkManner(self, message):
        #bool for work manner
        found_work_manner = 0
        #if work manner is found
        if(message.lower().find(" home") != -1):
                #get work manner
                found_work_manner = 1
        return found_work_manner

    #search message for presense of any e-mails
    #if e-mail is present in the message - get it
    def findEmail(self, message):
        found_email = None
        match = re.search(r'[\w\.-]+@[\w\.-]+', message)
        if(match != None):
            found_email = match.group(0)
        return found_email

    #main function of a Parser
    #JobPostDetails parser.parse(message)
    #receives a message from post in string format
    #returns object of type JobPostDetails 
    
    def parse(self, message):
        #initialize fields to look for
        found_city = None
        found_city_id = None
        found_state = None
        found_state_id = None
        found_company = None
        found_company_id = None
        found_employment_form = 0
        found_work_manner = 0
        found_email = None

        word_list = self.stringToList(message)

        #try to find known city - take first found
        #city_name_to_id = self.findIdByName(message, self.cities)
        city_name_to_id = self.findInDictionary(word_list, self.cities)
        
        if(city_name_to_id != None):
	        found_city = city_name_to_id[0]
        	found_city_id = city_name_to_id[1]
	

        #try to find known state - take first found
        state_name_to_id = self.findInDictionary(word_list, self.states)
        
        if(state_name_to_id != None):
			found_state = state_name_to_id[0]
			found_state_id = state_name_to_id[1]


        #try to find known company - take first found
        company_name_to_id = self.findIdByName(message, self.companies)
        
        if(company_name_to_id != None):
			found_company = company_name_to_id[0]
			found_company_id = company_name_to_id[1]

    	#try to find employment form - take first found
        found_employment_form = self.findEmploymentForm(message)
        
	#try to find contact working manner - take first found
        found_work_manner = self.findWorkManner(message)

        #try to find e-mail - take first found
        found_contact_email = self.findEmail(message)

        #debug
        #print("found city: " + str(found_city))
        #print("found city id: " + str(found_city_id))

        #print("found state: " + str(found_state))
        #print("found state id: " + str(found_state_id))
        
        #print("found company: " + str(found_company))
        #print("found company id: " + str(found_company_id))

        #print("found employment form: " + str(found_employment_form))

        #print("found working manner: " + str(found_work_manner))

        #print("found contact e-mail: " + str(found_contact_email))

        #print("\n\n")

        

        #create instance of JobPostDetails
        post_details = JobPostDetails(found_city_id, found_state_id, found_company_id, found_employment_form, found_work_manner, found_contact_email)
        ##print JobPostDetails found
        #print(post_details.toString())

        #return JobPostDetails
        return post_details
