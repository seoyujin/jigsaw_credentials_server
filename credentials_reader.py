import os
import httplib2
import oauth2client
from apiclient import discovery

def get_storage(id):

    credential_dir= os.path.expanduser('./datas/credentials/')
    file_name = id + '_credential.json'
    credential_path = os.path.join(credential_dir, file_name)

    return oauth2client.file.Storage(credential_path)

def get_service(id):
    
    store = get_storage(id)
    credentials = store.get()

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    return service
