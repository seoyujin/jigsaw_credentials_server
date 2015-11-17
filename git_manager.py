from git import Repo

def add():

    repo = Repo('./datas/server_url/')
    repo.index.add(['index.html'])
    repo.index.commit('url_change...')
    push_info = repo.remotes.origin.push()

def pull():
    repo = Repo('./datas/server_url/')
    push_info = repo.remotes.origin.pull()

def remove(file_name):

    fname = file_name.split('/')[-1]
    repo = Repo('./datas/')
    filepath = 'credentials/' + fname
    repo.index.remove([filepath])
    repo.index.commit('revoke credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()

def recover_add():

    repo = Repo('./')
    repo.index.add(['recover_list.txt'])
    repo.index.commit('recover file change...')
    push_info = repo.remotes.origin.push()

def recover_pull():

    repo = Repo('./')
    push_info = repo.remotes.origin.pull()

def garbage_add():

    os_path = '/home/yujin/jigsaw_credentials_server/'
    repo = Repo(os_path)
    repo.index.add(['garbage.txt'])
    repo.index.commit('garbage file change...')
    push_info = repo.remotes.origin.push()


