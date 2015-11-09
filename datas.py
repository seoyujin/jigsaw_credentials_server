import queue
import os
import util
import credentials_mgr

credential_dic ={}
credentials_list = []

credentials_path = './datas/credentials/'

class CredentialsInfo:
    STATE_USABLE        = 0
    STATE_RECOVERY_WAIT = 1
    STATE_RECOVERING    = 2

    def __init__(self, group_name):
        self.user_id_ = ''
        self.group_name_ = group_name
        self.credentials_name_ = ''
        self.state_ = CredentialsInfo.STATE_RECOVERY_WAIT  # 0: usable, 1: recovery_wait, 2: recovering
        if group_name[-1] == '0':
            self.state_ = CredentialsInfo.STATE_USABLE

    def get_user_id(self):
        return  self.user_id_ 

    def get_credentials_name(self):
        return self.credentials_name_
    
    def set_id_credentials_name(self, id, cre_file_name):
        self.user_id_ = id
        self.credentials_name_ = cre_file_name

    def get_group_name(self):
        return self.group_name_

    def get_state(self):
        return self.state_

    def set_usable_state(self):
        self.state_ = CredentialsInfo.STATE_USABLE

    def set_recovery_wait_state(self):
        self.state_ = CredentialsInfo.STATE_RECOVERY_WAIT

    def set_recovering_state(self):
        self.state_ = CredentialsInfo.STATE_RECOVERING

    def compute_usable_quota(self):
        global credentials_path

        if self.user_id_ == '':
            return 0

        store = credentials_mgr.get_storage(self.user_id_)
        if store == None:
            print(self.user_id_ + ' compute_usable_quota() error : no storage')
            return 0

        try:
            service = credentials_mgr.get_service(store)       

            about = service.about().get().execute()

            total_quota = int(about['quotaBytesTotal'])
            used_quota  = int(about['quotaBytesUsed'])
            return total_quota - used_quota

        except Exception as e:
            print(self.user_id_ + ' compute_usalble_quota() error : ')
            print(e)

            try:
                os.remove(credentials_path + self.get_credentials_name())
                self.set_id_credentials_name('','')
            except Exception as er:
                print(er)
                pass
            return 0

class GroupInfo:

    STATE_USBLE_GROUP = 1
    STATE_DISABLE_GROUP = 0
    MINIMUM_VALUE = 15<<30 # 16106127360

    def __init__(self, group_alphabet):
        self.usable_state_ = GroupInfo.STATE_DISABLE_GROUP
        self.group_alphabet_ = group_alphabet
        self.usable_quota_ = 0
        self.credentials_list =[ CredentialsInfo(group_alphabet + '0'), CredentialsInfo(group_alphabet + '1'), CredentialsInfo(group_alphabet + '2')]

    def get_usable_state(self):
        return self.usable_state_ 

    def compute_group_state(self):
        
        for cre in self.credentials_list:
            if CredentialsInfo.STATE_USABLE != cre.get_state():
                self.usable_state_ = GroupInfo.STATE_DISABLE_GROUP
                return

        self.usable_state_ = GroupInfo.STATE_USBLE_GROUP
        

    def get_usable_quota(self):
        return self.usable_quota_

    def compute_usable_quota(self):

        try:
            minimum = GroupInfo.MINIMUM_VALUE

            for cre in self.credentials_list:
                cre_quota = cre.compute_usable_quota()
                if minimum > cre_quota:
                    minimum = cre_quota

            self.usable_quota_ = minimum
            return minimum

        except Exception as e:
            print(e)
            #print(self.group_alphabet_ + ' : ' + e)
            return 0


def load_credentials_dic():
    
    global credential_dic

    credentials_list = os.listdir(credentials_path)

    for file_name in credentials_list:
        id = file_name.split('_', 1)[1].rsplit('.', 1)[0]
        credential_dic[id] = file_name
        

def load_credentials_list():

    credentials_list = os.listdir(credentials_path)
    credentials_list.sort()

    if len(credentials_list) <= 0 :
        return None

    group_dic = {}
    max_count = 0
    last_group_name = util.extract_grouping_name(credentials_list[-1])

    for cre in credentials_list:
        group_name = util.extract_grouping_name(cre) 
        name_count = count_alphabet(group_name)
        if max_count <  name_count:
            max_count = name_count 
        group_dic[group_name] = cre

    group_alphabet = 'a'
    while True:
        recover_group(group_alphabet, max_count, group_dic)
        if group_alphabet == last_group_name[0]:
            break
        group_alphabet = chr(ord(group_alphabet)+1)


def recover_group(group_alphabet, max_count, group_dic):

    global credentials_list

    cur_group_name = group_alphabet + '0' 

    for i in range(max_count):
        group_info = GroupInfo(cur_group_name[:-1])
        credentials_list.append(group_info)
        
        for k in range(3):
            cre_info = group_info.credentials_list[k] 
            cre_info.group_name_ = cur_group_name
            if cur_group_name not in group_dic:
                cre_info.set_recovery_wait_state()
            else:
                cre_info.set_usable_state()
                id = group_dic[cur_group_name].split('_')[1].split('.')[0]
                cre_info.set_id_credentials_name(id, group_dic[cur_group_name])
            cur_group_name = name_next_group_alphabet(cur_group_name)
        group_info.compute_group_state()


def count_alphabet(grouping_name):
    return len(grouping_name) -1


def name_next_group_alphabet(cur_gr_name):
    alphabet_part = cur_gr_name[:-1]
    no_part       = int(cur_gr_name[-1])

    if no_part < 2:
        return '%s%d' % (alphabet_part, no_part+1)
    else:
        return '%s%s0' % (alphabet_part, alphabet_part[0])

