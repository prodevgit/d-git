import os

from constants import DGIT_IGNORE, INDEX_PATH, OBJECT_PATH, TColors, HEAD, BRANCH_REF
from helper import multiple_find, get_file_index, diff_out
from models import DGitFile
from network import push, checkout, clone


class DGitCommand():

    def __init__(self):
        self.cwd = os.getcwd()
        with open(DGIT_IGNORE,'r') as ignore_file:
            self.ignore_ = ignore_file.read().splitlines()

    def init_repo(self):
        if not os.path.isdir('.dgit'):
            os.mkdir('.dgit')
            os.mkdir(OBJECT_PATH)
            os.mkdir(BRANCH_REF)
        registry = open(f'{INDEX_PATH}','wb')
        with open(HEAD,'wb+') as head:
            head.write(b'')
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

    def clone(self,repository,clone_by,token):
        print(clone(repository,clone_by,token))

    def branch(self):

        print(self.get_head())



    def status(self):
        diff_data = []
        indices,all_files,file_state,indexed_files = self.diff_files()
        for file in indexed_files:
            diff_data.append(DGitFile(
                fname=file['name'],
                path=file['path']
            ).check_diff())
        print('Changes')
        for data in diff_data:
            if data['status'] == True:
                print(f"{TColors.DIFF}{data['data']}")

        print(f"{TColors.WHITE}Files added")
        print("-----------")
        for file in file_state:
            if file['status'] == 'added':
                print(f"{TColors.OKGREEN}{file['file']}")

        print(f"{TColors.WHITE}Files deleted")
        print("-------------")
        for file in file_state:
            if file['status'] == 'deleted':
                print(f"{TColors.DIFF}{file['file']}")


    def add(self,path):
        self.diff_files()

    def stash(self):
        diff_data = []
        revert_data = []
        indices, all_files, file_state, indexed_files = self.diff_files()

        for file in indexed_files:
            diff_data.append(DGitFile(
                fname=file['name'],
                path=file['path']
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

        for file in file_state:
            if file['status'] == 'added':
                os.remove(file['file'])

            if file['status'] == 'deleted':
                with open(file['file'], 'wb+') as source_file:
                    with open(f'{OBJECT_PATH}/{get_file_index(file["file"])}/content') as object_copy:
                        for line in object_copy:
                            source_file.write(bytes(line, 'utf-8'))

        #backup stash to be implemented

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

    def checkout(self,branch):
        repository = 'e4e5647ef05e41d0a40f8af274ee8443'
        response = checkout(repository,branch)
        if response['data']['operation'] == 'create':
            print('Branch created :',response['data']['id'])
            self.set_branch(branch,response['data']['id'])

        elif response['data']['operation'] == 'exists':
            print('Branch already exists :',response['data']['id'])
        self.set_head(response['data']['id'])


    def push(self):
        print('pushing')
        repository = 'e4e5647ef05e41d0a40f8af274ee8443' #get using file
        branch = '6c87a515bc74462794d76a5b5f6433ca'
        file_data = []
        file_data.append({
            'name':'test.java',
            'path':'/home/devd/dev/d-git/trackfiles/test.java'
        })
        file_data.append({
            'name': 'test2.txt',
            'path': '/home/devd/dev/d-git/trackfiles/test2.txt'
        })
        file_data.append({
            'name': 'x.html',
            'path': '/home/devd/dev/d-git/trackfiles/x.html'
        })
        push(repository,branch,'xyz',file_data)

    #HELPER FUNCTIONS

    def get_head(self):
        head_ref = None
        with open(HEAD, 'r') as head:
            head_ref = head.readline()
        return head_ref

    def set_head(self, branch):
        with open(f'{HEAD}', 'wb+') as head:
            head.write(bytes(branch,'utf-8'))

    def get_branch(self,branch):
        branch_id = None
        with open(f'{BRANCH_REF}/{branch}', 'r') as branch_f:
            branch_id = branch_f.readline()
        return branch_id

    def set_branch(self,branch,branch_id):
        branch_ref = branch.rsplit('/',1)
        if len(branch_ref)!=1:
            if not os.path.isdir(f'{BRANCH_REF}/{branch_ref[0]}'):
                os.makedirs(f'{BRANCH_REF}/{branch_ref[0]}')

        with open(f'{BRANCH_REF}/{branch}', 'wb+') as branch_f:
            branch_f.write(bytes(branch_id,'utf-8'))
        return branch_id

    def diff_files(self):
        """
        Returns various lists as follows\n
        indices : Files in index registry\n
        all_files : All files in directory\n
        file_state : Whether a file is deleted or new file is added\n
        indexed_files : Files in index registry which is not deleted\n
        :return:
        """
        file_state = []
        indices = None
        with open(INDEX_PATH,'r') as index:
            indices = index.read().splitlines()
        indices = [index.split('=')[1] for index in indices]
        all_files = []
        indexed_files = []
        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(root,[dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    if os.path.isfile(f) and (filename.split('.')[1] not in [ext.replace('.','') for ext in self.ignore_]):
                        all_files.append(f)
                        if f in indices:
                            indexed_files.append({'path':f,'name':filename})

        for file in all_files:
            if file not in indices:
                file_state.append({'file': file, 'status': 'added'})
        for file in indices:
            if file not in all_files:
                file_state.append({'file':file,'status':'deleted'})

        return indices,all_files,file_state,indexed_files


