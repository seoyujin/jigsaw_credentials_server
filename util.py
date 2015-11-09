import datas
import os


def make_grouping_name(end_grouping_name):
    alphabet_part = end_grouping_name[:-1]
    no_part       = end_grouping_name[-1]
    if no_part == '2':
        cur_char = alphabet_part[0]
        if cur_char == 'z':
            new_alphabet_part = 'a' * (len(alphabet_part)+1)
            return '%s0' % new_alphabet_part
        else:
            next_char = chr( ord(cur_char)+1 )
            new_alphabet_part = next_char * len(alphabet_part)
            return '%s0' % new_alphabet_part
    else:
        return '%s%d' % (alphabet_part, int(no_part) + 1)

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

