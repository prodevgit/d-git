

from constants import INDEX_PATH, RECENT_PATH, OBJECT_PATH, TColors
from helper import difflib
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
    s = [str.find(x) for x in query_list]
    return sum(s)

def check_branch_exists(branch_name):
    return 0

