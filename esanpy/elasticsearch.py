# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from contextlib import closing
import glob
import json
from logging import getLogger
import multiprocessing
import os
import signal
import subprocess
import time
import zipfile

from esanpy.core import EsanpySetupError, EsanpyInvalidArgumentError, \
    EsanpyServerError, EsanpyStartupError
from esanpy.core import IVY_VERSION, ESRUNNER_VERSION, DEFAULT_CLUSTER_NAME, \
    DEFAULT_HTTP_PORT, DEFAULT_TRANSPORT_PORT, DEFAULT_PLUGINS


try:
    from urllib.request import Request
    from urllib.request import urlretrieve
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import Request
    from urllib import urlretrieve
    from urllib2 import urlopen
    from urllib2 import HTTPError

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

logger = getLogger('esanpy')


def get_esanalyzer_home():
    return os.path.expanduser('~/.esanpy')


def get_esrunner_home(esrunner_version):
    return get_esanalyzer_home() + "/" + esrunner_version


def get_es_home(http_port, esrunner_version):
    return get_esrunner_home(esrunner_version) + '/es_home_' + str(http_port)


def get_plugin_home(http_port, esrunner_version):
    return get_es_home(http_port, esrunner_version) + "/plugins"


def get_ivy_file():
    return get_esanalyzer_home() + "/ivy-" + IVY_VERSION + ".jar"


def get_ivy_url():
    return "http://search.maven.org/remotecontent?filepath=org/apache/ivy/ivy/" + IVY_VERSION + "/ivy-" + IVY_VERSION + ".jar"


def setup_esanalyzer(esrunner_version=ESRUNNER_VERSION, http_port=DEFAULT_HTTP_PORT, plugin_names=[]):
    esanalyzer_home = get_esanalyzer_home()
    if not os.path.exists(esanalyzer_home):
        os.mkdir(esanalyzer_home)

    # download ivy
    ivy_file = get_ivy_file()
    if not os.path.exists(ivy_file):
        urlretrieve(get_ivy_url(), ivy_file)

    esrunner_home = get_esrunner_home(esrunner_version)
    if not os.path.exists(esrunner_home):
        os.mkdir(esrunner_home)

    if not os.path.exists(esrunner_home + "/lib/elasticsearch-cluster-runner-" + ESRUNNER_VERSION + ".jar"):
        p = subprocess.Popen(["java",
                              "-jar",
                              "../ivy-" + IVY_VERSION + ".jar",
                              "-dependency",
                              "org.codelibs",
                              "elasticsearch-cluster-runner",
                              ESRUNNER_VERSION,
                              "-retrieve",
                              "lib/[artifact]-[revision](-[classifier]).[ext]"],
                             stdout=DEVNULL if logger.level != 10 else None,
                             stderr=DEVNULL if logger.level != 10 else None,
                             cwd=esrunner_home)
        p.wait()
        if p.returncode != 0:
            raise EsanpySetupError('Failed to download jar files. exit code: ' + str(p.returncode))

        # workaround
        removed_files = []
        removed_files.extend(glob.glob(esrunner_home + "/lib/asm-debug-all*"))
        removed_files.extend(glob.glob(esrunner_home + "/lib/commons-codec*"))
        for removed_file in removed_files:
            os.remove(removed_file)

    for plugin_name in plugin_names:
        install_plugin(plugin_name, http_port, esrunner_version)


def install_plugin(plugin_name, http_port=DEFAULT_HTTP_PORT, esrunner_version=ESRUNNER_VERSION):
    plugin_home = get_plugin_home(http_port, esrunner_version)
    if not os.path.exists(plugin_home):
        os.makedirs(plugin_home)

    if plugin_name.startswith("http:") or plugin_name.startswith("https:"):
        url = plugin_name
    elif ':' in plugin_name:
        values = plugin_name.split(':')
        if len(values) != 3:
            raise EsanpyInvalidArgumentError("Unknown plugin name: " + plugin_name)
        url = "https://repo1.maven.org/maven2/{}/{}/{}/{}-{}.zip".format(values[0].replace('.', '/'),
                                                                         values[1],
                                                                         values[2],
                                                                         values[1],
                                                                         values[2])
    else:
        url_template = "https://artifacts.elastic.co/downloads/elasticsearch-plugins/{}/{}-{}.zip"
        url = url_template.format(plugin_name,
                                  plugin_name,
                                  ".".join(esrunner_version.split('.')[0:3]))

    plugin_dir = plugin_home + "/" + url.split('/')[-1][0:-4]
    if not os.path.exists(plugin_dir):
        logger.debug("Downloading " + url)
        plugin_file, _ = urlretrieve(url)
        esrunner_home = get_esrunner_home(esrunner_version)
        with zipfile.ZipFile(plugin_file, 'r') as zf:
            zf.extractall(path=esrunner_home)
        logger.debug("Renaming to " + plugin_dir)
        os.rename(esrunner_home + "/elasticsearch", plugin_dir)


def get_esrunner_classpath(esrunner_version):
    jar_files = []
    lib_dir = get_esrunner_home(esrunner_version) + "/lib"
    for jar_file in os.listdir(lib_dir):
        if jar_file.endswith('.jar'):
            jar_files.append(lib_dir + "/" + jar_file)
    return ':'.join(jar_files)


def start_server(host='localhost', http_port=DEFAULT_HTTP_PORT,
                 transport_port=DEFAULT_TRANSPORT_PORT,
                 cluster_name=DEFAULT_CLUSTER_NAME,
                 plugin_names=DEFAULT_PLUGINS,
                 esrunner_version=ESRUNNER_VERSION):
    try:
        with closing(urlopen('http://' + host + ':' + str(http_port))) as response:
            if logger.isEnabledFor(10):
                logger.debug(json.loads(response.read().decode('utf-8')))
            return
    except Exception as e:
        logger.debug('Elasticsearch is not working: ' + str(e))

    setup_esanalyzer(esrunner_version, http_port, plugin_names)
    stop_server(host=host, http_port=http_port, esrunner_version=esrunner_version)

    esrunner_home = get_esrunner_home(esrunner_version)
    es_home = get_es_home(http_port, esrunner_version)
    # data_path = es_home +"/data/" + os.uname()[1]
    esrunner_args = ['java',
                     '-Xmx256m',
                     '-cp',
                     get_esrunner_classpath(esrunner_version),
                     "org.codelibs.elasticsearch.runner.ElasticsearchClusterRunner",
                     '-basePath',
                     es_home,
                     '-numOfNode',
                     '1',
                     '-clusterName',
                     cluster_name,
                     '-baseHttpPort',
                     str(http_port - 1),
                     '-baseTransportPort',
                     str(transport_port - 1)]

    logger.debug(' '.join(esrunner_args))
    p = subprocess.Popen(esrunner_args,
                         stdout=DEVNULL if logger.level != 10 else None,
                         stderr=DEVNULL if logger.level != 10 else None,
                         cwd=esrunner_home)

    pid_file = esrunner_home + "/" + str(http_port) + ".pid"
    with open(pid_file, 'wt') as f:
        f.write(str(p.pid))

    for i in range(30):
        time.sleep(1)
        logger.debug('Checking Elasticsearch status: ' + str(i))
        try:
            with closing(urlopen('http://' + host + ':' + str(http_port) +
                         '/_cluster/health?wait_for_status=yellow&timeout=1m')) as response:
                if logger.isEnabledFor(10):
                    logger.debug(json.loads(response.read().decode('utf-8')))
                return
        except Exception as e:
            logger.debug('Elasticsearch is not available: ' + str(e))

    if os.path.exists(pid_file):
        os.remove(pid_file)
    raise EsanpyStartupError('Failed to start Elasticsearch. See ' + es_home + '/logs/node_1/esanpy.log')


def stop_server(host='localhost', http_port=DEFAULT_HTTP_PORT,
                esrunner_version=ESRUNNER_VERSION):
    pid_file = get_esrunner_home(esrunner_version) + "/" + str(http_port) + ".pid"
    # stop existing process
    if os.path.exists(pid_file):
        with open(pid_file, 'rt') as f:
            pid = f.readline().strip()
        os.remove(pid_file)
        if len(pid) > 0:
            try:
                os.kill(int(pid), signal.SIGKILL)
            except Exception as e:
                logger.error('Failed to stop Elasticsearch process: ' + str(e))


def create_analysis(namespace, analyzer={}, tokenizer={}, token_filter={}, char_filter={},
                    host='localhost', http_port=DEFAULT_HTTP_PORT):
    url = 'http://' + host + ':' + str(http_port) + '/' + namespace
    req = Request(url)
    req.get_method = lambda: 'HEAD'
    req.add_header('Content-Type', 'application/json')
    try:
        with closing(urlopen(req)) as response:
            if response.code == 200:
                return False
    except HTTPError as e:
        if e.code == 404:
            logger.debug('Index does not exist: ' + str(e))
        else:
            raise EsanpySetupError('Failed to check ' + namespace + ' namespace: ' + e.read().decode('utf-8'))

    data = {
        "settings": {
            "index": {
                "refresh_interval": -1,
                "number_of_replicas": 0,
                "number_of_shards": multiprocessing.cpu_count(),
                "analysis": {
                    "filter": token_filter,
                    "char_filter": char_filter,
                    "analyzer": analyzer,
                    "tokenizer": tokenizer
                }
            }
        }
    }
    req = Request(url)
    req.get_method = lambda: 'PUT'
    req.add_header('Content-Type', 'application/json')
    try:
        with closing(urlopen(req, json.dumps(data).encode('utf-8'))) as response:
            if logger.isEnabledFor(10):
                logger.debug(response.read().decode('utf-8'))
    except HTTPError as e:
        raise EsanpySetupError('Failed to create ' + namespace + ' namespace: ' + e.read().decode('utf-8'))
    return True


def get_analysis(namespace,
                 host='localhost', http_port=DEFAULT_HTTP_PORT):
    url = 'http://' + host + ':' + str(http_port) + '/' + namespace
    req = Request(url)
    req.add_header('Content-Type', 'application/json')
    try:
        with closing(urlopen(req)) as response:
            if response.code == 200:
                result = json.loads(response.read().decode('utf-8'))
                namespace_obj = result.get(namespace)
                if namespace_obj is None:
                    return None
                settings_obj = namespace_obj.get('settings')
                if settings_obj is None:
                    return None
                index_obj = settings_obj.get('index')
                if index_obj is None:
                    return None
                return index_obj.get('analysis')
    except HTTPError as e:
        if e.code == 404:
            logger.debug('Index does not exist: ' + str(e))
        else:
            raise EsanpySetupError('Failed to get ' + namespace + ' namespace: ' + e.read().decode('utf-8'))
    return None


def delete_analysis(namespace,
                    host='localhost', http_port=DEFAULT_HTTP_PORT):
    url = 'http://' + host + ':' + str(http_port) + '/' + namespace
    req = Request(url)
    req.get_method = lambda: 'DELETE'
    req.add_header('Content-Type', 'application/json')
    with closing(urlopen(req)) as response:
        if response.code != 200:
            raise EsanpyServerError('Failed to delete ' + namespace)
