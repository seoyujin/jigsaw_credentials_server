from flask import Flask, request, redirect, render_template
import monitor
import httplib2
import oauth2client
from oauth2client import client, file
import credentials_mgr
import git_manager
import os
import json
import datas
import util

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

failed_donation = False
@app.route('/donations', methods = ['POST'])
def donations():
    global failed_donation
    id = request.form['id']

    try:
        datas.credential_dic[id]
    except:
        try:
            datas.credential_dic[id] = ''

            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                       scope=SCOPES,
                                       redirect_uri='%s/redirect_url'% SERVER_URL)
            flow.params['access_type'] = 'offline'
            flow.params['approval_prompt'] = 'force'
            flow.params['state'] = id

            auth_uri = flow.step1_get_authorize_url()
            return redirect(auth_uri)
        except:
            failed_donation = True
            del datas.credential_dic[id]

@app.route('/donations', methods = ['GET'])
def get_donations():

    global failed_donation

    if failed_donation:
        failed_donation = False
        return render_template('failed_donation.html')
    else:
        return render_template('already_donation.html')


@app.route('/redirect_url', methods = ['GET'])
def redirect_url():

    try:
        error = request.args.get('error', None)
        if error != None:
            return error

        id = request.args.get('state', None)
        if id == None:
            return 'No Id'

        store  = credentials_mgr.make_storage(id)

        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                   scope=SCOPES,
                                   redirect_uri='%s/redirect_url'% SERVER_URL)
        auth_code = request.args.get('code',None)
        credentials = flow.step2_exchange(auth_code)

        store.put(credentials)

        service = credentials_mgr.get_service(store)
        credentials_mgr.delete_all_files(service)
        folder_id = credentials_mgr.create_public_folder(service)

        cre_dic = json.loads(credentials.to_json())
        cre_dic['jigsaw_folder_id'] = folder_id
        cre_str = json.dumps(cre_dic)

        f = open(datas.credentials_path + '%s' % datas.credential_dic[id],'w') 
        f.write(cre_str)
        f.close()

        return render_template('donation_result.html')
    except:
        try:
            os.remove(datas.credentials_path + datas.credential_dic[id])
        except:
            pass
        try:
            del datas.credential_dic[id]
        except:
            pass

        return render_template('failed_donation.html')

@app.route('/credentials', methods =['DELETE'])
def credentials_delete():

    try:
        id = request.args.get('id', None)
        if id == None:
            id = 'anyone'

        store  = credentials_mgr.get_storage(id) 
        if store == None:
            return 'credentials not exist'

        credentials = store.get()
        if credentials == None:
            return 'already revoked'
        
        credentials.revoke(httplib2.Http())

        file_name = store._filename.split('/')[-1]
        end_file_name = util.get_end_credentials_name()
        if file_name != end_file_name:
            grouping_name = util.extract_grouping_name(file_name)
            datas.recover_que.put(grouping_name)

        datas.credential_dic.pop(id)

    except Exception as e:
        print(e)
        raise

    return 'revoked'

@app.route('/credentials', methods = ['GET'])
def credentials_all():

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
    local_datas = []

    credentials_files = os.listdir(datas.credentials_path)
    credentials_files.sort()

    if len(credentials_files) <= 0:
        return 'no credentials'

    for f in credentials_files:
        local_datas.append(f + '\n')

        j_file = open(datas.credentials_path + f , 'r')
        j_data = j_file.read()
        j_file.close()

        local_datas.append(j_data + '\n')

    return ''.join(local_datas)

@app.route('/credentials', methods = ['POST'])
def credentials_id():

    try:
        id = request.form['id']
        json_file = open(datas.credentials_path + datas.credential_dic[id], 'r')
        data = json_file.read()
        json_file.close()
        return data
    except Exception as e:
        return e


@app.route('/delete_all', methods = ['GET'])
def delete_all():
    
    credentials_files = os.listdir(datas.credentials_path) 

    print(str(len(credentials_files)))
    for cre in credentials_files:
        try:
            id = cre.split('_')[1].split('.')[0]
            store = credentials_mgr.get_storage(id)
            service = credentials_mgr.get_service(store)
            credentials_mgr.delete_all_files(service)
        except Exception as e:
            print(e)
            pass
            

    return 'del all'

if __name__ == '__main__':
    datas.load_credentials_dic()
    datas.load_recover_que()
    monitor.start_threading()
    app.run('0.0.0.0', 9991, debug=False)

