# -*- encoding: utf8 -*-
'''
Giving text, title and index, trun to tokens and add to index. 
Input text should be pure text, which not contain html tags. 
'''

import collections
import functools
import math
import re
import unicodedata

from copy import copy
from string import ascii_letters, digits, punctuation

_stopwords = frozenset()
_accepted = frozenset(ascii_letters + digits + punctuation) - frozenset('\'')

_punctuation = copy(punctuation)
_punctuation = _punctuation.replace('\\', '')
_punctuation = _punctuation.replace('/', '')
_punctuation = _punctuation.replace('-', '')

_re_punctuation = re.compile('[%s]' % re.escape(_punctuation))
_re_token = re.compile(r'[a-z0-9]+')

def get_ngrams(token_list, n=2):
    for i in range(len(token_list) - n + 1):
        yield token_list[i:i+n]

def isnumeric(text):
    """
    Returns a True if the text is purely numeric and False otherwise.
    """
    try:
        float(text)
    except ValueError:
        return False
    else:
        return True

def text2index(text, stopwords=_stopwords, ngrams=1, min_length=0, ignore_numeric=True):
    """
    Parses the given text and yields tokens which represent words within
    the given text. Tokens are assumed to be divided by any form of
    whitespace character.
    """

    text = re.sub(re.compile('\'s'), '', text)  # Simple heuristic
    text = re.sub(_re_punctuation, '', text)
    
    res = []
    matched_tokens = re.findall(_re_token, text.lower())
    for tokens in get_ngrams(matched_tokens, ngrams):
        for i in range(len(tokens)):
            tokens[i] = tokens[i].strip(punctuation)

            if len(tokens[i]) < min_length or tokens[i] in stopwords:
                break
            if ignore_numeric and isnumeric(tokens[i]):
                break
            # else:
                # yield tuple(tokens)
        res.append(' '.join(tokens))
    return ' '.join(res)

if __name__ == "__main__":
    text2 = 'Life is about making an impact, not making an income.'
    # rst = list(word_tokenize(text))
    # print text2index(text2)

