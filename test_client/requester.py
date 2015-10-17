import webbrowser
import requests

def donate_id(id):

    post_data = {'id':id}
    r = requests.post("http://54.64.113.34:9991/donations", post_data)

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
    r = requests.delete("http://54.64.113.34:9991/credentials", params=data)
    print(r.text)

def get_credentials():

    r = requests.get("http://54.64.113.34:9991/credentials")
    print(r.text)
