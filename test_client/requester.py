import webbrowser
import requests

SERVER_URL = 'http://1.234.65.53:9991'

def donate_id(id):

    post_data = {'id':id}
    r = requests.post("%s/donations" % SERVER_URL, post_data)

    url = r.url

    # MacOS
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

    # Windows
    # chrome_path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s'

    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'

    webbrowser.get(chrome_path).open(url)

def revoke_credentials(id):

    data = {'id':id}
    r = requests.delete("%s/credentials" % SERVER_URL, params=data)
    print(r.text)

def get_credentials():

    r = requests.get("%s/credentials" % SERVER_URL)
    print(r.text)
