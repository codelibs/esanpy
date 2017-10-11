# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from contextlib import closing
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


def default_converter(result):
    return [x.get('token') for x in result.get('tokens')]


def analyzer(text, analyzer='standard', namespace=None, attributes=None,
             host='localhost', http_port=DEFAULT_HTTP_PORT,
             converter=None):
    if text is None:
        return []
    data = {'analyzer': analyzer, 'text': text}
    if attributes is not None:
        data.update({"explain": True,
                     "attributes": attributes})
        if converter is None:
            converter = lambda x: x
    elif converter is None:
        converter=default_converter
    url_suffix = '/_analyze' if namespace is None else '/' + namespace + '/_analyze'
    return send_analyze_request('http://' + host + ':' + str(http_port) + url_suffix,
                                data,
                                converter=converter)


def custom_analyzer(text, namespace=None, attributes=None,
                    tokenizer='keyword', token_filter=[], char_filter=[],
                    host='localhost', http_port=DEFAULT_HTTP_PORT,
                    converter=None):
    if text is None:
        return []
    data = {"tokenizer": tokenizer,
            "filter": token_filter,
            "char_filter": char_filter,
            "text": text}
    if attributes is not None:
        data.update({"explain": True,
                     "attributes": attributes})
        if converter is None:
            converter = lambda x: x
    elif converter is None:
        converter=default_converter
    url_suffix = '/_analyze' if namespace is None else '/' + namespace + '/_analyze'
    return send_analyze_request('http://' + host + ':' + str(http_port) + url_suffix,
                                data,
                                converter=converter)


def send_analyze_request(url, data, converter):
    req = Request(url)
    req.add_header('Content-Type', 'application/json')
    with closing(urlopen(req, json.dumps(data).encode('utf-8'))) as response:
        result = json.loads(response.read().decode('utf-8'))
        return converter(result)
