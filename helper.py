from constants import INDEX_PATH, INDEX_FILE
import uuid

def write_index(fid,branch,commit):
    f = open(f'{INDEX_PATH}/{INDEX_FILE}','wb+')
    f.write()