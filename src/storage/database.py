import os
from datetime import datetime, timedelta, timezone
from typing import Any
from aiosqlite import Connection, Row, connect, DatabaseError
from utils.constants import (
    INSERT_SUMMARY,
    SELECT_CONTENT_SUMMARY,
    INSERT_CONTENT,
    SELECT_LAST_FETCH_TIME,
    CREATE_SOURCE_TABLE,
    CREATE_CONTENT_TABLE,
    CREATE_SUMMARY_TABLE,
    SELECT_ALL_SOURCES,
    SELECT_SOURCE_NAMES,
    INSERT_SOURCE,
    SELECT_CONTENT_BY_ID,
)


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db: Connection | None = None

    async def connect(self):
        self.db = await connect(self.db_path)
        self.db.row_factory = Row
        return self

    async def close(self):
        if self.db:
            await self.db.close()
            self.db = None

    async def execute(
        self, query: str, commit: bool = False, params: tuple[Any, ...] = ()
    ):
        if self.db is None:
            raise RuntimeError(
                "Database not initialized. Use 'async with' context manager."
            )

        try:
            cursor = await self.db.execute(query, params)
            if commit:
                await self.db.commit()
            return cursor
        except Exception as e:
            print(f"❌ DB Error: {e}")
            raise DatabaseError("Something went wrong")

    async def initialize_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        await self.connect()

        await self.execute(CREATE_SOURCE_TABLE, True, ())
        await self.execute(CREATE_CONTENT_TABLE, True, ())
        await self.execute(CREATE_SUMMARY_TABLE, True, ())

        print(f"✅ Database is initialized succesfully at {self.db_path} 💯")

    async def create_source(self, name: str, platform_type: str, platform_id: str):
        await self.execute(
            INSERT_SOURCE,
            True,
            (name, platform_type, platform_id, datetime.now(timezone.utc)),
        )

    async def create_content(
        self,
        source_id: str,
        platform_content_id: str,
        title: str,
        content: str,
        content_url: str,
        content_hash: str,
    ):
        cursor = await self.execute(
            INSERT_CONTENT,
            True,
            (
                source_id,
                platform_content_id,
                title,
                content,
                content_url,
                content_hash,
                datetime.now(timezone.utc),
            ),
        )

        return cursor.lastrowid

    async def create_summary(self, content_id, summary, strategy):
        await self.execute(
            INSERT_SUMMARY,
            True,
            (content_id, summary, strategy, datetime.now(timezone.utc)),
        )

    async def fetch_all_sources(self):
        cursor = await self.execute(SELECT_ALL_SOURCES)
        return await cursor.fetchall()

    async def fetch_source_names(self):
        cursor = await self.execute(SELECT_SOURCE_NAMES)
        rows = await cursor.fetchall()

        names = [row[0] for row in rows]

        return names

    async def fetch_last_content_fetch_time(self, source_id):
        cursor = await self.execute(SELECT_LAST_FETCH_TIME, False, (source_id,))
        result = await cursor.fetchone()

        if result and result[0]:
            return datetime.fromisoformat(result[0])

        return datetime.now(timezone.utc) - timedelta(days=7)

    async def fetch_content_summaries(self, content_id):
        cursor = await self.execute(SELECT_CONTENT_SUMMARY, False, (content_id,))
        result = await cursor.fetchone()
        return result["summary"] if result else None

    async def fetch_content_by_id(self, content_id):
        cursor = await self.execute(SELECT_CONTENT_BY_ID, False, (content_id,))
        return await cursor.fetchone()
