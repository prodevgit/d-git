from constants import INDEX_PATH, RECENT_PATH, OBJECT_PATH, TColors
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
    f = open(f'{INDEX_PATH}','rb')
    x = [index_path_pair.decode('utf8').split('=')[0] for index_path_pair in f.read().splitlines() if index_path_pair.decode('utf8').split('=')[1] == path][0]
    return x


def compare(source_file):
    diff_set = []
    with open(source_file, 'r') as f:
        source_lines = {}
        for _,line in enumerate(f.read().splitlines()):
            source_lines[_]=line
        print(source_lines)

    with open(f'{OBJECT_PATH}/{get_file_index(source_file)}/content', 'r') as f:
        content_lines = {}
        for _, line in enumerate(f.read().splitlines()):
            content_lines[_] = line
        print(content_lines)
    line_add_flag = True

    for entry in zip_longest(source_lines,content_lines):

        if entry[0] == None:
            diff_set.append({'line':entry[1]+1,'content':content_lines[entry[1]],'type':'~'})
        elif entry[1] == None:
            print(entry[0])
            # diff_set.append({'line': entry[0] + 1, 'content': source_lines[entry[0]],'type':'+'})
        elif content_lines[entry[0]] != source_lines[entry[1]] and line_add_flag == True:
            diff_set.append({'line': entry[0] + 1, 'content': source_lines[entry[1]], 'type': '+'})
            try:
                if content_lines[entry[0]] == source_lines[entry[1]+1]:
                    line_add_flag = False
            except KeyError:
                line_add_flag = False
        # elif source_lines[entry[0]] != content_lines[entry[1]]:
        #     diff_set.append({'line': entry[0] + 1, 'content': source_lines[entry[0]],'type':'~'})

    print(diff_set)
    return diff_set

def prepare_diff_out(diff_set,path):
    linemap = {}
    start_line = diff_set[0]['line']
    end_line = diff_set[-1]['line']
    print(start_line)
    print(end_line)
    line_data = [diff['line'] for diff in diff_set]
    for _,line_no in enumerate(range(start_line,end_line+1)):
        linemap[line_no]=_+2
    print(linemap)
    diff_out = ''
    with open(f'{OBJECT_PATH}/{get_file_index(path)}/content','r') as f:
        data = f.read().splitlines()
        for diff in diff_set:

            if diff['type'] == '+':
                temp_out = f'{TColors.OKGREEN}{diff["type"]} {diff["content"]}'
                line = diff["line"]
                prev_line = f'{data[line - linemap[line]]}'
                diff_out = f'{diff_out}\n{prev_line}\n{temp_out}'

            elif diff['type'] == '~':
                temp_out = f'{TColors.OKGREEN}{diff["type"]} {diff["content"]}'
                line = diff["line"]
                if line-1 in line_data :
                    diff_out = f'{diff_out}\n{temp_out}'
                else:
                    prev_line = f'{TColors.DIFF}- {data[line - linemap[line]]}'
                    diff_out = f'{diff_out}\n{prev_line}\n{temp_out}'
    print(diff_out)
    return diff_out

def multiple_find(str,query_list):
    s = [str.find(x) for x in query_list]
    return sum(s)

