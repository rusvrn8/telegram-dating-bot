import json
import os
import threading
import logging

from utils.exceptions import (
    DatabaseError,
    FileOperationError,
    UserNotFoundError,
    UserDataError
)

read_lock = threading.Lock()
write_lock = threading.Lock()


def load_from_json(file_path: str) -> dict:
    with read_lock:
        if not os.path.exists(file_path):
            return {}

        try:
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)

            if not isinstance(data, dict):
                logging.error(f"Invalid data type in {file_path}: {type(data)}")
                return {}

            return data
        except json.JSONDecodeError as e:
            raise FileOperationError(f"Ошибка чтения JSON файла {file_path}: {e}")
        except UnicodeDecodeError as e:
            raise FileOperationError(f"Ошибка кодировки в файле {file_path}: {e}")


def save_to_json(data: dict, file_path: str) -> None:
    try:
        with write_lock:
            try:
                temp_file = f"{file_path}.tmp"
                with open(temp_file, 'w', encoding="utf-8") as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=2)

                if os.path.exists(file_path):
                    backup_file = f"{file_path}.bak"
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(file_path, backup_file)

                os.rename(temp_file, file_path)

                if os.path.exists(f"{file_path}.bak"):
                    try:
                        os.remove(f"{file_path}.bak")
                    except:
                        pass

            except (IOError, OSError) as e:
                raise FileOperationError(f"Ошибка записи в файл {file_path}: {e}")
            except TypeError as e:
                raise FileOperationError(f"Ошибка сериализации данных: {e}")
    except FileOperationError:
        logging.error(f"Failed to save {file_path}")
        raise


class Database:
    def __init__(self, users_file: str, photos_file: str, likes_file: str):
        self.users_file = users_file
        self.photos_file = photos_file
        self.likes_file = likes_file

        try:
            self._users = load_from_json(users_file)
            self._photos = load_from_json(photos_file)
            self._likes = load_from_json(likes_file)
        except FileOperationError as e:
            logging.error(f"Failed to initialize database: {e}")
            self._users = {}
            self._photos = {}
            self._likes = {}

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
        try:
            save_to_json(self._users, self.users_file)
        except FileOperationError as e:
            logging.error(f"Failed to save users: {e}")
            raise DatabaseError("Не удалось сохранить данные пользователей")

    def save_photos(self) -> None:
        try:
            save_to_json(self._photos, self.photos_file)
        except FileOperationError as e:
            logging.error(f"Failed to save photos: {e}")
            raise DatabaseError("Не удалось сохранить данные фотографий")

    def save_likes(self) -> None:
        try:
            save_to_json(self._likes, self.likes_file)
        except FileOperationError as e:
            logging.error(f"Failed to save likes: {e}")
            raise DatabaseError("Не удалось сохранить данные лайков")

    def get_user(self, user_id: str) -> dict:
        if user_id not in self._users:
            raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")
        return self._users[user_id]

    def get_user_safe(self, user_id: str) -> dict | None:
        return self._users.get(user_id)

    def update_user(self, user_id: str, data: dict) -> None:
        if user_id not in self._users:
            raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")

        try:
            if not isinstance(data, dict):
                raise UserDataError("Данные должны быть словарем")

            for key, value in data.items():
                if value is not None:
                    self._users[user_id][key] = value
        except Exception as e:
            logging.error(f"Error updating user {user_id}: {e}")
            raise DatabaseError(f"Не удалось обновить данные пользователя: {e}")

    def add_user(self, user_id: str, user_data: dict) -> None:
        try:
            if not isinstance(user_data, dict):
                raise UserDataError("Данные пользователя должны быть словарем")

            required_fields = ['name', 'username', 'gender', 'age', 'goal', 'city']
            for field in required_fields:
                if field not in user_data:
                    raise UserDataError(f"Отсутствующее поле: {field}")

            if 'seen' not in user_data:
                user_data['seen'] = []

            self._users[user_id] = user_data
        except UserDataError:
            raise
        except Exception as e:
            logging.error(f"Error adding user {user_id}: {e}")
            raise DatabaseError(f"Не удалось добавить пользователя: {e}")

    def delete_user(self, user_id: str) -> None:
        try:
            if user_id in self._users:
                del self._users[user_id]
            if user_id in self._photos:
                del self._photos[user_id]
            if user_id in self._likes:
                del self._likes[user_id]
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")
            raise DatabaseError(f"Не удалось удалить пользователя: {e}")

    def add_photo(self, user_id: str, photo_file_id: str) -> None:
        try:
            if not photo_file_id or not isinstance(photo_file_id, str):
                raise UserDataError("Некорректный идентификатор фотографии")

            self._photos[user_id] = photo_file_id

            if user_id in self._users:
                self._users[user_id]['photo'] = photo_file_id
        except UserDataError:
            raise
        except Exception as e:
            logging.error(f"Error adding photo for user {user_id}: {e}")
            raise DatabaseError(f"Не удалось добавить фотографию: {e}")

    def add_like(self, user_id: str, liked_user_id: str) -> None:
        try:
            if not liked_user_id or not isinstance(liked_user_id, str):
                raise UserDataError("Некорректный идентификатор пользователя")

            if user_id not in self._likes:
                self._likes[user_id] = {'likes': [], 'seen': []}

            if liked_user_id in self._likes[user_id]['likes']:
                return

            self._likes[user_id]['likes'].append(liked_user_id)
        except UserDataError:
            raise
        except Exception as e:
            logging.error(f"Error adding like from {user_id} to {liked_user_id}: {e}")
            raise DatabaseError(f"Не удалось добавить лайк: {e}")

    def mark_like_seen(self, user_id: str, liked_user_id: str) -> None:
        try:
            if user_id in self._likes:
                if liked_user_id not in self._likes[user_id]['seen']:
                    self._likes[user_id]['seen'].append(liked_user_id)
        except Exception as e:
            logging.error(f"Error marking like as seen: {e}")

    def has_mutual_like(self, user_id: str, other_user_id: str) -> bool:
        try:
            return (user_id in self._likes and
                    other_user_id in self._likes[user_id]['likes'] and
                    other_user_id in self._likes and
                    user_id in self._likes[other_user_id]['likes'])
        except Exception as e:
            logging.error(f"Error checking mutual like: {e}")
            return False

    def get_users_count(self) -> int:
        return len(self._users)


def load_regions(file_path: str) -> tuple:
    try:
        if not os.path.exists(file_path):
            logging.warning(f"Regions file not found: {file_path}")
            return ()

        with open(file_path, 'r', encoding="utf-8") as file:
            regions_list = file.readlines()
            return tuple(elem.replace('\n', '') for elem in regions_list if elem.strip())
    except UnicodeDecodeError as e:
        logging.error(f"Encoding error in regions file: {e}")
        return ()
    except Exception as e:
        logging.error(f"Error loading regions: {e}")
        return ()
