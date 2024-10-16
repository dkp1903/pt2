from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.fetchers.price_fetcher import get_prices
from app.rate_limiter import rate_limiter
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TickerRequest(BaseModel):
    ticker: str
    country: str

class TickerPayload(BaseModel):
    tickers: list[TickerRequest]

@router.post("/get-prices/")
@rate_limiter
async def get_prices_endpoint(payload: TickerPayload, request: Request):
    try:
        logger.info(f"Received request from {request.client.host}")
        
        # Validate payload
        if not payload.tickers:
            raise HTTPException(status_code=400, detail="Tickers list cannot be empty.")
        
        # Fetch prices (both US stocks and Indian mutual funds)
        results = await get_prices(payload.tickers)
        logger.info("Get Prices done")
        return {"prices": results}
    
    except HTTPException as e:
        logger.error(f"Client error: {str(e.detail)}")
        raise e
    
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
