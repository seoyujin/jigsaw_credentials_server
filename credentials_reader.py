import os
import httplib2
import oauth2client
from apiclient import discovery
import monitor
import datas

def make_storage(id):

    credential_dir= os.path.expanduser('./datas/credentials/')

    grouping_name = ''
    if datas.recover_que.qsize() > 0:
        grouping_name = datas.recover_que.get()
    else:
        end_file_name = get_end_credentials_name()
        if end_file_name == None:
            grouping_name = 'a0'
        else:
            end_grouping_name = monitor.extract_grouping_name(end_file_name)
            grouping_name = monitor.make_grouping_name(end_grouping_name)

    file_name = monitor.make_credentials_name(id, grouping_name)
    credential_path = os.path.join(credential_dir, file_name)

    datas.credential_dic[id] = file_name    

    return oauth2client.file.Storage(credential_path)

def get_storage(id):

    credential_dir = os.path.expanduser('./datas/credentials/')

    try :
        credential_path = os.path.join(credential_dir,datas.credential_dic[id])
    except Exception as e:
        print('credentilas_reader.py : get_storage(id) erro: %s' % e)
        return None

    return oauth2client.file.Storage(credential_path)

def get_service(store):
    
    credentials = store.get()

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    return service

def get_end_credentials_name():

    credentials_list = os.listdir('./datas/credentials/')

    if len(credentials_list) <= 0:
        return None

    credentials_list.sort() 
    return credentials_list[-1]


def create_public_folder(service):

    body = {
    'title': 'jigsaw',
    'mimeType': 'application/vnd.google-apps.folder'
    }

    file = service.files().insert(body=body).execute()

    permission = {
    'value': '',
    'type': 'anyone',
    'role': 'reader'
    }

    service.permissions().insert(
      fileId=file['id'], body=permission).execute()

    return file['id']


def delete_all_files(service, max=10):

    results = service.files().list(maxResults=max).execute()
    items = results.get('items', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            try:
                service.files().delete(fileId=item['id']).execute()
            except Exception as error:
                print(error)
