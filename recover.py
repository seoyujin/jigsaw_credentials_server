import threading
import time
from apiclient import errors
import os
import credentials_mgr
import datas
import util
import git_manager


def recover():

    while True:

        time.sleep(5)

        lines = []
        with open('./recover_list.txt', 'r') as f:
            lines = f.readlines()

        print('recover not yet...')
        if len(lines) <= 0:
            continue

        print('recovering start...')

        credentials = lines[0].strip()
        group_name = util.extract_grouping_name(credentials)
        group_alphabet = group_name[:-1]

        group_info = None
        for g in datas.credentials_list:
            if group_alphabet == g.get_group_alphabet():
                group_info = g
                break
        
        origin_cre_info = None
        recover_cre_info = None
        if group_info:
    
            for cre in group_info.credentials_list:
                print(cre.get_credentials_name())
                if cre.get_state() == datas.CredentialsInfo.STATE_USABLE:
                    origin_cre_info = cre
                if cre.get_credentials_name() == credentials:
                    recover_cre_info = cre

        if (origin_cre_info == None) or (recover_cre_info == None):
            continue

        store = credentials_mgr.get_storage(origin_cre_info.get_user_id())
        service_o = credentials_mgr.get_service(store)
        store = credentials_mgr.get_storage(recover_cre_info.get_user_id())
        service_r = credentials_mgr.get_service(store)
        
        all_origin_files = credentials_mgr.retrieve_all_files(service_o)
        recover_files = credentials_mgr.retrieve_all_files(service_r)

        origin_jigsaw_folder_id = ''
        for file in all_origin_files:
            if file['title'] == 'jigsaw':
                origin_jigsaw_folder_id = file['id']
                break

        origin_children_folder_dic = credentials_mgr.get_children_folder(all_origin_files, origin_jigsaw_folder_id)

        recover_jigsaw_folder_info = None        
        for file in recover_files:
            if file['title'] == 'jigsaw':
                recover_jigsaw_folder_info = file
                break
        if recover_jigsaw_folder_info == None:
            recover_jigsaw_folder_info = credentials_mgr.create_public_folder(service_r, 'jigsaw')

        recover_children_folder_dic = {}
        for folder_name in origin_children_folder_dic.values():
            folder_info = credentials_mgr.create_public_folder(service_r, folder_name, recover_jigsaw_folder_info['id'])
            recover_children_folder_dic[folder_info['title']] = folder_info['id']

        for file in all_origin_files:
        
           parent_folder_id = file['parents'][0]['id']
           if parent_folder_id in origin_children_folder_dic:
                folder_name = origin_children_folder_dic[parent_folder_id]
                file_name = folder_name + '_' + file['title']
                file_path_name = './recover_files/'+ file_name
                #download
                credentials_mgr.download_file(service_o, file['id'],file_path_name ) 
                #upload
                credentials_mgr.upload_file(service_r, recover_children_folder_dic[folder_name], file_name, file['mimeType'], file_path_name)

        recover_cre_info.set_usable_state()
        group_info.compute_group_state()        

        lines.pop(0)
        with open('./recover_list.txt', 'w') as f:
            f.write('')
            for str in lines:
                f.write(str)

        git_manager.recover_add()



def start_threading():
    threading.Timer(1.0, recover).start()

if __name__ == '__main__':
    recover()
