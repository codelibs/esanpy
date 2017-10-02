# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import glob
import json
from logging import getLogger
import os
import signal
import subprocess
import time
import zipfile

from esanpy.core import EsAnalyzerSetupError, EsanpyInvalidArgumentError
from esanpy.core import IVY_VERSION, ESRUNNER_VERSION, DEFAULT_CLUSTER_NAME,\
    DEFAULT_HTTP_PORT, DEFAULT_TRANSPORT_PORT, DEFAULT_PLUGINS


try:
    from urllib.request import urlretrieve
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib import urlretrieve
    from urllib2 import urlopen
    from urllib2.error import URLError

logger = getLogger('esanpy')


def get_esanalyzer_home():
    return os.path.expanduser('~/.esanpy')


def get_esrunner_home(esrunner_version):
    return get_esanalyzer_home() + "/" + esrunner_version


def get_plugin_home(http_port, esrunner_version):
    return get_esrunner_home(esrunner_version) + '/es_home_' + str(http_port) + "/plugins"


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
                             stdout=subprocess.DEVNULL if logger.level != 10 else None,
                             stderr=subprocess.DEVNULL if logger.level != 10 else None,
                             cwd=esrunner_home)
        p.wait()
        if p.returncode != 0:
            raise EsAnalyzerSetupError('Failed to download jar files. exit code: ' + str(p.returncode))

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
        url = "https://repo1.maven.org/maven2/{}/{}/{}/{}-{}.zip".format(values[0],
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
        with urlopen('http://' + host + ':' + str(http_port)) as response:
            logger.debug(json.loads(response.read().decode()))
            return
    except OSError as e:
        logger.debug('Elasticsearch is not working: ' + str(e))

    setup_esanalyzer(esrunner_version, http_port, plugin_names)
    stop_server(host=host, http_port=http_port, esrunner_version=esrunner_version)

    esrunner_home = get_esrunner_home(esrunner_version)
    esrunner_args = ['java',
                     '-Xmx256m',
                     '-cp',
                     get_esrunner_classpath(esrunner_version),
                     "org.codelibs.elasticsearch.runner.ElasticsearchClusterRunner",
                     '-basePath',
                     esrunner_home + '/es_home_' + str(http_port),
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
                         stdout=subprocess.DEVNULL if logger.level != 10 else None,
                         stderr=subprocess.DEVNULL if logger.level != 10 else None,
                         cwd=esrunner_home)

    pid_file = esrunner_home + "/" + str(http_port) + ".pid"
    with open(pid_file, 'wt') as f:
        f.write(str(p.pid))

    for i in range(30):
        time.sleep(1)
        try:
            with urlopen('http://' + host + ':' + str(http_port) +
                         '/_cluster/health?wait_for_status=yellow&timeout=1m') as response:
                logger.debug(json.loads(response.read().decode()))
                return
        except Exception:
            logger.debug('Checking Elasticsearch status: ' + str(i))


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
            except Exception:
                logger.error('Failed to stop Elasticsearch process')
