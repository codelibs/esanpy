# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from logging import getLogger, basicConfig
import unittest
import os

import esanpy
from esanpy.core import EsanpySetupError


class ElasticsearchTest(unittest.TestCase):

    def setUp(self):
        basicConfig()
        getLogger('esanpy').setLevel(10)
        esanpy.start_server()

    def tearDown(self):
        esanpy.stop_server()

    def test_analysis_case1(self):
        mapping_file = os.path.abspath("tests/resources/case1_mapping_ja.txt")
        userdict_file = os.path.abspath("tests/resources/case1_userdict.txt")
        esanpy.create_analysis('case1',
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

        analysis = esanpy.get_analysis('case1')
        self.assertTrue('filter' in analysis, "filter exists.")
        self.assertTrue('ja_stopword' in analysis.get('filter'), "ja_stopword exists.")
        self.assertTrue('tokenizer' in analysis, "tokenizer exists.")
        self.assertTrue('kuromoji_user_dict' in analysis.get('tokenizer'), "kuromoji_user_dict exists.")
        self.assertTrue('char_filter' in analysis, "char_filter exists.")
        self.assertTrue('mapping_ja_filter' in analysis.get('char_filter'), "mapping_ja_filter exists.")
        self.assertTrue('analyzer' in analysis, "analyzer exists.")
        self.assertTrue('kuromoji_analyzer' in analysis.get('analyzer'), "kuromoji_analyzer exists.")

        result = esanpy.analyzer('①東京スカイツリーに行く',
                                 analyzer="kuromoji_analyzer",
                                 namespace='case1')
        self.assertEqual(result, ['1', '東京スカイツリー', 'に'])

        esanpy.delete_analysis('case1')

        analysis = esanpy.get_analysis('case1')
        self.assertTrue(analysis is None, "analysis is None.")

    def test_analysis_case2(self):
        try:
            esanpy.create_analysis('case2',
                                   analyzer={
                                       "kuromoji_analyzer": {
                                           "type": "custom",
                                           "char_filter": ["xxx"],
                                           "tokenizer": "xxx",
                                           "filter": ["xxx"]
                                           }
                                   }
                                   )
            self.fail('EsanpySetupError should be thrown.')
        except EsanpySetupError as e:
            print(e)
        esanpy.get_analysis('case2')


if __name__ == "__main__":
    unittest.main()
