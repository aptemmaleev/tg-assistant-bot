import re

import gspread

from gspread.exceptions import WorksheetNotFound
from gspread.spreadsheet import Spreadsheet, Worksheet
from gspread.client import Client
from gspread_formatting import *

from .table import table
from .counter import add_char

worksheet_name = 'AutoGrades'

class Table():
    __worksheet: Worksheet
    
    __logins_list: list
    __children_dict: dict
    
    __tasks_list: list
    __tasks_dict: dict
    
    def __init__(self, worksheet, position):
        self.__worksheet = worksheet
        print('NEW')
        self.__logins_list = []
        self.__children_dict = {}
        self.__tasks_list = []
        self.__tasks_dict = {}
        
        self.column = re.findall(r'[a-zA-Z]+', position)[0]
        self.row = int(re.findall(r'\d+', position)[0])
        
        # Parse children and their logins
        childrens = self.__worksheet.get_values(f'{self.column}{str(self.row + 2)}:{chr(ord(self.column) + 4)}{str(self.row + 31)}')
        if (len(childrens) > 2):   
            for child in childrens:
                self.__children_dict[child[2]] = {'id': child[0], 'name': child[1]}
                self.__logins_list.append(child[2])
        else:
            return None
        
        # Parse tasks with grades
        tasks = self.__worksheet.get_values(f'{chr(ord(self.column) + 5)}{str(self.row + 1)}:ALL{str(self.row + 31)}')
        if (len(tasks) == 0):
            return
        for i in range(len(tasks[0])):
            self.__tasks_dict[int(tasks[0][i])] = []
            self.__tasks_list.append(int(tasks[0][i]))
            for j in range(1, len(tasks)):
                if (tasks[j][i]) == '1':
                    self.__tasks_dict[int(tasks[0][i])].append(self.__logins_list[j - 1])
        
    # Task exist
    def task_exist(self, id):
        if (id in self.__tasks_list):
            return True
        return False
    
    def get_logins_list(self):
        return self.__logins_list
    
    # Add task
    def add_task(self, id, name = None):
        column = add_char(self.column, 5 + len(self.__tasks_list))
        row = self.row + 1
        self.__worksheet.update(f'{column}{row}', str(id))
        if (name != None):
            self.__worksheet.insert_note(f'{column}{row}', name)
            print(name)
        self.__tasks_dict[int(id)] = []
        self.__tasks_list.append(id)

    # Set grades
    def set_grade(self, id, logins_of_solvers, name = ''):
        if (not id in self.__tasks_dict.keys()):
            self.add_task(id, name)
        print(id)
        print(logins_of_solvers)
        # Check differents between solvers
        before_solvers = self.__tasks_dict[id]
        new_solvers = list(set(logins_of_solvers)-set(before_solvers))
        if (new_solvers == 0):
            return
        # Creating new solver list
        new_solvers = list(set(logins_of_solvers) | set(before_solvers))
        write_solvers = []
        # Make rows in columns
        for i in range(len(self.__logins_list)):
            write_solvers.append([])
        # Add grades
        for login in new_solvers:
            if login in self.__logins_list:
                write_solvers[int(self.__children_dict[login]['id']) - 1].append(1)
        # Write to sheets
        column = add_char(self.column, 5 + self.__tasks_list.index(id))
        row = self.row + 2
        self.__worksheet.update(f'{column}{row}', write_solvers)

class GradesSheet():
    __client: Client = None
    __spreadsheet: Spreadsheet = None
    __worksheet: Worksheet = None

    __onlinegdb: Table
    __acmp: Table
    __codeforces: Table
    
    def __init__(self, key):
        self.__client = gspread.service_account('data\service_account.json')
        self.__spreadsheet = self.__client.open_by_key(key)
        self.__worksheet = self.get_worksheet(worksheet_name)
        
        self.__onlinegdb: Table = None
        self.__acmp: Table = None
        self.__codeforces: Table = None
                
    def get_worksheet(self, name) -> Worksheet:
        try:
            return self.__spreadsheet.worksheet(name)
        except WorksheetNotFound as e:
            worksheet = self.__spreadsheet.add_worksheet(name, 1000, 1000)
            # Set column width
            set_column_widths(worksheet, [('B:C', 50), ('D', 20), ('E', 250), ('F', 150), ('G:H', 100)])
            # Configuration cells
            worksheet.format('A2', {"textFormat": {"bold": True}})
            worksheet.format('A1:ALL150', {"horizontalAlignment": "CENTER"})
            # Headers cells

            worksheet.merge_cells('D2:H2')
            worksheet.merge_cells('D35:H35')
            worksheet.merge_cells('D68:H68')
            worksheet.merge_cells('D101:H101')
            
            worksheet.format(['D2:H2', 'D35:H35', 'D68:H68', 'D101:H101'], {"horizontalAlignment": "CENTER", "textFormat": {"bold": True}, "backgroundColor": {"red": 170.5,"green": 170.5,"blue": 280.5}})
            worksheet.format(['D36:ALL36', 'D3:ALL3', 'D69:ALL69', 'D102:ALL102'], {"horizontalAlignment": "CENTER", "textFormat": {"bold": True}})
            
            worksheet.update('A1', table, raw=False)
            return worksheet
            
    def get_onlinegdb_table(self) -> Table:
        if (self.__onlinegdb == None):
            self.__onlinegdb = Table(self.__worksheet, self.__worksheet.get_values('B7')[0][0])
        return self.__onlinegdb
    
    def get_acmp_table(self) -> Table:
        if (self.__acmp == None):
            self.__acmp = Table(self.__worksheet, self.__worksheet.get_values('B8')[0][0])
        return self.__acmp
    
    def get_codeforces_table(self) -> Table:
        if (self.__codeforces == None):
            self.__codeforces = Table(self.__worksheet, self.__worksheet.get_values('B9')[0][0])
        return self.__codeforces
    
    def get_title(self) -> str:
        return self.__spreadsheet.title
    
    
        
# sheet = GradesSheet("1zG8XczLuXrF7ObB5-BRk-7LCVsdhvvgAqpm5PaVMFa0")

# onlinegdb = sheet.get_onlinegdb_table()
# print(onlinegdb.task_exist(1111))
# if not onlinegdb.task_exist(1111):
#     onlinegdb.add_task(1111)
# else:
#     print('exist')