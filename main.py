from flask import Flask, request, redirect, render_template
import monitor
import httplib2
import oauth2client
from oauth2client import client, file
import credentials_reader
import git_manager
import os
import json
import datas

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

    try:
        datas.credential_dic[id]
    except:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                   scope=SCOPES,
                                   redirect_uri='%s/redirect_url'% SERVER_URL)
        flow.params['access_type'] = 'offline'
        flow.params['state'] = id

        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)


@app.route('/donations', methods = ['GET'])
def get_donations():
    return render_template('already_donation.html')
    

@app.route('/redirect_url', methods = ['GET'])
def redirect_url():
    error = request.args.get('error', None)
    if error != None:
        return error

    id = request.args.get('state', None)
    if id == None:
        return 'No Id'

    store  = credentials_reader.make_storage(id)
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                               scope=SCOPES,
                               redirect_uri='%s/redirect_url'% SERVER_URL)
    auth_code = request.args.get('code',None)
    credentials = flow.step2_exchange(auth_code)

    store.put(credentials)

    service = credentials_reader.get_service(store)
    credentials_reader.delete_all_files(service)
    folder_id = credentials_reader.create_public_folder(service)
    
    cre_dic = json.loads(credentials.to_json())
    cre_dic['jigsaw_folder_id'] = folder_id
    cre_str = json.dumps(cre_dic)

    f = open('./datas/credentials/%s' % datas.credential_dic[id],'w') 
    f.write(cre_str)
    f.close()

    return render_template('donation_result.html')

@app.route('/credentials', methods =['DELETE'])
def credentials_delete():

    try:
        id = request.args.get('id', None)
        if id == None:
            id = 'anyone'

        store  = credentials_reader.get_storage(id) 
        if store == None:
            return 'credentials not exist'

        credentials = store.get()
        if credentials == None:
            return 'already revoked'
        
        credentials.revoke(httplib2.Http())

        file_name = store._filename.split('/')[-1]
        end_file_name = credentials_reader.get_end_credentials_name()
        if file_name != end_file_name:
            grouping_name = monitor.extract_grouping_name(file_name)
            datas.recover_que.put(grouping_name)

        datas.credential_dic.pop(id)

    except Exception as e:
        print(e)
        raise

    return 'revoked'

@app.route('/credentials', methods = ['GET'])
def credentials_get():

    '''
    if len(datas.qouta_sort_list) == 0:
        return 'no credentials'
    else:
        sorting_files = []

        try:
            for qouta in datas.qouta_sort_list:
                sorting_files.append(qouta.get_file_name()+'\n')
        except Exception as e:
            pass
        return ''.join(sorting_files)
    '''
    datas = []

    credentials_files = os.listdir('./datas/credentials/')
    credentials_files.sort()

    if len(credentials_files) <= 0:
        return 'no credentials'

    for f in credentials_files:
        datas.append(f + '\n')

        j_file = open('./datas/credentials/'+f , 'r')
        j_data = j_file.read()
        j_file.close()

        datas.append(j_data + '\n')

    return ''.join(datas)

if __name__ == '__main__':
    datas.load_credentials_dic()
    monitor.start_threading()
    app.run('0.0.0.0', 9991, debug=False)

