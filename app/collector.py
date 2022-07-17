import asyncio
from random import random
from sqlalchemy import select
from app.db.database import async_session
from app.db.models import Ticker, TickerPrice


async def collect_change() -> None:

    async with async_session() as session:
        query = select(Ticker)
        result = await session.execute(query)
        queryset = result.scalars().all()
        await asyncio.gather(
            *[
                save_price(i) for i in queryset
            ]
        )


async def save_price(ticker: Ticker) -> None:
    price = TickerPrice()
    price.ticker_id = ticker.id
    price.price = generate_movement()

    async with async_session() as session:
        session.begin()
        session.add(price)
        await session.commit()
        await session.close()


def generate_movement() -> int:
    movement = -1 if random() < 0.5 else 1
    return movement
