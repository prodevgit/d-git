import time
from constants import INDEX_PATH,OBJECT_PATH
import uuid

class DGitFile():

    def __init__(self ,fname=None ,index=None ,last_update=None, path=None, branch=None):
        self.fname = fname
        self.index = index
        self.last_update = last_update
        self.path = path
        self.branch = branch

    def save(self):
        index = str(uuid.uuid4())
        self.last_update = time.time()
        f = open(f'{OBJECT_PATH}/{self.path}/{self.fname}','wb+')


