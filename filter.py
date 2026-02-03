import json
import os
import threading

users_file_path = 'users_test.json'
read_lock = threading.Lock()

def load_from_json(file_path):
    with read_lock:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        return {}

users = load_from_json(users_file_path)

def filter(fil_key, fil_val, users_dict, user_id):
    filter_users = {u for u in users_dict if u != user_id and u not in users_dict[user_id]['seen'] and users_dict[u][fil_key] == fil_val}
    return filter_users


dct = [{'gender': 'Девушка'}, {'goal': 'Дружба'}]

res_list = {u for u in users}
for elem in dct:
    for key in list(elem.keys()):
        filter_list = filter(key, elem.get(key), users, "447731007")
        res_list.intersection_update(filter_list)

print(res_list)