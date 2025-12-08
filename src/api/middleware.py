from fastapi import Request, Response


async def timing_middleware(request: Request, call_next):
    # Simple timing middleware placeholder
    response: Response = await call_next(request)
    return response

