import os


async def is_admin(user_id: int):
    admins = list(map(int, os.getenv('ADMINS').split(',')))
    return user_id in admins
