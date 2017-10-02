# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals


IVY_VERSION = "2.4.0"
ESRUNNER_VERSION = "5.6.0.0"
DEFAULT_HTTP_PORT = 9299
DEFAULT_TRANSPORT_PORT = 9399
DEFAULT_CLUSTER_NAME = 'esanpy'
DEFAULT_PLUGINS = ['analysis-icu',
                   'analysis-kuromoji',
                   'analysis-phonetic',
                   'analysis-smartcn',
                   'analysis-stempel',
                   'analysis-ukrainian']


class EsanpyError(Exception):
    pass


class EsAnalyzerSetupError(EsanpyError):
    pass


class EsanpyInvalidArgumentError(EsanpyError):
    pass


class EsanpyIndexExistError(EsanpyError):
    pass


class EsanpyServerError(EsanpyError):
    pass
