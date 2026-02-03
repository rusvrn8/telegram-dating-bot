import random
from faker import Faker
import json

def save_to_json(data, file_path):
    with open(file_path, 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False)

with open('regions_rf.txt', 'r', encoding="utf-8") as file:
    regions_list = file.readlines()
    regions = tuple(elem.replace('\n', '') for elem in regions_list)

goals = ["Общение", "Дружба", "Интим", "Отношения"]
genders = ["Парень", "Девушка"]

fake = Faker()
fake_ru = Faker("ru_RU")


if __name__ == '__main__':
    data_gen_m = {}
    for i in range(3700302188, 3700302188 + 5000):
        name = fake_ru.first_name_male()
        username = fake.first_name_male().lower()
        data_gen_m[str(i)] = {
            "name": name,
            "username": "@" + username + str(random.randint(5, 99)),
            "gender": "Парень",
            "age": str(random.randint(16, 45)),
            "goal": random.choice(goals),
            "city": random.choice(regions),
            "photo": None,
            "seen": []
        }

    data_gen_f = {}
    for i in range(3700302188 + 5001, 3700302188 + 10000):
        name = fake_ru.first_name_female()
        username = fake.first_name_female().lower()
        data_gen_f[str(i)] = {
            "name": name,
            "username": "@" + username + str(random.randint(5, 99)),
            "gender": "Девушка",
            "age": str(random.randint(16, 45)),
            "goal": random.choice(goals),
            "city": random.choice(regions),
            "photo": None,
            "seen": []
        }

    data_gen_m.update(data_gen_f)

    save_to_json(data_gen_m, 'users.json')
