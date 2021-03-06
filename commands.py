import json
import os

from binascii import hexlify

import paramiko
from paramiko.ssh_exception import SSHException

from constants import DGIT_IGNORE, INDEX_PATH, OBJECT_PATH, TColors, HEAD, BRANCH_REF, \
    USER_SIGNATURE, DGIT, BRANCH_PATH, BRANCH_REF_INDEX, REPOSITORY_ID, SSH_FINGERPRINT
from helper import multiple_find, get_file_index, diff_out, process_clone_data
from models import DGitFile
from network import push, checkout, clone, get_ssh_server_command, get_token_by_ssh


class DGitCommand():

    def __init__(self):
        self.cwd = os.getcwd()
        self.active = False
        try:
            with open(DGIT_IGNORE,'r') as ignore_file:
                self.ignore_ = ignore_file.read().splitlines()
                if '.dgit/' not in self.ignore_:
                    self.ignore_.append('.dgit/')
                self.active = True
        except FileNotFoundError as e:
            print(e)
            import sys
            try:
                arg = sys.argv[1]
                if arg == 'clone':
                    self.active = True
                else:
                    print("Invalid Repository")
                    self.active = False
            except:
                pass

    def generate_support_files(self,repository=None):
        if not os.path.isdir('.dgit'):
            os.mkdir('.dgit')
        if not os.path.isdir(OBJECT_PATH):
            os.mkdir(OBJECT_PATH)
        if not os.path.isdir(BRANCH_REF):
            os.mkdir(BRANCH_REF)
        if repository:
            with open(REPOSITORY_ID,'w+') as f:
                f.write(repository)
        with open(BRANCH_REF_INDEX,'wb+') as f:
            f.write(b'')

    def init_repo(self):
        with open(BRANCH_REF_INDEX,'wb+') as f:
            f.write(b'')
        registry = open(f'{INDEX_PATH}','wb')
        with open(HEAD,'wb+') as head:
            head.write(b'')
        try:
            latest_index = registry.readlines()[-1]
        except:
            latest_index = 0
        registry.close()
        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(f'{root}/',[dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    file_type_status = False
                    try:
                        file_type_status = filename.split('.')[1] not in [ext.replace('.','') for ext in self.ignore_]
                    except:
                        file_type_status = filename not in [ext.replace('.','') for ext in self.ignore_]

                    if os.path.isfile(f) and file_type_status:
                        latest_index = latest_index+1
                        DGitFile(
                            fname=filename,
                            index=latest_index,
                            last_update=None,
                            path=f,
                            branch=None,
                            commit=None
                        ).save()

    def clone(self,sshkey,repository):

        file_check_repo = repository.split(':')[1]
        file_check_repo = file_check_repo.split('/')[1]

        if os.path.isfile(f'{file_check_repo}/{USER_SIGNATURE}'):
            print("You're already in a repository")
            exit()
        data = {}
        if '@' in repository:
            hostname, repository = repository.split(':')
            user, hostname = hostname.split('@')
            from paramiko.client import SSHClient
            client = SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                client.connect(hostname=hostname, username=user, key_filename=sshkey)
                sshkey_fingerprint = hexlify(client.get_transport().__dict__['auth_handler'].private_key.get_fingerprint(),':').decode('utf-8')
                ssh_response = get_ssh_server_command()
                if ssh_response['status'] == False:
                    print("Clone failed due to dgit server error")
                    return 0
                DGIT_SSH_SERVER_COMMAND = ssh_response['data'].replace('\n','') + ' ' + repository
                stdin, stdout, stderr = client.exec_command(DGIT_SSH_SERVER_COMMAND)
                data = stdout.read().decode("utf8").strip()
                data = json.loads(data)
            except SSHException as e:
                print(e)
                print("Can't connect to Dgit SSH server. SSH Authentication failed")
            client.close()

        if data['status'] == 'True':
            token = data['data']
            if token:

                if not os.path.isdir(f'{file_check_repo}/{DGIT}'):
                    os.makedirs(f'{file_check_repo}/{DGIT}')
                with open(f'{file_check_repo}/{USER_SIGNATURE}','wb+') as signature:
                    signature.write(bytes(token,'utf-8'))

                clone_data=clone(token)
                curr_dir = os.getcwd()
                os.chdir(f'{os.getcwd()}/{clone_data["data"]["name"]}')
                repo_init_command_instance = DGitCommand()
                repo_init_command_instance.generate_support_files(repository=clone_data["data"]["name"])
                os.chdir(curr_dir)

                process_clone_data(clone_data,token)

                os.chdir(f'{os.getcwd()}/{file_check_repo}')
                with open(SSH_FINGERPRINT,'w+') as f:
                    f.write(sshkey_fingerprint)

                repo_init_command_instance = DGitCommand()
                repo_init_command_instance.init_repo()


        else:
            print(data['message'])



    def branch(self):
        print(f"You're on {self.get_branch_name(self.get_head())}")

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
        # self.diff_files()
        indices = None
        with open(INDEX_PATH, 'r') as index:
            indices = index.read().splitlines()
        try:
            latest_index = int(indices[-1].split('=')[0])
        except:
            latest_index = 0

        indices = [index.split('=')[1] for index in indices]

        for root, d_names, f_names in os.walk(self.cwd):
            if multiple_find(f'{root}/',[dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    if os.path.isfile(f) and (filename.split('.')[1] not in [ext.replace('.','') for ext in self.ignore_]):
                        if f not in indices:
                            latest_index = latest_index+1
                            DGitFile(
                                fname=filename,
                                index=latest_index,
                                last_update=None,
                                path=f,
                                branch=None,
                                commit=None
                            ).save()


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
        indices, all_files, file_state, indexed_files = self.diff_files()
        for file in indexed_files:
            diff_data.append(DGitFile(
                fname=file['name'],
                path=file['path']
            ).check_diff())
        print('Changes')
        for data in diff_data:
            if data['status'] == True:
                print(f'\n\n{TColors.WHITE}{data["data"]}')
                formatted_out = diff_out(data['data'])
                for line in formatted_out:
                    print(line)
        #Can include newly added file's contents

    def checkout(self,branch):
        try:
            response = checkout(branch)
            if response['data']['operation'] == 'create':
                print('Branch created :',response['data']['id'])
                self.set_branch(branch,response['data']['id'])

            elif response['data']['operation'] == 'exists':
                print('Branch already exists :',response['data']['id'])
            self.set_head(response['data']['id'])
        except Exception as e:
            print(e)

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

    def get_head(self,is_name = False):
        head_ref = None
        with open(HEAD, 'r') as head:
            head_ref = head.readline()
        if is_name:
            return ''
        else:
            return head_ref

    def set_head(self, branch):
        with open(f'{HEAD}', 'wb+') as head:
            head.write(bytes(branch,'utf-8'))

    def get_branch(self,branch):
        branch_id = None
        with open(f'{BRANCH_REF}/{branch}', 'r') as branch_f:
            branch_id = branch_f.readline()
        return branch_id

    def get_branch_name(self,branch_id):
        branch_name = ''
        with open(f'{BRANCH_REF_INDEX}', 'r') as branch_f:
            branches = branch_f.readlines()
            for branch in branches:
                if branch.split('=')[0] == branch_id:
                    branch_name = branch.split('=')[1]
        return branch_name

    def set_branch(self,branch,branch_id):
        print("Branch: ",branch)
        branch_ref = branch.rsplit('/',1)
        print("Branch Split: ",branch_ref)
        if len(branch_ref)!=1:
            if not os.path.isdir(f'{BRANCH_REF}/{branch_ref[0]}'):
                os.makedirs(f'{BRANCH_REF}/{branch_ref[0]}')

            if not os.path.isdir(f'{BRANCH_PATH}/{branch}'):
                os.makedirs(f'{BRANCH_PATH}/{branch}')

        with open(f'{BRANCH_REF}/{branch}', 'wb+') as branch_f:
            branch_f.write(bytes(branch_id,'utf-8'))

        with open(f'{BRANCH_REF_INDEX}', 'wb') as branch_index:
            branch_index.write(bytes(f'{branch_id}={branch}', 'utf-8'))

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
            if multiple_find(f'{root}/',[dir for dir in self.ignore_ if dir.__contains__('/')]) < 0:
                for filename in f_names:
                    f = os.path.join(root, filename)
                    file_ext_status = None
                    try:
                        file_ext_status = filename.split('.')[1] not in [ext.replace('.','') for ext in self.ignore_]
                    except:
                        file_ext_status = filename not in [ext.replace('.','') for ext in self.ignore_]
                    if os.path.isfile(f) and file_ext_status:
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


