# -*- coding: utf-8 -*-

from logging import getLogger
import unittest

import esanpy


class AnalyzerTest(unittest.TestCase):

    def setUp(self):
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

    def test_analyzer_kuromoji(self):
        result = esanpy.analyzer('今日の天気は晴れです。',
                                 analyzer='kuromoji')
        self.assertEqual(result, ['今日', '天気', '晴れ'])

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


if __name__ == "__main__":
    unittest.main()
