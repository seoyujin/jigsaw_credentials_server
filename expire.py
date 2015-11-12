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
        
def expire():

    expired_date = date.today() + timedelta(days = -2)

    os_path = '/home/yujin/jigsaw_credentials_server/'
    cre_path = os_path + 'datas/credentials/' 
    cre_list = os.listdir(cre_path)

    #f = open(os_path + '/aaa_test.txt', 'w')
    #f.write(str(expired_date) + '\n')
    for cre in cre_list:
        store = oauth2client.file.Storage(cre_path + cre)
        service = credentials_mgr.get_service(store)
        all_files = credentials_mgr.retrieve_all_files(service)

        jigsaw_files = {}
        for file in all_files:
            if file['mimeType'] != 'application/vnd.google-apps.folder':
                break
            if file['title'] == 'jigsaw':
                jigsaw_files[file['id']] = file

        #f.write(cre + '\n')
        for file in all_files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                #f.write(file['title']+ '    ' + file['mimeType'] + '    ' + file['parents'][0]['id'] +  '\n')
                if file['parents'][0]['id'] in jigsaw_files:
                    folder_date = convert_date(file['title'])
                    if folder_date:
                        if folder_date <= expired_date:
                            service.files().delete(fileId=file['id']).execute()

    #f.close()



if __name__ == '__main__':
    expire()
