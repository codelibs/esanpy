# Esanpy: Elasticsearch based Analyzer for Python [![Build Status](https://travis-ci.org/codelibs/esanpy.svg?branch=master)](https://travis-ci.org/codelibs/esanpy)

Esanpy is Python Text Analyzer based on Elasticsearch.
Using Elasticsearch, Esanpy provides powerful and fully-customizable text analysis.
Since Esanpy manages Elasticsearch instance internally, you DO NOT need to install/configure Elasticsearch.

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

`custom_analyzer` has `tokenizer`, `token_filter` and `char_filter` as arguments.

```
tokens = esanpy.custom_analyzer('this is a <b>test</b>',
                                tokenizer="keyword",
                                token_filter=["lowercase"],
                                char_filter=["html_strip"])
```

For Elasticsearch Analyze API, see [Analyze](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-analyze.html).

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

## Advance Usecases

### Register Analyzer

You can register own analyzers by `create_analysis`.
To register analyzers with `my_analyzers` namespace:

```
esanpy.create_analysis('my_analyzers',
                       char_filter={
                           "mapping_ja_filter": {
                               "type": "mapping",
                               "mappings_path": mapping_file
                               }
                       },
                       tokenizer={
                           "kuromoji_user_dict": {
                               "type": "kuromoji_tokenizer",
                               "mode": "normal",
                               "user_dictionary": userdict_file,
                               "discard_punctuation": False
                               }
                       },
                       token_filter={
                           "ja_stopword": {
                               "type": "ja_stop",
                               "stopwords": [
                                   "行く"
                                   ]
                               }
                       },
                       analyzer={
                           "kuromoji_analyzer": {
                               "type": "custom",
                               "char_filter": ["mapping_ja_filter"],
                               "tokenizer": "kuromoji_user_dict",
                               "filter": ["ja_stopword"]
                               }
                       }
                       )
```

To use kuromoji_analyzer, invoke `analyzer` with a namespace and analyzer:

```
tokens = esanpy.analyzer('①東京スカイツリーに行く',
                         analyzer="kuromoji_analyzer",
                         namespace='my_analyzers')
# tokens = ['1', '東京スカイツリー', 'に']
```

To delete namespace, use `delete_analysis`:

```
esanpy.delete_analysis('my_analyzers')
```

For more information, see [Analysis](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/analysis.html).

### Uninstall Esanpy

To remove Esanpy, check/kill processes:

```
$ ps aux | grep esanpy
$ kill [above PIDs]
```

and then remove `~/.esanpy` directory:

```
$ rm -rf ~/.esanpy
```
