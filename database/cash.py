from typing import Any, Optional

import structlog
from redis.exceptions import ReadOnlyError
from ormsgpack import ormsgpack
from redis.asyncio import Redis

logger: structlog.BoundLogger = structlog.get_logger("RedisClient")


class RedisClient:
    def __init__(self, db: int, host: str = '127.0.0.1', port: int = 6379) -> None:
        self.__redis_client = Redis(host=host, port=port, db=db)

    async def set(self, key: str, value: Any, ex: int = None, serial: bool = False) -> None:
        await logger.adebug(f"REDIS SET key={key}, value={value}, serial={serial}, ex={ex}")
        if serial:
            value = ormsgpack.packb(value)
        elif not serial and not isinstance(value, bytes | memoryview | str | int | float):
            # await logger.awarning(
            #     "The value is not bytes | memoryview | str | int | float. The value will be serialized.", value=value,
            #     t_value=type(value))
            value = ormsgpack.packb(value)

        try:
            if ex is None:
                await self.__redis_client.set(name=key.lower(), value=value)
            else:
                await self.__redis_client.set(name=key.lower(), value=value, ex=ex)
        except ReadOnlyError as _:
            await logger.aerror("Redis write error")

    async def get(self, key: str, serial: bool = False) -> Optional[Any]:
        value: Any = await self.__redis_client.get(name=key.lower())

        if not value:
            return

        if serial and value:
            value = ormsgpack.unpackb(value)

        await logger.adebug(f"REDIS GET key={key}, value={value[:10] if value is not None else value}..., "
                            f"serial={serial}")
        return value

    async def delete(self, *keys: bytes | str | memoryview) -> None:
        await logger.adebug(f"REDIS DELETE keys={[*keys]}")
        await self.__redis_client.delete(*keys)

    async def close(self) -> None:
        """
        Close the Redis connection gracefully.
        """
        await self.__redis_client.close()
        await logger.adebug('Redis connection closed')
