import asyncio
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from requests import Session
from bs4 import BeautifulSoup
from bs4.element import Tag

from config import config

class OnlinegdbError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class OnlinegdbLoginError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Assignment():    
    def __init__(self, id, active, session, not_submitted_count = 0, pending_count = 0, done_count = 0, name = None):
        self.id: int = id                   # Assignment id
        self.active = active
        
        self.name: str = name
        
        self.not_submitted_count: int = not_submitted_count
        self.pending_count: int = pending_count         
        self.done_count: int = done_count
        
        self.session: Session = session     # Onlinegdb Session
        
        self.submissions = list()           # {'name': str, 'id': int, 'done': bool, 'grade': int}
        self.done = list()
    
    def get_active_status(self) -> bool:
        return (self.not_submitted_count == 0 and self.pending_count == 0 and self.done_count == 0)
    
    def update_submissions(self):
        response = self.session.get(f'https://www.onlinegdb.com/t/as/{str(self.id)}/sub/evaluate')
        # If status code = OK!
        if (response.status_code != 200):
            raise OnlinegdbError(f'Service status code: {response.status_code}')
        # Clear submissions list
        self.submissions.clear()
        # Parse submissions table
        soup = BeautifulSoup(response.content, features="lxml")
        table = soup.find('table', attrs={'id':'submission_list'})
        if (table == None):
            return
        rows = table.find_all('tr')
        # Process rows and columns
        for row in rows:
            cols = row.find_all('td')
            if(len(cols)):
                sub_id = int(cols[0].find_all(href=True)[0].get('href').split('/')[-1])
                name = cols[0].text.replace('\n', '')
                cols = [ele.text.strip() for ele in cols]
                grade = cols[1].split(' ')
                done = grade[0] == grade[-1]
                if (grade[0] != 'Evaluating'):
                    self.submissions.append({'name': name, 
                                            'id': sub_id, 
                                            'done': done, 
                                            'grade': int(grade[0])})
        
    def update_done(self):
        response = self.session.get(f'https://www.onlinegdb.com/t/as/{str(self.id)}/view/submissionsdone')
        self.done.clear()
        soup = BeautifulSoup(response.content, features="lxml")
        table = soup.find('table', attrs={'id':'submission_list'})
        if (table == None):
            return
        # Parse submissions table
        soup = BeautifulSoup(response.content, features="lxml")
        table = soup.find('table', attrs={'id':'submission_list'})
        if (table == None):
            return
        rows = table.find_all('tr')
        # Process rows and columns
        for row in rows:
            cols = row.find_all('td')
            if(len(cols)):
                sub_id = int(cols[0].find_all(href=True)[0].get('href').split('/')[-1])
                name = cols[0].text.replace('\n', '')
                cols = [ele.text.strip() for ele in cols]
                grade = cols[1].split(' ')
                done = grade[0] == grade[-1]
                self.done.append(name)
        self.done_count = len(self.done)
        
    def review(self):
        self.update_submissions()
        for submission in self.submissions:
            if (submission['done']):
                self.session.post(f'https://www.onlinegdb.com/sub/status/{submission["id"]}', 
                                  data={'grade': submission['grade']})
    
class AutoOnlinegdb():    
    email = None                    # Teacher's account email
    password = None                 # Teacher's account password
    session = None                  # Request Session
        
    def __init__(self, classroom):
        self.classroom = classroom
        # Initialize session
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value]   
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        self.session = Session()
        self.session.headers = {"User-Agent": user_agent_rotator.get_random_user_agent()}
        # Login in account
        self.email = config.onlinegdb.email
        self.password = config.onlinegdb.password
        self.login()
        
    def login(self):
        response = self.session.post(url= "https://www.onlinegdb.com/login", 
                                 data={"email": self.email, "password": self.password, "login-submit": "Log In"})
        # If status code = OK!
        if (response.status_code != 200):
            raise OnlinegdbError(f'Service status code: {response.status_code}')
        # Check if logined in
        soup = BeautifulSoup(response.content, features="lxml")
        a = soup.find('a', attrs={'href': "/profile/"})
        if (a == None):
            raise OnlinegdbLoginError(f'Cannot login in account {self.email}')
        
    def get_assignments_on_evalute(self) -> list:
        response = self.session.get(url= f"https://www.onlinegdb.com/classroom/{self.classroom}")
        soup = BeautifulSoup(response.content, features="lxml")
        assignments = soup.find_all('li', attrs={'class': 'list-group-item col-sm-12'})
        result = list()
        for assignment in assignments:
            assignment: Tag = assignment
            assignment_id = assignment.get_attribute_list('data-id')[0]
            pending_for_evalution = assignment.find('a', attrs={'class': "btn btn-info btn-xs"})
            if pending_for_evalution == None:
                continue
            evalute_count = pending_for_evalution.text.split(' ')[0].replace('\n', '')
            # print(assignment_id, evalute_count)
            result.append(Assignment(int(assignment_id), True, self.session, pending_count=evalute_count))
        return result
    
    def get_assignments(self) -> list:
        response = self.session.get(url= f"https://www.onlinegdb.com/classroom/{self.classroom}")
        soup = BeautifulSoup(response.content, features="lxml")
        assignments = soup.find_all('li', attrs={'class': 'list-group-item col-sm-12'})
        result = list()
        for assignment in assignments:
            name = assignment.text.splitlines(False)[1]
            assignment: Tag = assignment
            assignment_id = assignment.get_attribute_list('data-id')[0]
            # print(assignment_id)
            # Get tasks buttons
            pending_for_evalution = assignment.find('a', attrs={'class': "btn btn-info btn-xs"})
            not_submitted = assignment.find('button', attrs={'class': "btn btn-warning btn-xs"})
            submission_done = assignment.find('button', attrs={'class': "btn btn-success btn-xs"})
            # If buttons dont exist
            if pending_for_evalution == None:
                result.append(Assignment(int(assignment_id), False, self.session, name=name))
                continue
            # Get text from buttons
            not_submitted_count = not_submitted.text.split(' ')[0].replace('\n', '')
            evalute_count = pending_for_evalution.text.split(' ')[0].replace('\n', '')
            done_count = submission_done.text.split(' ')[0].replace('\n', '')
            
            result.append(Assignment(int(assignment_id), 
                                     False, 
                                     self.session,
                                     int(not_submitted_count),
                                     int(evalute_count),
                                     int(done_count), 
                                     name=name))
        return result
            
# ao = AutoOnlinegdb(onlinegdb_login, onlinegdb_password)

# assigments = ao.get_assignments_on_evalute()

# for task in assigments:
#     task.review()

# assignments = ao.get_assignments()
# print('DOOOONE')

# from sheets.sheets import GradesSheet
# import time
  
# sheet = GradesSheet("1XXOskFsamnE0pK3fjQhXkVDmlfbBeNb9Ey23nTxXLlU")

# onlinegdb_table = sheet.get_onlinegdb_table()
    
# for assignment in assignments:
#     print(assignment.id)
#     if assignment.done_count > 0:
#         assignment.update_done()
#         if not onlinegdb_table.task_exist(assignment.id):
#             onlinegdb_table.add_task(assignment.id, assignment.name)
#         onlinegdb_table.set_grade(assignment.id, assignment.done)
#         time.sleep(2)
        