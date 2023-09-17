import os
import requests


server_url = 'http://185.205.246.39:5000'


def download_file(path):
    res = requests.post(server_url + '/get-file', data={'path': path})

    if res.status_code != 200:
        return 404

    if '.png' not in path:
        if os.path.exists(path):
            return 200

    folders = path.replace('/', '\\').split('\\')[:-1]

    dir = ''
    for folder in folders:
        dir += folder + '\\'

        if not os.path.exists(dir):
            os.mkdir(dir)

    with open(path, 'wb+') as f:
        f.write(res.content)

    return 200


def get_path(path, clips):
    while True:
        res = requests.post(server_url + '/get-path', data={'path': path})
        if res.json()['path'] not in clips:
            return res.json()['path']


def get_config():
    res = requests.get(server_url + '/get-config-main')

    return res.json()


if __name__ == '__main__':
    from pprint import pprint
    pprint(get_config())
