# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from logging import getLogger, basicConfig
import unittest

import esanpy


class AnalyzerTest(unittest.TestCase):

    def setUp(self):
        basicConfig()
        getLogger('esanpy').setLevel(10)
        esanpy.start_server()

    def tearDown(self):
        esanpy.stop_server()

    def test_analyzer_default(self):
        result = esanpy.analyzer('This is a pen.')
        self.assertEqual(result, ['this', 'is', 'a', 'pen'])

    def test_analyzer_standard(self):
        result = esanpy.analyzer('This is a pen.',
                                 analyzer='standard')
        self.assertEqual(result, ['this', 'is', 'a', 'pen'])

    def test_analyzer_standard_explain(self):
        def test_converter(result):
            return [{"token": x.get('token'),
                     "start_offset": x.get('start_offset'),
                     "end_offset": x.get('end_offset'),
                     "position": x.get('position'),
                     "type": x.get('type'),
                     "keyword": x.get('keyword')} for x in result.get('detail').get('analyzer').get('tokens')]
        result = esanpy.analyzer('This is a pen.',
                                 analyzer='standard',
                                 attributes=['keyword'],
                                 converter=test_converter)
        self.assertEqual([x.get('token') for x in result], ['this', 'is', 'a', 'pen'])
        self.assertEqual([x.get('start_offset') for x in result], [0, 5, 8, 10])
        self.assertEqual([x.get('end_offset') for x in result], [4, 7, 9, 13])
        self.assertEqual([x.get('position') for x in result], [0, 1, 2, 3])
        self.assertEqual([x.get('type') for x in result], ['<ALPHANUM>', '<ALPHANUM>', '<ALPHANUM>', '<ALPHANUM>'])
        self.assertEqual([x.get('keyword') for x in result], [None, None, None, None])

    def test_analyzer_kuromoji(self):
        result = esanpy.analyzer('今日の天気は晴れです。',
                                 analyzer='kuromoji')
        self.assertEqual(result, ['今日', '天気', '晴れ'])

    def test_analyzer_kuromoji_explain(self):
        def test_converter(result):
            return [{"token": x.get('token'),
                     "pos": x.get('partOfSpeech')} for x in result.get('detail').get('analyzer').get('tokens')]
        result = esanpy.analyzer('今日の天気は晴れです。',
                                 analyzer='kuromoji',
                                 attributes=['partOfSpeech'],
                                 converter=test_converter)
        self.assertEqual([x.get('token') for x in result], ['今日', '天気', '晴れ'])
        self.assertEqual([x.get('pos') for x in result], ['名詞-副詞可能', '名詞-一般', '名詞-一般'])

    def test_custom_analyzer_case1(self):
        result = esanpy.custom_analyzer('this is a <b>test</b>',
                                        tokenizer="keyword",
                                        token_filter=["lowercase"],
                                        char_filter=["html_strip"])
        self.assertEqual(result, ['this is a test'])

    def test_custom_analyzer_case2(self):
        result = esanpy.custom_analyzer('this is a test',
                                        tokenizer="whitespace",
                                        token_filter=["lowercase",
                                                      {"type": "stop", "stopwords": ["a", "is", "this"]}],
                                        char_filter=[])
        self.assertEqual(result, ['test'])

    def test_custom_analyzer_case3(self):
        result = esanpy.custom_analyzer('detailed output',
                                        tokenizer="standard",
                                        token_filter=["snowball"],
                                        char_filter=[],
                                        attributes=["keyword"])
        tokens = result.get('detail').get('tokenizer').get('tokens')
        self.assertEqual([x.get('token') for x in tokens], ['detailed', 'output'])
        self.assertEqual([x.get('start_offset') for x in tokens], [0, 9])
        self.assertEqual([x.get('end_offset') for x in tokens], [8, 15])
        self.assertEqual([x.get('position') for x in tokens], [0, 1])
        self.assertEqual([x.get('type') for x in tokens], ['<ALPHANUM>', '<ALPHANUM>'])
        self.assertEqual([x.get('keyword') for x in tokens], [None, None])
        tokens = result.get('detail').get('tokenfilters')[0].get('tokens')
        self.assertEqual([x.get('token') for x in tokens], ['detail', 'output'])
        self.assertEqual([x.get('start_offset') for x in tokens], [0, 9])
        self.assertEqual([x.get('end_offset') for x in tokens], [8, 15])
        self.assertEqual([x.get('position') for x in tokens], [0, 1])
        self.assertEqual([x.get('type') for x in tokens], ['<ALPHANUM>', '<ALPHANUM>'])
        self.assertEqual([x.get('keyword') for x in tokens], [False, False])


if __name__ == "__main__":
    unittest.main()
