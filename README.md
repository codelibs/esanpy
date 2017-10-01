# Esanpy: Elasticsearch based Analyzer for Python

Esanpy is Python text analyzer based on Elasticsearch.
Using embedded Elasticsearch, Esanpy provides powerful and fully-customizable text analysis.
Since Esanpy manages Elasticsearch instance internally, you do not need to install/configure Elasticsearch.

## Install Esanpy

    $ pip install esanpy

If you want to install development version, run as below:

    $ git clone https://github.com/codelibs/esanpy.git
    $ cd esanpy
    $ pip install .

## Python

### Start Server

```
import esanpy

esanpy.start_server()
```

### Stop Server

```
import esanpy

esanpy.stop_server()
```

### Command

    $ esanpy --text "This is Hello World."

