import json
import uuid
import requests

from constants import USER_SIGNATURE, REPOSITORY_ID

BASE_URL = 'http://localhost:8000/api/v1'

def checkout(name,parent=None):
    HEADERS = {'Authorization': get_repo_token()}
    data = {}
    data['name'] = name
    data['parent'] = parent
    r = requests.post(f'{BASE_URL}/branch/{get_repo_id()}/console-create',data=data,headers=HEADERS)
    print(r.json())
    return r.json()

def push(repository,branch,commit,file_data):
    data = {}
    data['repository'] = repository
    data['branch'] = branch
    data['commit'] = commit
    files = {}
    fdata=[]
    for file in file_data:
        f=open(file['path'], 'rb')
        identifier = str(uuid.uuid4())
        files[identifier]=f
        fdata.append({
            'name':file['name'],
            'path':file['path'],
            'identifier':identifier
        })
    xdata=data
    xdata['fdata']=fdata
    if fdata:
        HEADERS = {'Authorization': 'Token 53d3d1310cd736aa5ec02ff550c48ec30767d95d',
                   'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(f'{BASE_URL}/repository/push',data=json.dumps(xdata),params={'request_for':'tracker'},headers=HEADERS)
        session=r.json()
        print(session)
        if session:
            HEADERS = {'Authorization': 'Token 53d3d1310cd736aa5ec02ff550c48ec30767d95d'}
            r = requests.post(f'{BASE_URL}/repository/push', files=files,data=data, params={'request_for': 'pusher', 'session':session['data']},
                              headers=HEADERS)
            print(r.json())

def clone(token):
    HEADERS = {'Authorization': token}
    # r = requests.post(f'{BASE_URL}/repository/clone', data=data,params={'clone_by': clone_by},headers=HEADERS)
    r = requests.post(f'{BASE_URL}/repository/clone', headers=HEADERS)
    return r.json()

def get_clone_file(object,token):
    HEADERS = {'Authorization': token}
    r = requests.get(object['url'], headers=HEADERS)
    return r.content

def get_ssh_server_command():
    r = requests.get(f'{BASE_URL}/ssh/server-command-retreive')
    return r.json()

def get_repo_token():
    with open(USER_SIGNATURE, 'r') as signature:
        return signature.readline().split('\n')[0]

def get_repo_id():
    with open(REPOSITORY_ID, 'r') as repository:
        return repository.readline().split('\n')[0]