# -*- encoding: utf8 -*-
'''
Inverted index with number and positions 
for each term in each document. 
'''

import collections
import functools
import math
import os
import json


class InvertedIndex(object):

    def __init__(self):
        self._documents = collections.Counter()
        self._terms = {}
        self._terms_pos = {}

    def __getitem__(self, term):
        return self._terms[term]

    def __getitempos__(self, term):
        return self._terms_pos[term]

    def __contains__(self, term):
        return term in self._terms

    def __repr__(self):
        return '<InvertedIndex: {} terms, {} documents>'.format(
            len(self._terms), len(self._documents)
        )

    def add_term_occurrence(self, term, document):
        """
        Adds an occurrence of the term in the specified document.
        """
        if document not in self._documents:
            self._documents[document] = 0

        if term not in self._terms:
            self._terms[term] = collections.Counter()
            # self._terms_pos[term] = {}

        if document not in self._terms[term]:
            self._terms[term][document] = 0
            # self._terms_pos[term][document] = []

        self._documents[document] += 1
        self._terms[term][document] += 1
        # self._terms_pos[term][document].append(self._documents[document])

    def get_total_term_frequency(self, term):
        """
        Gets the frequency of the specified term in the entire corpus.
        """
        if term not in self._terms:
            raise IndexError('TERM_DOES_NOT_EXIST')

        return sum(self._terms[term].values())

    def get_term_frequency(self, term, document, normalized=False):
        """
        Returns the frequency of the term specified in the document.
        """
        if document not in self._documents:
            raise IndexError('DOCUMENT_DOES_NOT_EXIST')

        if term not in self._terms:
            raise IndexError('TERM_DOES_NOT_EXIST')

        result = self._terms[term].get(document, 0)
        if normalized:
            result /= self.get_document_length(document)

        return float(result)

    def get_document_frequency(self, term):
        """
        Returns the number of documents the specified term appears in.
        """
        if term not in self._terms:
            raise IndexError('TERM_DOES_NOT_EXIST')
        else:
            return len(self._terms[term])

    def get_document_length(self, document):
        """
        Returns the number of terms found within the specified document.
        """
        if document in self._documents:
            return self._documents[document]
        else:
            raise IndexError('DOCUMENT_DOES_NOT_EXIST')

    def get_documents(self, term):
        """
        Returns all documents related to the specified term in the
        form of a Counter object.
        """
        if term not in self._terms:
            raise IndexError('TERM_DOES_NOT_EXIST')
        else:
            return self._terms[term]

    def terms(self):
        return list(self._terms)

    def documents(self):
        return self._documents

    def items(self):
        return self._terms

    def items_pos(self):
        return self._terms_pos

    def to_dict(self):
        return {
            'documents': self._documents,
            'terms': self._terms,
            'terms_pos': self._terms_pos,
        }

    def from_dict(self, data):
        self._documents = collections.Counter(data['documents'])
        self._terms = {}
        for term in data['terms']:
            self._terms[term] = collections.Counter(data['terms'][term])
        self._terms_pos = data['terms_pos']

    def writefile(self, filepath):
        f = open(filepath+'documents.json', 'w')
        json.dump(self._documents, f)
        f.close()
        f = open(filepath+'terms.json', 'w')
        json.dump(self._terms, f)
        f.close()
        f = open(filepath+'terms_pos.json', 'w')
        json.dump(self._terms_pos, f)
        f.close()

if __name__ == "__main__":

    index = InvertedIndex()
    index.add_term_occurrence('hello', 'document1.txt')
    index.add_term_occurrence('world', 'document1.txt')
    
    print(index.get_documents('hello'))
    print(index.items())
    print(index.items_pos())

    for term in index.items().keys():
        plist = ""
        for doc in index.items()[term].keys():
            posting = ""
            posting += doc + '\t'
            posting += str(index.items()[term][doc])+'\t'
            posting += '\t'.join([str(x) for x in index.items_pos()[term][doc]])+'\n'
        plist += posting
        print(plist)



