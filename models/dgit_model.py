import hashlib
import os
import time
from constants import INDEX_PATH,OBJECT_PATH
import uuid
# from helper import write_index, get_file_id
from helper import get_file_index
from serializer import FileSerializer


class DGitFile():

    def __init__(self ,fname=None ,index=None ,last_update=None, path=None, branch=None, commit=None, created=None, integrity=None):
        self.fname = fname
        self.index = index
        self.last_update = last_update
        self.path = path
        self.branch = branch
        self.commit = commit
        self.created = created
        self.integrity = integrity

    def save(self):
        sha256 = hashlib.sha256()

        #check for existing file
        if self.last_update:
            # fid = get_file_id(self.path)
            # f_object = open(f'{OBJECT_PATH}/{fid}', 'rb')
            # data = 'get hash'
            # sha256.update(data)
            # start_integrity = sha256.hexdigest()
            # f_file = open(f'{self.path}', 'rb')
            # data = 'get hash'
            # sha256.update(data)
            # end_integrity = sha256.hexdigest()
            # if start_integrity == end_integrity:
            #     pass
            # else:
            #     self.commit = str(uuid.uuid4())
            #     self.last_update = time.time()
            #     write_index(self.fid, self.branch, self.commit)
            #     f_object
            pass
        else:
            file = open(f'{self.path}', 'rb')
            data = file.read()
            # sha256.update(data)
            # self.integrity = sha256.hexdigest()
            self.integrity = hashlib.md5(data).hexdigest()
            self.last_update = time.time()
            file.close()
            index_file = open(f'{INDEX_PATH}','ab')
            index_file.write(bytes(f'{self.index}={self.path}\n',encoding='utf8'))
            index_file.close()
            if not os.path.isdir(f'{OBJECT_PATH}/{index_file}'):
                os.mkdir(f'{OBJECT_PATH}/{self.index}/')
            object_file = open(f'{OBJECT_PATH}/{self.index}/descriptor','wb+')
            for key,value in self.__dict__.items():
                object_file.write(bytes(f'{key}={value}\n', encoding='utf8'))
            with open(self.path) as source_file:
                with open(f'{OBJECT_PATH}/{self.index}/content', 'wb+') as object_copy:
                    for line in source_file:
                        object_copy.write(bytes(line,'utf8'))
            object_file.close()


    def check_diff(self):
        diff = dict()
        diff['data'] = dict()
        diff['status'] =False
        sha256 = hashlib.sha256()
        index = get_file_index(self.path)
        index_file = open(f'{OBJECT_PATH}/{index}/descriptor', 'rb')
        serializer = FileSerializer(index_file)
        self.last_update = serializer.last_update
        if self.last_update:
            index = get_file_index(self.path)
            index_file = open(f'{OBJECT_PATH}/{index}/descriptor', 'rb')
            start_integrity  = serializer.integrity.split('\n')[0]
            file = open(f'{self.path}', 'rb')
            data = file.read()
            end_integrity = hashlib.md5(data).hexdigest()
            if start_integrity == end_integrity:
                diff['status'] = False
            else:
                diff['status'] = True
                diff['data'] = self.path

        return diff



