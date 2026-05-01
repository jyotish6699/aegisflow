from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def get_items(item_id: int, request: Request):
    print(request.query_params)
    return {
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "headers": dict(request.headers),
        "items_id":item_id
    }
    


# what is Request?
# Request is an object represention the complete incoming HTTP request, it is created by fastAPI by default but injected only when explicitly requested.

# what is query_params?
# key-value pairs sent in the URL after '?' in a GET request.

# asyc def handler(request: Request): is a Raw API for inspection or middleware-like
# async def handler(name: str, age: int): is a clean API for explicitly ask for name and age only from the url.

# ?name=jyotish is a query parameter/string
# ? -> start query
# & -> seperate values
# = -> key and value

# decorator with path operation function/route handler
# @app.get("/")
# async def path_operation(name: str):
#     print(name)
#     return {"received": name}