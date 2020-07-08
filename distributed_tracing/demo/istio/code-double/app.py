from flask import Flask, request
import time
import os
import grequests

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
urls = os.environ['NEXT_HOP']            # 'http://fourth-hop-a.istio-server.svc.cluster.local' && 'http://fourth-hop-b.istio-server.svc.cluster.local'
urls = list(urls.split(" ")) 
delay = os.environ['DELAY']              # 3s

@app.route("/")
def do_GET():
    time.sleep(int(delay))
    request_headers = request.headers
    for header in istio_headers:
        if header in request_headers:
            headers_to_forward[header] = request_headers[header] 
    
    print(headers_to_forward)
    response = (grequests.get(url, headers=headers_to_forward) for url in urls)
    response = grequests.map(response)
    
    return response[0].content + response[1].content
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)