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


if __name__ == '__main__':
    add()
