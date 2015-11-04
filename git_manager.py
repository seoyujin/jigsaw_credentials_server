from git import Repo

def add(file_name):

    fname = file_name.split('/')[-1]
    
    repo = Repo('./datas/')
    filepath = 'credentials/' + fname
    repo.index.add([filepath])
    repo.index.commit('donate credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()

def remove(file_name):

    fname = file_name.split('/')[-1]

    repo = Repo('./datas/')
    filepath = 'credentials/' + fname
    repo.index.remove([filepath])
    repo.index.commit('revoke credentials - %s' % filepath)
    push_info = repo.remotes.origin.push()
