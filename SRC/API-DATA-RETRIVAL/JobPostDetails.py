class JobPostDetails:
    'class for description of current post'
    #constructor
    def __init__(self, city_id, state_id, company_id, emp_form, work_manner, email):
        self.city_id = city_id
        self.state_id = state_id
        self.company_id = company_id
        self.emp_form = emp_form
        self.work_manner = work_manner
        self.email = email

    #toString
    def toString(self):
          return "JobPostDetails: " + "\n" + "city_id is: " + str(self.city_id) + "\n\n" + "state_id is: " + str(self.state_id) + "\n\n" + "company_id is: " + str(self.company_id) + "\n\n" + "emp_form is: " + str(self.emp_form) +"\n\n" + "work_manner is: " + str(self.work_manner) + "\n\n" + "email is: " + str(self.email)
