import os
import httplib2
import oauth2client
from apiclient import discovery
import monitor
import datas
import util

def make_storage(id):

    grouping_name = ''
    group_info = None    
    cre_obj = None

    for g_info in datas.credentials_list:
        
        if g_info.get_usable_state() == datas.GroupInfo.STATE_DISABLE_GROUP:

            for cre_file in g_info.credentials_list:
                if cre_file.get_state() == datas.CredentialsInfo.STATE_RECOVERY_WAIT:
                    group_info = g_info
                    grouping_name = cre_file.get_group_name()
                    cre_obj = cre_file
                    break
        if group_info != None:
            break
            
    if group_info == None:
        end_file_name = util.get_end_credentials_name()
        if end_file_name == None:
            grouping_name = 'a0'
        else:
            end_grouping_name = util.extract_grouping_name(end_file_name)
            if end_grouping_name[-1] != '2':
                end_grouping_name = end_grouping_name[:-1] + '2'
            grouping_name = util.make_grouping_name(end_grouping_name)
        
        group_info = datas.GroupInfo(grouping_name[:-1])
        cre_obj = group_info.credentials_list[0]
        datas.credentials_list.append(group_info)
            

    file_name = util.make_credentials_name(id, grouping_name)
    credential_path = os.path.join(datas.credentials_path, file_name)

    datas.credential_dic[id] = file_name    

    return oauth2client.file.Storage(credential_path), group_info, cre_obj

def get_storage(id):

    credential_dir = os.path.expanduser(datas.credentials_path)

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


def delete_all_files(service, max=50):

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
