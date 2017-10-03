# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import argparse
from logging import getLogger, Formatter, StreamHandler
import os
import sys

from esanpy import analyzers
from esanpy import elasticsearch
from esanpy.core import ESRUNNER_VERSION, DEFAULT_CLUSTER_NAME, DEFAULT_HTTP_PORT, DEFAULT_TRANSPORT_PORT,\
    DEFAULT_PLUGINS


start_server = elasticsearch.start_server
stop_server = elasticsearch.stop_server
create_analysis = elasticsearch.create_analysis
get_analysis = elasticsearch.get_analysis
delete_analysis = elasticsearch.delete_analysis
analyzer = analyzers.analyzer
custom_analyzer = analyzers.custom_analyzer

logger = getLogger('esanpy')


def parse_args(args):
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('--runner-version', dest='esrunner_version', action='store',
                        default=ESRUNNER_VERSION, help='Elasticsearch cluster name')
    parser.add_argument('--cluster-name', dest='cluster_name', action='store',
                        default=DEFAULT_CLUSTER_NAME, help='Elasticsearch cluster name')
    parser.add_argument('--host', dest='host', action='store',
                        default='localhost', help='Elasticsearch host name')
    parser.add_argument('--http-port', dest='http_port', action='store',
                        default=DEFAULT_HTTP_PORT, type=int, help='Elasticsearch HTTP port')
    parser.add_argument('--transport-port', dest='transport_port', action='store',
                        default=DEFAULT_TRANSPORT_PORT, type=int, help='Elasticsearch Transport port')
    parser.add_argument('--analyzer-name', dest='analyzer_name', action='store',
                        default='standard', help='Analyzer name')
    parser.add_argument('--text', dest='text', action='store', help='Text to analyze')
    parser.add_argument('--plugin', dest='plugins', action='append', help='Plugins to install')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                        default=False, help='Display debug messages')
    parser.add_argument('--stop', dest='stop', action='store_true',
                        default=False, help='Stop Elasticsearch on exit')
    return parser.parse_args(args=args)


def configure_logging(options):
    formatter = Formatter('[%(asctime)s] %(message)s')
    handler = StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if options.verbose:
        logger.setLevel(10)
    else:
        logger.setLevel(20)


def main(args=None):
    options = parse_args(args)

    configure_logging(options)

    plugin_names = DEFAULT_PLUGINS if options.plugins is None else options.plugins
    start_server(host=options.host,
                 http_port=options.http_port,
                 transport_port=options.transport_port,
                 cluster_name=options.cluster_name,
                 plugin_names=plugin_names,
                 esrunner_version=options.esrunner_version)

    tokens = analyzer(options.text,
                      analyzer=options.analyzer_name)
    print('\n'.join(tokens))

    if options.stop:
        stop_server(host=options.host,
                    http_port=options.http_port,
                    esrunner_version=options.esrunner_version)

    return 0


if __name__ == '__main__':
    sys.exit(main())
