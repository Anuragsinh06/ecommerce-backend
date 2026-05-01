import asyncpg
import json
from config.config import settings

class Database:
    def __init__(self):
        self._pool = None

    async def connect(self):
        if not self._pool:
            try:
                # Initializing the pool
                self._pool = await asyncpg.create_pool(
                    settings.DATABASE_URL,
                    min_size=5,
                    max_size=20
                )
                print("Database connection pool established")
            except Exception as e:
                print(f" Error connecting to database: {e}")
                raise e

    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
            print("Database connection pool closed")

    async def fetchrow(self, query, *args):
        # Safety check to prevent NoneType error
        if self._pool is None:
            raise RuntimeError("DB Pool not initialized. Call db.connect() first.")
        
        async with self._pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def execute(self, query, *args):
     async with self._pool.acquire() as connection:
        return await connection.execute(query, *args)

    async def call_function(self, function_name: str, *args):
        args_str = ", ".join([f"${i + 1}" for i in range(len(args))])
        query = f"SELECT {function_name}({args_str})"
        
        row = await self.fetchrow(query, *args)
        if row and row[0]:
            if isinstance(row[0], str):
                return json.loads(row[0])
            return row[0]
        return None

# Global instance
db = Database()