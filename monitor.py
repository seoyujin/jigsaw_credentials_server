import threading
import time
import credentials_reader
from apiclient import errors
import os
import credentials_reader
import datas

class Credentilas_info:
    file_name = ''
    user_name = ''
    folder_id = ''
    total_quota = 0 
    used_quota = 0 

    def set_credentials_info(self, file_name_, user_name_, folder_id_, total_quota_, used_quota_):
        self.file_name = file_name_
        self.user_name = user_name_
        self.folder_id = folder_id_
        self.total_quota = total_quota_
        self.used_quota = used_quota_

    def get_file_name(self):
        return self.file_name

    def get_user_name(self):
        return self.user_name

    def get_folder_id(self):
        return self.folder_id

    def get_total_quota(self):
        return self.total_quota

    def get_used_quota(self):
        return self.used_quota


def monitor():

    while True:

        file_name_list = os.listdir("./datas/credentials/")
        file_name_list.sort()
        tmp_list = list()

        for file_name in file_name_list:

            id = file_name.split('_')[1].split('.')[0] 
            store = credentials_reader.get_storage(id)
            service = credentials_reader.get_service(store)       

            try:
                about = service.about().get().execute()

                info = Credentilas_info() 
                info.set_credentials_info(file_name, about['name'], about['rootFolderId'], about['quotaBytesTotal'], about['quotaBytesUsed']) 
                tmp_list.append(info)

            except Exception as e:
                os.remove('./datas/credentials/'+file_name)
                datas.credential_dic.pop(id)

                if file_name != file_name_list[-1]:
                    grouping_name = extract_grouping_name(file_name)
                    datas.recover_que.put(grouping_name)
                
                print('An error occurred: %s\n\n' % e)

        #sorting
        datas.qouta_sort_list = sorted(tmp_list, key=lambda e:int(e.get_used_quota()))
        
        for info in datas.qouta_sort_list:
            print('Credentials name: %s' % info.get_file_name())
            print('Current user name: %s' % info.get_user_name())
            print('Root folder ID: %s' % info.get_folder_id())
            print('Total quota (bytes): %s' % info.get_total_quota())
            print('Used quota (bytes): %s\n' % info.get_used_quota())
            
        print('----------------------------------------------------\n') 
        
        time.sleep(5)

def start_threading():
    threading.Timer(1.0,monitor).start()


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

