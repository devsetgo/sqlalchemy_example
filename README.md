# SQLAlchemy Example

Working on an example of sqlalchemy 2.0 async with FastAPI/Starlette

## Speed Test
via HTTPX only
python3 loop.py

via calling C code
compile first
gcc -shared -o http_request.so http_request.c -lcurl -fPIC

run

python3 loop_c.py
