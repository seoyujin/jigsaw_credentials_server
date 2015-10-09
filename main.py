from flask import Flask, request, redirect
from git import Repo
import os
import httplib2
import oauth2client
from oauth2client import client, file, tools
from apiclient import discovery

SCOPES              = ['https://www.googleapis.com/auth/drive',
                       'https://www.googleapis.com/auth/drive.file',
                       'https://www.googleapis.com/auth/drive.appdata',
                       'https://www.googleapis.com/auth/drive.apps.readonly',
                       'https://www.googleapis.com/auth/drive.metadata.readonly'
                      ]

CLIENT_SECRET_FILE  = 'client_secret.json'
APPLICATION_NAME    = 'CREDENTIAL_SERVER' 

app = Flask(__name__)

@app.route('/get_credentials', methods = ['GET'])
def get_credentials():

    id = request.args.get('id', None)
    if id == None:
        id = 'anyone'

    store  = get_storage(id)
    credentials = store.get()

    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                               scope=SCOPES,
                               redirect_uri='http://ec2-54-64-113-34.ap-northeast-1.compute.amazonaws.com:9991/redirect_url')
    flow.params['state'] = id

    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)

@app.route('/redirect_url', methods = ['GET'])
def redirect_url():

    error = request.args.get('error', None)
    if error != None:
        return error

    id = request.args.get('state', None)
    if id == None:
        return 'No Id'

    store  = get_storage(id)
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                               scope=SCOPES,
                               redirect_uri='http://ec2-54-64-113-34.ap-northeast-1.compute.amazonaws.com:9991/redirect_url')

    auth_code = request.args.get('code',None)
    credentials = flow.step2_exchange(auth_code)
    store.put(credentials)    

    repo = Repo('./datas/')
    filepath = 'credentials/%s_credential.json' % id
    repo.index.add([filepath])
    repo.index.commit('add credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()

    return 'ok'

@app.route('/revoke_credentials', methods =['GET'])
def revoke_credentials():

    id = request.args.get('id', None)
    if id == None:
        id = 'anyone'

    store  = get_storage(id)
    credentials = store.get()

    credentials.revoke(httplib2.Http())

    repo = Repo('./datas/')
    filepath = 'credentials/%s_credential.json' % id
    repo.index.remove([filepath])
    repo.index.commit('revoke credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()

    return 'revoked'

def get_storage(id):

    credential_dir= os.path.expanduser('./datas/credentials/')
    file_name = id + '_credential.json'
    credential_path = os.path.join(credential_dir, file_name)

    return oauth2client.file.Storage(credential_path)

if __name__ == '__main__':
    app.run('0.0.0.0', 9991, debug=False)

