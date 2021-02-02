# Users management
REF_KEY_LEN = 16
GOODS_LIST_LEN = 3

QRY_CREATE_USERS_TABLE = f"""
    CREATE TABLE IF NOT EXISTS Users (
        id  BIGINT PRIMARY KEY NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        referee BIGINT,
        refkey VARCHAR({int(REF_KEY_LEN)}) NOT NULL,
        balance NUMERIC(20,2) DEFAULT 0 NOT NULL
    );
 """

QRY_ADD_USER = """
    INSERT INTO users(id, name, email, referee, refkey) VALUES ($1, $2, $3, $4, $5)
    RETURNING id;
"""

QRY_GET_USER_INFO = "SELECT name, email, refkey, balance FROM users WHERE id=$1;"

QRY_GET_REFERRALS = "SELECT id, name FROM users WHERE referee=$1;"

QRY_GET_REFEREE = "SELECT id, name FROM users WHERE refkey=$1;"

QRY_GET_BALANCE = "SELECT balance FROM users WHERE id = $1"

QRY_UPDATE_BALANCE = """UPDATE users SET balance=balance+$1 WHERE id = $2
    RETURNING balance
"""

# Goods management

QRY_CREATE_GOODS_TABLE = """
    CREATE TABLE IF NOT EXISTS Goods (
        id SERIAL PRIMARY KEY NOT NULL,
        name VARCHAR(255) NOT NULL,
        price NUMERIC(20,2) NOT NULL, 
        descr VARCHAR(512),
        photo_url VARCHAR(512),
        photo BYTEA,
        file_id VARCHAR(255)
    );
"""

QRY_ADD_GOOD = """
    INSERT INTO Goods(name, price, descr, photo_url, photo, file_id) VALUES($1, $2, $3, $4, $5, $6)
    RETURNING id;
"""

QRY_DEL_GOOD = "DELETE FROM Goods WHERE id=$1"

QRY_GET_GOOD = """
    SELECT name, price, descr, photo_url, photo, file_id FROM Goods WHERE id=$1
"""

QRY_GET_ALL_GOODS = """
    SELECT id, name, price FROM Goods ORDER BY name
"""

QRY_GET_GOODS_LIKE = f"""
    SELECT id, name, price, photo_url, photo, file_id FROM Goods 
    WHERE UPPER(name) LIKE $1 ORDER BY name LIMIT {int(GOODS_LIST_LEN)}
"""