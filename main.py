import asyncio
from fastapi import Request, FastAPI, WebSocket
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.collector import collect_change
from app.db.database import async_session
from app.db.models import Ticker, TickerPrice

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


@app.get("/tickers")
async def tickers(request: Request):
    """Return list of tickers"""

    async with async_session() as session:
        query = select(Ticker)
        result = await session.execute(query)
    queryset = result.scalars().all()
    response = {
        "queryset": queryset,
        'request': request
    }
    return templates.TemplateResponse("tickers.html", response)


@app.get("/{ticker_id}")
async def chart(request: Request, ticker_id: int):

    async with async_session() as session:
        query = select(Ticker).where(Ticker.id == ticker_id).options(selectinload(Ticker.prices))
        result = await session.execute(query)
        ticker_prices = result.scalars().first().prices
        prices = []
        x = 0
        for price in ticker_prices:
            prices.append(
                {
                    'x': x,
                    'y': price.price
                }
            )
            x += 1

        response = {
            "request": request,
            'prices': prices,
            "x": x,
            "ticker_id": ticker_id
        }
    return templates.TemplateResponse("chart.html", response)


@app.websocket("/ws/{ticker_id}")
async def websocket_endpoint(websocket: WebSocket, ticker_id: int):
    """
    Для облегчения работы данные по всем 100 ticker начинают собираться только в момент работы webSocket
    """

    await websocket.accept()
    while True:
        async with async_session() as session:
            await collect_change()
            await asyncio.sleep(1)
            query = select(func.sum(TickerPrice.price).label('total')).where(TickerPrice.ticker_id == ticker_id)
            result = await session.execute(query)
            ticker_price = result.scalars().first()

            last = select(TickerPrice).where(TickerPrice.ticker_id == ticker_id).order_by(TickerPrice.id.desc())
            result = await session.execute(last)
            last_value = result.scalars().first()

            response = {
                "price": ticker_price,
                "last_value_price": last_value.price
            }
        await websocket.send_json(response)
