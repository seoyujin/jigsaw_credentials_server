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

    group_info = None
    cre_obj = None
    store = None

    try:
        error = request.args.get('error', None)
        if error != None:
            return error

        id = request.args.get('state', None)
        if id == None:
            return 'No Id'

        store, group_info, cre_obj  = credentials_mgr.make_storage(id)

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

    except:
        cre_obj.set_recovery_wait_state()
        cre_obj.set_id_credentials_name('','')

        end_group_info = datas.credentials_list[-1]
        if group_alphabet == end_group_info.group_alphabet_:
            state = datas.CredentialsInfo.STATE_RECOVERY_WAIT
            for cre in end_group_info.credentials_list:
                if cre.get_state() == datas.CredentialsInfo.STATE_USABLE:
                    state = cre.get_state
                    break
            if state == datas.CredentialsInfo.STATE_USABLE:
                datas.credentials_list.pop()

        try:
            os.remove(datas.credentials_path + datas.credential_dic[id])
        except:
            pass
        try:
            del datas.credential_dic[id]
        except:
            pass

        return render_template('failed_donation.html')

    if cre_obj.get_state() == datas.CredentialsInfo.STATE_RECOVERY_WAIT:
        fp = open('./recover_list.txt', 'a')
        fp.write(store._filename.rsplit('/',1)[-1] + '\n')
        fp.close
        cre_obj.set_recovering_state()

    cre_obj.set_id_credentials_name(id, store._filename.split('/')[-1])
    group_info.compute_group_state()
    return render_template('donation_result.html')

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
    except Exception as e:
        return 'revoke fail : ' + e

    try:
        file_name = store._filename.split('/')[-1]
        group_name = util.extract_grouping_name(file_name)
        group_alphabet = group_name[:-1]
                
        group_info = None
        for g_info in datas.credentials_list:
            if g_info.group_alphabet_ == group_alphabet:
                group_info = g_info
        
        if group_info == None:
            return 'revoked.'

        for cre in group_info.credentials_list:
            if cre.get_group_name() == group_name:
                cre.set_recovery_wait_state()
                cre.set_id_credentials_name('','')

        group_info.compute_group_state()

        end_group_info = datas.credentials_list[-1]
        if group_alphabet == end_group_info.group_alphabet_:
            state = datas.CredentialsInfo.STATE_RECOVERY_WAIT
            for cre in end_group_info.credentials_list:
                if cre.get_state() == datas.CredentialsInfo.STATE_USABLE:
                    state = cre.get_state()
                    break
            if state != datas.CredentialsInfo.STATE_USABLE:

                for cre in end_group_info.credentials_list:
                    try:
                        os.remove(datas.credentials_path + cre.get_credentials_name())
                    except:
                        pass

                datas.credentials_list.pop()

        datas.credential_dic.pop(id)

    except Exception as e:
        print(e)
        return 'revoked..'

    return 'revoked'

@app.route('/credentials', methods = ['GET'])
def credentials_all():

    local_datas = ['']

    sort_list = list(datas.credentials_list)

    if len(sort_list) <= 0:
        return 'no credentials'

    p_val = 10000000000 * 2
    sort_list = sorted( sort_list, key=lambda e: (e.get_usable_state()* p_val) + e.compute_usable_quota())
    sort_list.reverse()
    for group in sort_list:
        if group.get_usable_state() == datas.GroupInfo.STATE_DISABLE_GROUP:
            break
        for cre in group.credentials_list:
            local_datas.append(cre.get_credentials_name() + '\n')

            j_file = open(datas.credentials_path + cre.get_credentials_name() , 'r')
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
    datas.load_credentials_list()
    monitor.start_threading()
    app.run('0.0.0.0', 9991, debug=False)

