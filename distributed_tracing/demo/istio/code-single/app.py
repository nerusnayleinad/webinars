from flask import Flask, request
import time
import os
import requests

app = Flask(__name__)

istio_headers = [
    'x-request-id',
    'x-b3-traceid',
    'x-b3-spanId',
    'x-b3-parentspanid',
    'x-b3-sampled',
    'x-b3-flags',
    'b3'
]

headers_to_forward = {}
url = os.environ['NEXT_HOP']           
delay = os.environ['DELAY']   

@app.route("/")
def do_GET():
    time.sleep(int(delay))
    request_headers = request.headers
    for header in istio_headers:
        if header in request_headers:
            headers_to_forward[header] = request_headers[header] 
    
    response = requests.get(url, headers=headers_to_forward)
    
    return response.content
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)