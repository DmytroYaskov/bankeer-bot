import sqlite3
import aiosqlite
import asyncio


# async def create_table():
#     """
#     Creates the main table for storing transactional data.
#     TODO - pass a table name - to make code more configurable and parametrizable
#     """
#     async with aiosqlite.connect("test.db") as conn:
#         cursor_ = conn.cursor()
#         cursor_.execute(
#         """
#         CREATE TABLE IF NOT EXISTS transactions_data3
#         (
#         account TEXT PRIMARY KEY,
#         transaction_id TEXT,
#         transaction_time INTEGER,
#         description TEXT,
#         mcc INTEGER,
#         original_mcc INTEGER,
#         amount REAL,
#         operation_amount REAL,
#         currency_code TEXT,
#         balance REAL,
#         system_reached_time INTEGER
#         )
#         """
#         )
#         conn.commit()


async def write_transactions_data(data):
    async with aiosqlite.connect("test.db") as conn:
        await conn.execute(
            """
            INSERT INTO transactions_data2
            (transaction_id, transaction_time, description, mcc, original_mcc, amount, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (data["transaction_id"], data["transaction_time"], data["description"],
            data["mcc"], data["mcc_text"], data["amount"], data["balance"] )
        )
        await conn.commit()

# def get_transactions_data_db():
#     with sqlite3.connect("test.db") as conn:
#         cursor_ = conn.cursor()
#         selected_data = cursor_.execute(
#             """
#             SELECT * FROM transactions_data3
#             """
#             ).fetchall()
#          conn.commit()
