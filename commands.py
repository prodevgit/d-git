import os

from constants import DGIT_IGNORE, INDEX_PATH, OBJECT_PATH, TColors
from helper import multiple_find, get_file_index, diff_out
from models import DGitFile


class DGitCommand():

    def __init__(self):
        self.cwd = os.getcwd()
        with open(DGIT_IGNORE,'r') as ignore_file:
            self.ignore_ = ignore_file.read().splitlines()

    def init_repo(self):
        if not os.path.isdir('.dgit'):
            os.mkdir('.dgit')
            os.mkdir(OBJECT_PATH)
        registry = open(f'{INDEX_PATH}','wb')
        try:
            latest_index = registry.readlines()[-1]
        except:
            latest_index = 0
        registry.close()
        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(root,[dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    if os.path.isfile(f) and (filename.split('.')[1] not in [ext.replace('.','') for ext in self.ignore_]):
                        latest_index = latest_index+1
                        DGitFile(
                            fname=filename,
                            index=latest_index,
                            last_update=None,
                            path=f,
                            branch=None,
                            commit=None
                        ).save()

    def status(self):
        diff_data = []
        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(root,[dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    if os.path.isfile(f) and (filename.split('.')[1] not in [ext.replace('.','') for ext in self.ignore_]):
                        diff_data.append(DGitFile(
                            fname=filename,
                            path=f
                        ).check_diff())
        print('Changes')
        for data in diff_data:
            if data['status'] == True:
                print(f"{TColors.DIFF}{data['data']}")

    def stash(self):
        diff_data = []
        revert_data = []
        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(root, [dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    if os.path.isfile(f) and (
                            filename.split('.')[1] not in [ext.replace('.', '') for ext in self.ignore_]):
                        diff_data.append(DGitFile(
                            fname=filename,
                            path=f
                        ).check_diff())
        for data in diff_data:
            if data['status'] == True:
                revert_data.append(data['data'])
        if revert_data:
            for revert in revert_data:
                with open(revert,'wb') as source_file:
                    with open(f'{OBJECT_PATH}/{get_file_index(revert)}/content') as object_copy:
                        for line in object_copy:
                            source_file.write(bytes(line,'utf-8'))

    def diff(self):
        diff_data = []
        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(root, [dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    if os.path.isfile(f) and (
                            filename.split('.')[1] not in [ext.replace('.', '') for ext in self.ignore_]):
                        diff_data.append(DGitFile(
                            fname=filename,
                            path=f
                        ).check_diff())
        print('Changes')
        for data in diff_data:
            if data['status'] == True:
                print(f'\n\n{TColors.WHITE}{data["data"]}')
                formatted_out = diff_out(data['data'])
                for line in formatted_out:
                    print(line)