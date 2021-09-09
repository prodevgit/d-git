import json
import uuid

import requests
BASE_URL = 'http://localhost:8000/api/v1'

def checkout(repository,name,parent=None):
    HEADERS = {'Authorization': 'Token 53d3d1310cd736aa5ec02ff550c48ec30767d95d'}
    data = {}
    data['name'] = name
    data['parent'] = parent
    r = requests.post(f'{BASE_URL}/branch/{repository}/create',data=data,headers=HEADERS)
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

def clone(repository,clone_by,token):
    HEADERS = {'Authorization': token}
    data={}
    data['repository']=repository
    r = requests.post(f'{BASE_URL}/repository/clone', data=data,params={'clone_by': clone_by},headers=HEADERS)
    print(r.text)
    return r.json()
