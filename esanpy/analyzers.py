# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
from logging import getLogger

from esanpy.core import DEFAULT_HTTP_PORT


try:
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request

logger = getLogger('esanpy')


def analyzer(text, analyzer='standard', index=None,
             host='localhost', http_port=DEFAULT_HTTP_PORT):
    if text is None:
        return []
    data = {'analyzer': analyzer, 'text': text}
    url_suffix = '/_analyze' if index is None else '/' + index + '/_analyze'
    return send_analyze_request('http://' + host + ':' + str(http_port) + url_suffix,
                                data)


def custom_analyzer(text, tokenizer='keyword', token_filter=[], char_filter=[],
                    host='localhost', http_port=DEFAULT_HTTP_PORT):
    if text is None:
        return []
    data = {"tokenizer": tokenizer,
            "filter": token_filter,
            "char_filter": char_filter,
            "text": text}
    return send_analyze_request('http://' + host + ':' + str(http_port) + '/_analyze',
                                data)


def send_analyze_request(url, data):
    req = Request(url)
    req.add_header('Content-Type', 'application/json')
    with urlopen(req, json.dumps(data).encode('utf-8')) as response:
        result = json.loads(response.read().decode())
        return [x.get('token') for x in result.get('tokens')]
