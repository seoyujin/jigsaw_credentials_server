import threading
import time
from apiclient import errors
import os
import credentials_mgr
import datas
import util


def recover():

    while True:


    if cre_obj.get_state() == datas.CredentialsInfo.STATE_RECOVERY_WAIT:
        fp = open('./recover_list.txt', 'a')
        fp.write(store._filename.rsplit('/',1)[-1] + '\n')
        fp.close
        cre_obj.set_recovering_state()

        term = 5
        time.sleep(term)

def start_threading():
    threading.Timer(1.0, recover).start()

