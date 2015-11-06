import queue
import os
import util

credential_dic ={}
qouta_sort_list = list() 
recover_que = queue.Queue()
recover_que_view_list = []

credentials_path = './datas/credentials/'


def load_credentials_dic():
    
    global credential_dic

    credentials_list = os.listdir(credentials_path)

    for file_name in credentials_list:
        id = file_name.split('_')[1].split('.')[0]
        credential_dic[id] = file_name

def load_recover_que():

    credentials_list = os.listdir(credentials_path)
    credentials_list.sort()

    if len(credentials_list) <= 0 :
        return None

    group_dic = {}
    max_count = 0
    last_group_name = util.extract_grouping_name(credentials_list[-1])

    for cre in credentials_list:
        
      group_name = util.extract_grouping_name(cre) 
      name_count = count_alphabet(group_name)
      if max_count <  name_count:
         max_count = name_count 
      
      group_dic[group_name] = cre
    print(group_dic)

    group_alphabet = 'a'
    while True:

      recover_group(group_alphabet, max_count, group_dic)
      if group_alphabet == last_group_name[0]:
         break
      group_alphabet = chr(ord(group_alphabet)+1)


def recover_group(group_alphabet, max_count, group_dic):

    global recover_que
    global recover_que_view_list

    cur_group_name = group_alphabet + '0' 
    last_group_name = ''

    for i in range(max_count):
        last_group_name += group_alphabet

    last_group_name += '2'

    while True:
        print(cur_group_name)
        
        try:
           group_dic[cur_group_name]
        except:
           recover_que.put(cur_group_name)
           recover_que_view_list.append(cur_group_name)

        if cur_group_name == last_group_name:
           break

        cur_group_name = name_next_group_alphabet(cur_group_name)


def count_alphabet(grouping_name):

    char_num = 0
    for ch in grouping_name:
        try:
            int_idx = int(ch)
        except:
            char = ch
            char_num += 1

    return char_num


def name_next_group_alphabet(cur_gr_name):

    char = ''
    char_num = 0
    int_idx = 0
    for ch in cur_gr_name:
        try:
            int_idx = int(ch)
        except:
            char = ch
            char_num += 1

    if int_idx >= 2:
        char_num += 1

    int_idx = (int_idx +1) % 3

    next_group_name = ''
    for i in range(char_num):
        next_group_name += char
    next_group_name += str(int_idx)

    return next_group_name
