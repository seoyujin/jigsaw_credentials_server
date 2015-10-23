from flask import Flask, request, redirect, render_template
from git import Repo
import capacity_monitor
import httplib2
import oauth2client
from oauth2client import client, file
import credentials_reader

SCOPES              = ['https://www.googleapis.com/auth/drive',
                       'https://www.googleapis.com/auth/drive.file',
                       'https://www.googleapis.com/auth/drive.readonly',
                       'https://www.googleapis.com/auth/drive.appdata',
                       'https://www.googleapis.com/auth/drive.apps.readonly',
                       'https://www.googleapis.com/auth/drive.metadata',
                       'https://www.googleapis.com/auth/drive.metadata.readonly',
                       'https://www.googleapis.com/auth/drive.photos.readonly'
                      ]

CLIENT_SECRET_FILE  = 'client_secret.json'
APPLICATION_NAME    = 'CREDENTIAL_SERVER' 
SERVER_URL          = 'http://silencenamu.cafe24.com:9991'

app = Flask(__name__)

@app.route('/donations', methods = ['POST'])
def donations():

    id = request.form['id']

    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                               scope=SCOPES,
                               redirect_uri='%s/redirect_url'% SERVER_URL)
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

    store  = credentials_reader.get_storage(id)
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                               scope=SCOPES,
                               redirect_uri='%s/redirect_url'% SERVER_URL)

    auth_code = request.args.get('code',None)
    credentials = flow.step2_exchange(auth_code)
    store.put(credentials)    

    repo = Repo('./datas/')
    filepath = 'credentials/%s_credential.json' % id
    repo.index.add([filepath])
    repo.index.commit('add credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()

    service = credentials_reader.get_service(id)
    about = service.about().get().execute()
    
    return render_template('donation_result.html', name=about['name'])

@app.route('/credentials', methods =['DELETE'])
def credentials_delete():

    id = request.args.get('id', None)
    if id == None:
        id = 'anyone'

    store  = credentials_reader.get_storage(id) 
    credentials = store.get()

    if credentials == None:
        return 'already revoked'
    
    credentials.revoke(httplib2.Http())

    repo = Repo('./datas/')
    filepath = 'credentials/%s_credential.json' % id
    repo.index.remove([filepath])
    repo.index.commit('revoke credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()

    return 'revoked'

@app.route('/credentials', methods = ['GET'])
def credentials_get():
   # return render_template('donation_result.html', name='hhelo')

    if len(capacity_monitor.qouta_sort_list) == 0:
        return 'no credentials'
    else:
        sorting_files = []

        try:
            for qouta in capacity_monitor.qouta_sort_list:
                sorting_files.append(qouta.get_file_name()+'\n')
        except Exception as e:
            pass
        return ''.join(sorting_files)

if __name__ == '__main__':
    capacity_monitor.start_threading()
    app.run('0.0.0.0', 9991, debug=False)

