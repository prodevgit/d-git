from constants import INDEX_PATH, RECENT_PATH, OBJECT_PATH
from serializer import FileSerializer


def write_index(fid,branch,commit):
    f = open(f'{INDEX_PATH}','wb')
    recent_registry = open(f'{RECENT_PATH}','rb')
    l_index = FileSerializer(recent_registry).__dict__['latest_index']
    new_index = l_index + 1
    #write new index to file
    f.write()

def get_file_index(path):
    f = open(f'{INDEX_PATH}','rb')
    x = [index_path_pair.decode('utf8').split('=')[0] for index_path_pair in f.read().splitlines() if index_path_pair.decode('utf8').split('=')[1] == path][0]
    return x


def compare(source_file):
    with open(source_file, 'r') as f:
        d = set(f.read().splitlines())
    with open(f'{OBJECT_PATH}/{get_file_index(source_file)}/content', 'r') as f:
        e = set(f.read().splitlines())

    return d-e

def multiple_find(str,query_list):
    s = [str.find(x) for x in query_list]
    return sum(s)

