import json
import re
import threading
from time import sleep

import requests
from bs4 import BeautifulSoup

class AcmpParser():
    def __init__(self, children_ids):
        self.children_ids = children_ids
        
    def get_solvers(self, task_id) -> list:
        solvers = []
        
        for child_id in self.children_ids:
            page = requests.get(f'https://acmp.ru/?main=user&id={child_id}')
            page.encoding = 'windows-1251'
            soup = BeautifulSoup(page.text, 'html.parser')
            for e in soup.find('h4').parent.find('p').find_all('a'):
                task = int(e.contents[0])
                if (task_id == task):
                    solvers.append(child_id)
                    
        return solvers