#!/usr/bin/python

import os
import sqlite3
import json
import collections
import sys
import numpy
import scipy.io
from itertools import izip, tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

sqlite_db = None
def connect_db():
    """Connects to the specific database."""
    print "Opening database connection"
    rv = sqlite3.connect("words.db")
    rv.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    global sqlite_db
    if sqlite_db is None:
        sqlite_db = connect_db()
    return sqlite_db

def close_db(error):
    """Closes the database again at the end of the request."""
    if sqlite_db is not None:
        sqlite_db.close()

def load(f):
    db = get_db()
    for line in f:
        line = line.strip()
        words = {}
        for word in line.split(' '):
            cur = db.execute(('SELECT id '
                              'FROM words '
                              'WHERE word = ? '),
                             [word])
            
            word_id = cur.fetchone()
            if word_id is not None:
                words[word] = word_id[0]
            else:
                cur = db.execute(('INSERT INTO words (word) VALUES (?)'),
                                 [word])
                words[word] = cur.lastrowid
        
        first = True
        prev = None
        first_sentence_id = None
        for word in line.split(' '):
            cur = db.execute(('INSERT INTO '
                              'sentences (word_id, prev_id) '
                              'VALUES (?, ?) '),
                             [words[word], prev])
            if first:
                first_sentence_id = cur.lastrowid
            first = False
            prev = cur.lastrowid
    
        cur = db.execute(('INSERT INTO '
                          'raw (sentence, sentence_id) '
                          'VALUES (?, ?) '),
                         [line, first_sentence_id])


        db.commit()

def generate_matrix(out_filename):
    db = get_db()
    
    cur = db.execute(('SELECT COUNT(*) + 1 FROM words'))
    num_words = cur.fetchone()[0]
    
    mat = numpy.memmap(out_filename, 
                       dtype=numpy.int32, 
                       mode='w+',
                       shape=(num_words + 1, num_words + 1))
    
    cur = db.execute(('SELECT (SELECT sentences2.word_id + 1 '
                      '        FROM sentences AS sentences2 '
                      '        WHERE sentences2.id = sentences.prev_id '
                      '       ) prev_word_id, '
                      '       sentences.word_id + 1 '
                      'FROM sentences '))
    
    for row in cur:
        (prev_word_id, word_id) = row
        if prev_word_id is None:
            prev_word_id = 0
        mat[prev_word_id, word_id] += 1
    
    del mat
    
def main(do_what):
    if do_what == "LOAD":
        load(sys.stdin)
    if do_what == "MATRIX":
        generate_matrix(sys.argv[2])
    
if __name__ == "__main__":
    main(sys.argv[1])
    
