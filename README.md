# Esanpy: Elasticsearch based Analyzer for Python

Esanpy is Python Text Analyzer based on Elasticsearch.
Using embedded Elasticsearch, Esanpy provides powerful and fully-customizable text analysis.
Since Esanpy manages Elasticsearch instance internally, you do not need to install/configure Elasticsearch.

## Install Esanpy

    $ pip install esanpy

If you want to install development version, run as below:

    $ git clone https://github.com/codelibs/esanpy.git
    $ cd esanpy
    $ pip install .

## Python

First of all, import esanpy module.

```
import esanpy
```

### Start Server

To access to Elasticsearch, use `start_server` function.
This function downloads/configures embedded elasticsearch and plugins, and then start Elasticsearch instance.
The embedded elasticsearch is saved in `~/.esanpy` directory.
If they are configured, this function just start elasticsearch instance.

```
esanpy.start_server()
```

### Analyze Text

Esanpy provides `analyzer` and `custom_analyzer` function.

```
tokens = analyzer("This is a pen.")
# tokens = ["this", "is", "a", "pen"]
```

### Stop Server

```
esanpy.stop_server()
```

### Command

```
$ esanpy --text "This is a pen."
this
is
a
pen
```

```
$ esanpy --text 今日の天気は晴れです。 --analyzer kuromoji
今日
天気
晴れ
```

