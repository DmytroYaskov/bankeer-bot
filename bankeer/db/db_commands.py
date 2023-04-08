import aiosqlite
import asyncio
import logging
import os


class DatabaseManager:
    def __init__(self, db_name, main_table, mcc_table) -> None:
        self.db_name = db_name
        self.main_table = main_table
        self.mcc_table = mcc_table

    async def create_main_table(self):
        """
        Creates the main table for storing transactional data.
        TODO - pass a table name - to make code more configurable and parametrizable
        """
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                f"""
            CREATE TABLE IF NOT EXISTS {self.main_table}(
            account TEXT,
            transaction_id TEXT UNIQUE PRIMARY KEY,
            transaction_time INTEGER,
            description TEXT,
            mcc INTEGER FOREIGN KEY,
            original_mcc INTEGER,
            amount REAL,
            operation_amount REAL,
            currency_code TEXT,
            balance REAL,
            system_reached_time DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
            );
            """
            )
            await conn.commit()

    async def create_mcc_table(self):
        """
        Creates table with MCC codes information.
        """
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                f"""
            CREATE TABLE IF NOT EXISTS {self.mcc_table}(
            description_en TEXT UNIQUE PRIMARY KEY,
            description_ua TEXT
            );    
            """
            )

    async def drop_table(self, table):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                f"""
                DROP TABLE IF EXISTS {table};
                """
            )
            await conn.commit()

    async def write_transactions_data(self, data, account_id):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                """
                INSERT INTO transactions_data
                (account, transaction_id, transaction_time, description, mcc, original_mcc, amount, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict (transaction_id) do nothing
                """,
                (account_id, data["transaction_id"], data["transaction_time"], data["description"],
                 data["mcc"], data["mcc_text"], data["amount"], data["balance"])
            )

            await conn.commit()
            return conn.total_changes
        
    async def write_mcc_data(self, data):
        async with aiosqlite.connect(self.db_name) as conn:
            # clist = [("Agricultural services", "Сільськогосподарські послуги", ),
            #          ("Contracted services", "Послуги за контрактом", ), 
            #          ("Transportation", "Транспортні послуги", ), 
            #          ("Utilities", "Комунальні послуги", ),
            #          ("Retail outlets", "Роздрібні магазини", ),
            #          ("Clothing outlets", "Магазини одягу", ),
            #          ("Miscellaneous outlets", "Інші магазини")

                     
                    # ]
            await conn.executemany(
                f"""
                INSERT INTO {self.mcc_table}
                (description_en, description_ua)
                VALUES (?, ?)
                """,
                


            )

    async def get_transactions_data_db(self):
        async with aiosqlite.connect("CashFlow.db") as conn:
            selected_data = await conn.execute(
                """
                SELECT * FROM transactions_data
                """
            )
            await conn.commit()


if __name__ == '__main__':
    DB_NAME = os.environ["DATABASE_NAME"]
    TABLE_NAME = os.environ["TABLE_NAME"]
    MCC_TABLE = os.environ["MCC_"]

    db_manager = DatabaseManager(DB_NAME, TABLE_NAME, )

    async def main():
        # await db_manager.drop_table()
        await db_manager.create_main_table()


    asyncio.run(main())
    