import json
import os
import threading


read_lock = threading.Lock()
write_lock = threading.Lock()


def load_from_json(file_path):
    with read_lock:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        return {}


def save_to_json(data, file_path):
    with write_lock:
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)


users_file_path = 'users.json'

users = load_from_json(users_file_path)
users_new = load_from_json('users_count.json')

users_lst = set(users.keys())
users_new_lst = set(users_new.keys())

res = list(users_new_lst - users_lst)

users_res = {key: users_new[key] for key in res}

if __name__ == '__main__':
    # print(f"Users count - {len(res)}")
    # save_to_json(users_res, 'users_new.json')
    # count_female = 0
    # count_male = 0
    # for key in res:
    #     if users_res[key]['gender'] == 'Девушка':
    #         count_female += 1
    #     elif users_res[key]['gender'] == 'Парень':
    #         count_male += 1
    #
    # print(f"Девушка - {count_female}, Парень - {count_male}")
    del_list = []
    print(len(users_new))
    for key in users_lst:
        if users[key]['city'] == 'Воронежская область':
            del_list.append(key)
            # users_new.pop(key)

    print(len(del_list))
    # print(len(users_new))
    # save_to_json(users_new, 'users_count.json')