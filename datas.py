import queue
import os

credential_dic ={}
qouta_sort_list = list() 
recover_que = queue.Queue()


def load_credentials_dic():
    
    global credential_dic

    credentials_list = os.listdir('./datas/credentials/')

    for file_name in credentials_list:
        id = file_name.split('_')[1].split('.')[0]
        credential_dic[id] = file_name


def load_recover_que():

    credentials_list = os.listdir('./datas/credentials/')
    credentials_list.sort()

    if len(credentials_list) <= 0 :
        return None
    '''
    end_grouping_name = 'a0'
    for cre  in credentials_list:
        cur_grouping_name = extract_grouping_name(cre)
        if cur_grouping_name != end_grouping_name:
            recover_que.put(end_grouping_name)
            end_grouping_name = 
    '''
