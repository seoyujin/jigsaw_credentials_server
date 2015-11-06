import datas
import os

def make_grouping_name(end_grouping_name):

    char = ''
    char_num =0
    int_idx =0
    grouping_name =''

    for ch in end_grouping_name:
        try:
            int_idx = int(ch)
        except:
            char = ch
            char_num += 1

    if int_idx < 2:
        int_idx += 1
    else:
        int_idx = 0
        num = ord(char)
        if num < ord('z'):
            char = chr(num+1)
        else:
            char = 'a'
            char_num += 1


    for i in range(char_num):
        grouping_name += char
    grouping_name += str(int_idx)

    return grouping_name

def make_credentials_name(id, grouping_name):
    return grouping_name + '_'+ id  + '.json'

def extract_grouping_name(file_name):
    name_pieces = file_name.split('_')
    return name_pieces[0]

def get_end_credentials_name():

    credentials_list = os.listdir(datas.credentials_path)

    if len(credentials_list) <= 0:
        return None

    credentials_list.sort() 
    return credentials_list[-1]


def find_missing_grouping_name(first_gr_name, last_gr_name):

    missing_gr_names = []
    cur_gr_name = first_gr_name

    if first_gr_name == last_gr_name:
        return missing_gr_names

    while True:
        cur_gr_name = make_grouping_name(cur_gr_name)

        if cur_gr_name == last_gr_name:
            return missing_gr_names

        missing_gr_names.append(cur_gr_name)

    return missing_gr_names
