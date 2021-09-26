import glob
import os.path

import requests

from constants import INDEX_PATH, RECENT_PATH, OBJECT_PATH, TColors
from helper import difflib
from network import get_clone_file
from serializer import FileSerializer
from itertools import chain, zip_longest


def write_index(fid,branch,commit):
    f = open(f'{INDEX_PATH}','wb')
    recent_registry = open(f'{RECENT_PATH}','rb')
    l_index = FileSerializer(recent_registry).__dict__['latest_index']
    new_index = l_index + 1
    #write new index to file
    f.write()

def get_file_index(path):
    with open(f'{INDEX_PATH}','r') as f:
        index = [index_path_pair.split('=')[0] for index_path_pair in f.read().splitlines() if index_path_pair.split('=')[1] == path][0]
    return index


def diff_out(source_file):
    formatted_diff = []
    with open(source_file, 'r') as f:
        source_lines = f.read().splitlines()

    with open(f'{OBJECT_PATH}/{get_file_index(source_file)}/content', 'r') as f:
        content_lines = f.read().splitlines()

    for line in difflib.unified_diff(content_lines,source_lines):
        if line[0] == '-' and line[0:3] != '---':
            formatted_diff.append(f'{TColors.DIFF}{line}')
        elif line[0] == '+' and line[0:3] != '+++':
            formatted_diff.append(f'{TColors.OKGREEN}{line}')
        else:
            formatted_diff.append(f'{TColors.WHITE}{line}')
    return formatted_diff

def multiple_find(str,query_list):
    print("Dirs: ",query_list)
    s = [str.find(x) for x in query_list]
    print(s)
    return sum(s)

def check_branch_exists(branch_name):
    return 0

def process_clone_data(clone_data,token):
    # try:
    repository_name = clone_data['data']['name']
    objects_count = clone_data['data']['objects_count']
    branches = clone_data['data']['data']
    default_branch = clone_data['data']['default']
    current_count = 1
    if not os.path.isdir(f'{os.getcwd()}/{repository_name}'):
        os.mkdir(repository_name)
    for branch in branches:
        # if branch['object_id'] == default_branch['object_id']:
        #
        # else:
        commits = branch['commits']
        for commit_key,commit in commits.items():
            objects = commit['objects']
            for object_key,object in objects.items():
                with open(f"{repository_name}/{object['path']}",'wb+') as f:
                    file_content = get_clone_file(object,token)
                    f.write(file_content)
                progressBar(current_count,objects_count,20)
                current_count = current_count + 1

def process_default_branch(branch_data):
    pass
def progressBar(index, total, bar_len=50, title='Please wait'):
    '''
    index is expected to be 0 based index.
    0 <= index < total
    '''
    percent_done = (index+1)/total*100
    percent_done = round(percent_done, 1)

    done = round(percent_done/(100/bar_len))
    togo = bar_len-done

    done_str = '█'*int(done)
    togo_str = '░'*int(togo)

    # print(f' [{done_str}{togo_str}] {percent_done}% done', end='\r')
    print(f' [{done_str}{togo_str}] {index+1}/{total} files', end='\r')

    if round(percent_done) == 100:
        print('')

def get_ssh_by_fingerprint(fingerprint):
    ssh_path=f"{os.path.expanduser('~')}/.ssh"
    public_keys = glob.glob(f"{ssh_path}*/*.pub")



