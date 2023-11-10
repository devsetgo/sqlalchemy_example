import asyncio
from ctypes import cdll, c_char_p, c_long
import time
from statistics import mean, median
from tqdm import tqdm

def call_code():
    # Load the shared library
    lib = cdll.LoadLibrary('./http_request.so')

    # Set the argument types and return type
    lib.http_get.argtypes = [c_char_p]
    lib.http_get.restype = c_long

    # Call the function
    # url = "http://localhost:5000/api/health/status".encode('utf-8')
    url = "http://localhost:5000/users?limit=100&offset=1".encode('utf-8')
    
    status_code = lib.http_get(url)

    return status_code

async def run(n):
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(None, call_code) for _ in range(n)]
    return await asyncio.gather(*futures)

import subprocess

def count_processes(process_name):
    process = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    
    lines = str(out).split('\\n')
    print(lines)
    # Filter out the parent process
    worker_lines = [line for line in lines if process_name in line and 'parent process' not in line]

    return len(worker_lines)

# print(count_processes('uvicorn'))



if __name__ == "__main__":
    n = 1000
    loops = 10
    req_list = []
    t0 = time.time()
    response_list=[]
    for l in tqdm(range(loops), ascii=True):
        start_time = time.time()
        responses = asyncio.run(run(n))
        end_time = time.time()
        elapsed_time = end_time - start_time
        requests_per_second = n / elapsed_time

        req_list.append(requests_per_second)
        response_list.append(responses)

    ave = mean(req_list)
    med = median(req_list)
    t1 = time.time() - t0
    total_req = n*loops
    # u_count = count_processes('uvicorn')
    print("")
    # print(f"Number of Uvicorn Workers: {u_count}")
    print(f"Mean: {ave:,.2f}, Median: {med:,.2f}, Total Requests:{total_req:,} in {t1:.2f} seconds, Process Mean Requests: {total_req/t1:,.2f}")
    
    # loop_num = 0
    # for r in response_list:
    #     loop_num +=1
    #     if 200 not in r:
    #         print(f"There is a no OK response: {r}")
        # else:
            # print(f"No failures in loop {loop_num}")
