from typing import Any

from saltapi.repository.database import engine


class UnitOfWork:
    def __enter__(self) -> "UnitOfWork":
        self.connection = engine.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.rollback()
        self.connection.close()

    def rollback(self) -> None:
        self.connection.rollback()

    async def commit(self) -> None:
        await self.connection.commit()
