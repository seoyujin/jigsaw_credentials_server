
import os
import oauth2client
import credentials_mgr
from datetime import date, timedelta

def convert_date(date_str):
        
    try:
        year = int(date_str[:4])
        month = int(date_str[5:7])
        day = int(date_str[8:])

        return date(year, month, day)
    except:
        return None
        
def garbage():

    garbage_date = date.today() + timedelta(days = -2)
    os_path = '/home/yujin/jigsaw_credentials_server/'

    fi = open(os_path +'aaa_garbage.txt', 'w')

    gb_list = []
    with open(os_path +'garbage.txt') as f:
        for line in f:
            date_str = line.split(' ')[0]
            cur_date = convert_date(date_str)
            if cur_date <= garbage_date:
                gb_list.append(line)

    cre_path = os_path + 'datas/credentials/' 
    cre_list = os.listdir(cre_path)
    cre_dic = {}
    for cre in cre_list:
        id = cre.split('_')[1].split('.')[0]
        cre_dic[id] = cre

    cur_id = ''
    all_files = None
    for gb in gb_list:
        id = gb.split(' ')[1]
        file_name = gb.split(' ')[2]

        if id not in cre_dic:
            continue

        if id != cur_id:
            store = oauth2client.file.Storage(cre_path + cre_dic[id])
            service = credentials_mgr.get_service(store)
            all_files = credentials_mgr.retrieve_all_files(service)
            cur_id = id

        for file in all_files:
            if file['title'].strip() == file_name.strip():
                fi.write(file['title'] + ' ' + file_name + '\n')
                service.files().delete(fileId=file['id']).execute()
                break
    fi.close()


if __name__ == '__main__':
    garbage()
