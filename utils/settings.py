import json


def get_settings(id):
    path = id + ".json"
    json_file = open(path)

    settings = json.load(json_file)

    return settings


if __name__ == '__main__':
    id = 'config'

    from pprint import pprint
    settings = get_settings(id)

    pprint(settings)