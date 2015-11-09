import threading
import time
from apiclient import errors
import os
import credentials_mgr
import datas
import util


def monitor():

    while True:
        lock = threading.Lock()
        lock.acquire()
        sort_list = list(datas.credentials_list)
        lock.release()

        for group_info in sort_list:

            print('. . . . . . . . . . . . . . . . . . . . . . . . . . . .  .\n')
            print('group alphabet : ' + group_info.group_alphabet_)
            print('group qouta : ' + str(group_info.compute_usable_quota()))
            if group_info.get_usable_state() == datas.GroupInfo.STATE_USBLE_GROUP:
                print('group state : usable group')
            else:
                print('group state : disable group')
            print('\n')

            for cre in group_info.credentials_list:
                print('credentials group name :' + cre.get_group_name())
                print('credentials uer id : ' + cre.get_user_id())
                print('credentials file name : ' + cre.credentials_name_)
                print('credentials usable quota : ' + str(cre.compute_usable_quota()))
                if cre.get_state() == datas.CredentialsInfo.STATE_USABLE:
                    print('credentials state : usable credentials')
                elif cre.get_state() == datas.CredentialsInfo.STATE_RECOVERY_WAIT:
                    print('credentials state : recovery wait credentials')
                elif cre.get_state() == datas.CredentialsInfo.STATE_RECOVERING:
                    print('credentials state : recovering credentials')
                print('\n')
        print('======================================================================\n') 

        
        time.sleep(10)

def start_threading():
    threading.Timer(1.0,monitor).start()

