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
The elasticsearch is saved in `~/.esanpy` directory.
If they are configured, this function just start elasticsearch instance.

```
esanpy.start_server()
```

### Analyze Text

Esanpy provides `analyzer` and `custom_analyzer` function.

```
tokens = esanpy.analyzer("This is a pen.")
# tokens = ["this", "is", "a", "pen"]
```

To use other analyzer, set an analyzer name with `analyzer`.

```
tokens = esanpy.analyzer("今日の天気は晴れです。", analyzer="koromoji")
```

### Stop Server

To stop Elasticsearch, use `stop_server()`.

```
esanpy.stop_server()
```

## Command

Esanpy provides `esanpy` command.

```
$ esanpy --text "This is a pen."
this
is
a
pen
```

`esanpy` starts Elasticsearch if it does not run.
So, it takes time to start it, but it will be fast after that because Elasticsearch instance is reused.

To change analyzer, use `--analyzer` option.

```
$ esanpy --text 今日の天気は晴れです。 --analyzer kuromoji
今日
天気
晴れ
```

`--stop` opition stops Elasticsearch instance on the command exit.

```
$ esanpy --text "This is a pen." --stop
```

