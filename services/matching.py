import logging
import random


def filter_users(fil_key: str, fil_val, users: dict, user_id: str) -> set:
    logging.info(f'Filtering users by {fil_key}={fil_val}')

    if fil_val and isinstance(fil_val, str):
        filtered = {u for u in users if
                    u != user_id and
                    u not in users[user_id]['seen'] and
                    users[u][fil_key] == fil_val}
    elif fil_val and isinstance(fil_val, list):
        filtered = {u for u in users if
                    u != user_id and
                    u not in users[user_id]['seen'] and
                    users[u][fil_key] in fil_val}
    else:
        filtered = {u for u in users if u != user_id and u not in users[user_id]['seen']}

    return filtered


class MatchingService:
    def __init__(self, database):
        self.db = database

    def find_random_user(self, user_id: str, filters: dict) -> str | None:
        unseen_users = {u for u in self.db.users if u != user_id and u not in self.db.users[user_id]['seen']}

        if not filters:
            return random.choice(list(unseen_users)) if unseen_users else None

        filters_to_apply = [
            ('gender', filters.get('filter_gender')),
            ('goal', filters.get('filter_goal')),
            ('city', filters.get('filter_region')),
            ('age', filters.get('filter_age'))
        ]

        for key, value in filters_to_apply:
            if value:
                filtered = filter_users(key, value, self.db.users, user_id)
                unseen_users.intersection_update(filtered)

        return random.choice(list(unseen_users)) if unseen_users else None

    def mark_as_seen(self, user_id: str, seen_user_id: str) -> None:
        if user_id in self.db.users:
            self.db.users[user_id]['seen'].append(seen_user_id)


class LikeService:
    def __init__(self, database):
        self.db = database

    def add_like(self, user_id: str, liked_user_id: str) -> bool:
        self.db.add_like(user_id, liked_user_id)
        return self._check_mutual_like(user_id, liked_user_id)

    def _check_mutual_like(self, user_id: str, other_user_id: str) -> bool:
        return self.db.has_mutual_like(user_id, other_user_id)

    def mark_like_as_seen(self, user_id: str, liked_user_id: str) -> None:
        self.db.mark_like_seen(user_id, liked_user_id)

    def get_new_mutual_likes(self, user_id: str) -> list:
        if user_id not in self.db.likes:
            return []

        mutual_likes = []
        for like_user_id in self.db.likes[user_id]['likes']:
            if (like_user_id not in self.db.likes[user_id]['seen'] and
                self._check_mutual_like(user_id, like_user_id)):
                mutual_likes.append(like_user_id)

        return mutual_likes
