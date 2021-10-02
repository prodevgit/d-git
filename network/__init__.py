import glob
import json
import os
import subprocess
import uuid
import requests

from constants import USER_SIGNATURE, REPOSITORY_ID, SSH_FINGERPRINT

BASE_URL = 'http://localhost:8000/api/v1'

def checkout(name,parent=None):
    HEADERS = {'Authorization': f"Token {get_user_token_shh()['token']}"}
    data = {}
    data['name'] = name
    data['parent'] = parent
    r = requests.post(f'{BASE_URL}/branch/{get_repo_id()}/create',data=data,headers=HEADERS)
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

def get_token_by_ssh(ssh_key):
    data = {'key':ssh_key}
    r = requests.post(f'{BASE_URL}/auth/get-token-by-ssh', data=data)
    return r.json()

def get_user_token_shh():
    with open(SSH_FINGERPRINT,'r') as f:
        ssh_fingerprint = f.read().replace('\n','')
    ssh_path = get_ssh_by_fingerprint(ssh_fingerprint)
    with open(ssh_path,'r') as f:
        key = f.read().replace('\n','')
        token_response = get_token_by_ssh(key)
        return token_response

def get_ssh_by_fingerprint(fingerprint):
    ssh_path=f"{os.path.expanduser('~')}/.ssh"
    public_keys = glob.glob(f"{ssh_path}*/*.pub")
    for pubkey in public_keys:
        output = subprocess.check_output(f'ssh-keygen -E md5 -lf {pubkey}',shell=True).decode('utf-8')
        pubkey_fingerprint = output.split(' ')[1].split('MD5:')[1]
        if fingerprint == pubkey_fingerprint:
            return pubkey