import os
import httplib2
import oauth2client
from apiclient import discovery, http, errors
import monitor
import datas
import util
from apiclient.http import MediaFileUpload
import os

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


def retrieve_all_files(service):

    result = []
    page_token = None
    while True:
        try:
          param = {}
          if page_token:
            param['pageToken'] = page_token

          files = service.files().list(orderBy = 'folder,title', **param).execute()

          result.extend(files['items'])
          page_token = files.get('nextPageToken')
          if not page_token:
            break
        except Exception as error:
          print('An error occurred: %s' % error)
          break
    return result



def upload_file(service, folder_id, title,  mime_type, filename):


  media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
  body = {
    'title': title,
    'description': '',
    'mimeType': mime_type,
    "parents": [{
        "kind": "drive#fileLink",
        "id": folder_id
    }]
  }

  try:
    file = service.files().insert( body=body,media_body=media_body).execute()
    print('Upload Complete')
    return file
  except Exception as e:
    print(e)
    return None



def create_public_folder(service, folder_name, parent_id= None):

    body = {
    'title': folder_name,
    'mimeType': 'application/vnd.google-apps.folder'
    }

    # Set the parent folder.
    if parent_id:
        body['parents'] = [{
            "kind": "drive#fileLink",
            'id': parent_id }]

    file = service.files().insert(body=body).execute()

    permission = {
    'value': '',
    'type': 'anyone',
    'role': 'reader'
    }

    service.permissions().insert(fileId=file['id'], body=permission).execute()

    return file


def get_children_folder(all_files, parent_folder_id):

    ch_folder_dic = {}

    for file in all_files:

        if file['mimeType'] != 'application/vnd.google-apps.folder':
            break

        if file['parents'][0]['id'] == parent_folder_id:
            ch_folder_dic[file['id']] = file['title']

    return ch_folder_dic


def download_file(service, file_id, file_path_name):

    file = open(file_path_name, 'wb')
    request = service.files().get_media(fileId=file_id)
    media_request = http.MediaIoBaseDownload(file, request)

    while True:
        try:
          download_progress, done = media_request.next_chunk()
        except errors.HttpError as error:
          print('An error occurred: %s' % error)
          file.close
          os.remove(file_path_name)
          return


        if download_progress:
          print('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
          print('Download Complete')
          file.close
          return

    file.close



def delete_all_files(service):

    files = retrieve_all_files(service)

    try:
        for f in files:
            service.files().delete(fileId=f['id']).execute()
    except Exception as e:
        print(e)

