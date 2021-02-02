from io import BytesIO
from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

from .sql import *


class Database:
    def __init__(self):
        """Создается база данных без подключения в loader"""

        self.pool: Union[Pool, None] = None

    async def create(self):
        """В этой функции создается подключение к базе"""

        pool = await asyncpg.create_pool(
            user=config.PGUSER,  # Пользователь базы (postgres или ваше имя), для которой была создана роль
            password=config.PGPASSWORD,  # Пароль к пользователю
            host=config.ip,  # Ip адрес базы данных. Если локальный компьютер - localhost, если докер - название сервиса
            database=config.DATABASE  # Название базы данных. По умолчанию - postgres, если вы не создавали свою
        )
        self.pool = pool

# User management functions
    async def create_table_users(self):
        await self.pool.execute(QRY_CREATE_USERS_TABLE)

    async def get_user_info(self, id: int):
        return await self.pool.fetchrow(QRY_GET_USER_INFO, id)

    async def get_referee(self, ref_key: str):
        if len(ref_key) != REF_KEY_LEN:
            return None
        return await self.pool.fetchval(QRY_GET_REFEREE, ref_key)

    async def get_balance(self, id: int):
        return await self.pool.fetchval(QRY_GET_BALANCE, id)

    async def add_user(self, id: int, username: str, ref_key: str, referee: int=None, email: str=None):
        return await self.pool.fetchval(QRY_ADD_USER, id, username, email, referee, ref_key)

    async def add_money(self, id: int, amount: float):
        await self.pool.execute(QRY_UPDATE_BALANCE, amount, id)

# Goods management functions
    async def create_table_goods(self):
        await self.pool.execute(QRY_CREATE_GOODS_TABLE)

    async def delete_good(self, id: int):
        await self.pool.execute(QRY_DEL_GOOD, id)

    async def add_good(self, name: str, price: float, descr: str = None, photo_url: str=None,
                       file_id: str=None, photo: BytesIO = None):
        return await self.pool.fetchval(QRY_ADD_GOOD, name, price, descr, photo_url, photo, file_id)

    async def get_good(self, id: int):
        return await self.pool.fetchrow(QRY_GET_GOOD, id)

    async def get_all_goods(self):
        return await self.pool.fetch(QRY_GET_ALL_GOODS)

    async def get_goods_like(self, name: str):
        return await self.pool.fetch(QRY_GET_GOODS_LIKE, name+'%')



    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num + 1}" for num, item in enumerate(parameters)
        ])
        return sql, tuple(parameters.values())



    async def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return await self.pool.fetch(sql)

    async def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = f"""
        SELECT * FROM Users WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.pool.fetchrow(sql, *parameters)

    async def count_users(self):
        return await self.pool.fetchval("SELECT COUNT(*) FROM Users")

    async def update_user_email(self, email, id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET email=$1 WHERE id=$2
        """
        return await self.pool.execute(sql, email, id)

    async def delete_users(self):
        await self.pool.execute("DELETE FROM Users WHERE TRUE")
