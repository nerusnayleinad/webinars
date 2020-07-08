from flask import Flask
from flask import request
import sys
import time
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format
import requests


app = Flask(__name__)
tracer = init_tracer('hello')

@app.route('/<name>')
def hello(name):
    with tracer.start_active_span('hello') as scope:
        scope.span.set_tag('hello_to', name)
        hello_str = format_string(name)
        print_hello(hello_str)
    return hello_str
    

def format_string(hello_to):
    with tracer.start_active_span('format') as scope:
        hello_str = http_get(8081, 'format', 'helloTo', hello_to)
        scope.span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str

def print_hello(hello_str):
    with tracer.start_active_span('println') as scope:
        http_get(8082, 'publish', 'helloStr', hello_str)
        scope.span.log_kv({'event': 'println'})

def http_get(port, path, param, value):
    url = 'http://localhost:%s/%s' % (port, path)

    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url, params={param: value}, headers=headers)
    assert r.status_code == 200
    return r.text


# main
app.run(host='0.0.0.0', port=8080, debug=True)