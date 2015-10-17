import threading
import time
import credentials_reader
from apiclient import errors
import os


qouta_sort_list = list() 

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


def monitoring_capacity():
    global qouta_sort_list

    while True:

        file_name_list = os.listdir("./datas/credentials/")
        tmp_list = list()

        for file_name in file_name_list:
            name_pieces = file_name.split('_')
            service = credentials_reader.get_service(name_pieces[0])       

            try:
                about = service.about().get().execute()

                info = Credentilas_info() 
                info.set_credentials_info(file_name, about['name'], about['rootFolderId'], about['quotaBytesTotal'], about['quotaBytesUsed']) 
                tmp_list.append(info)

            except Exception as e:
                print('An error occurred: %s' % e)

        #sorting
        qouta_sort_list = sorted(tmp_list, key=lambda e:int(e.get_used_quota()))

        for info in qouta_sort_list:
            print('Credentials name: %s' % info.get_file_name())
            print('Current user name: %s' % info.get_user_name())
            print('Root folder ID: %s' % info.get_folder_id())
            print('Total quota (bytes): %s' % info.get_total_quota())
            print('Used quota (bytes): %s\n\n' % info.get_used_quota())
            
        time.sleep(100)

def start_threading():
    threading.Timer(1.0,monitoring_capacity).start()

