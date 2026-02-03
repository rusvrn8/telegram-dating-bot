import json
import os
import threading

read_lock = threading.Lock()
write_lock = threading.Lock()


def load_from_json(file_path: str) -> dict:
    with read_lock:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            return data
        return {}


def save_to_json(data: dict, file_path: str) -> None:
    with write_lock:
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)


class Database:
    def __init__(self, users_file: str, photos_file: str, likes_file: str):
        self.users_file = users_file
        self.photos_file = photos_file
        self.likes_file = likes_file
        self._users = load_from_json(users_file)
        self._photos = load_from_json(photos_file)
        self._likes = load_from_json(likes_file)

    @property
    def users(self) -> dict:
        return self._users

    @property
    def photos(self) -> dict:
        return self._photos

    @property
    def likes(self) -> dict:
        return self._likes

    def save_users(self) -> None:
        save_to_json(self._users, self.users_file)

    def save_photos(self) -> None:
        save_to_json(self._photos, self.photos_file)

    def save_likes(self) -> None:
        save_to_json(self._likes, self.likes_file)

    def get_user(self, user_id: str) -> dict:
        return self._users.get(user_id)

    def update_user(self, user_id: str, data: dict) -> None:
        if user_id in self._users:
            self._users[user_id].update(data)

    def add_user(self, user_id: str, user_data: dict) -> None:
        self._users[user_id] = user_data

    def delete_user(self, user_id: str) -> None:
        self._users.pop(user_id, None)
        self._photos.pop(user_id, None)
        self._likes.pop(user_id, None)

    def add_photo(self, user_id: str, photo_file_id: str) -> None:
        self._photos[user_id] = photo_file_id
        if user_id in self._users:
            self._users[user_id]['photo'] = photo_file_id

    def add_like(self, user_id: str, liked_user_id: str) -> None:
        if user_id not in self._likes:
            self._likes[user_id] = {'likes': [], 'seen': []}
        self._likes[user_id]['likes'].append(liked_user_id)

    def mark_like_seen(self, user_id: str, liked_user_id: str) -> None:
        if user_id in self._likes and liked_user_id not in self._likes[user_id]['seen']:
            self._likes[user_id]['seen'].append(liked_user_id)

    def has_mutual_like(self, user_id: str, other_user_id: str) -> bool:
        return (user_id in self._likes and
                other_user_id in self._likes[user_id]['likes'] and
                other_user_id in self._likes and
                user_id in self._likes[other_user_id]['likes'])

    def get_users_count(self) -> int:
        return len(self._users)


def load_regions(file_path: str) -> tuple:
    with open(file_path, 'r', encoding="utf-8") as file:
        regions_list = file.readlines()
        return tuple(elem.replace('\n', '') for elem in regions_list)
