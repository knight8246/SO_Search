import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
from os import listdir
import sys
import os
import re
import json
import time
import MySQLdb

from invertedindex import InvertedIndex
from text2index import text2index

def merging2Blocks(db, db2, block1, block2, block_id):
    ## Merge 2 blocks in DB
    ## same term: posting_index add
    ## different term: directly save
    cursor = db2.cursor()

    # create a new block
    tablename = 'Blocks_%s' % block_id
    sql = "CREATE TABLE %s (\
         Term  VARCHAR(250) NOT NULL,\
         PostingList LONGTEXT,\
         PRIMARY KEY (Term))" % tablename
    cursor.execute(sql)

    # outer join two blocks
    sql = "select a.Term as Term,a.PostingList,b.PostingList \
        from %s a left join %s b\
        on a.Term = b.Term\
        union\
        select b.Term as Term,a.PostingList,b.PostingList\
        from %s a right join %s b\
        on a.Term = b.Term" % \
        (block1, block2, block1, block2)
    cursor.execute(sql)

    # insert into new block
    res = cursor.fetchone()
    writer = db.cursor()
    while res:
        term = res[0]
        plist = ""
        if res[1] is not None:
            plist = res[1]
        if res[2] is not None:
            plist += res[2]
        sql = "INSERT INTO %s(Term, PostingList)\
            VALUES (\"%s\", \"%s\")" % (tablename, term, plist)
        writer.execute(sql)
        res = cursor.fetchone()

    # # drop the merged tables
    # sql = "DROP TABLE %s" % block1
    # cursor.execute(sql)
    # sql = "DROP TABLE %s" % block2
    # cursor.execute(sql)

    db.commit()
    print(block1, ' ', block2, ' have been merged. ')

if __name__ == "__main__":
    db = MySQLdb.connect("localhost", "teacat", 
                "123456", "WSMT2", charset='utf8' )
    db2 = MySQLdb.connect("localhost", "teacat", 
                "123456", "WSMT2", charset='utf8', 
                cursorclass = MySQLdb.cursors.SSCursor)
    print("Successfully connected. ")

    # cursor = db.cursor()
    # for i in range(186):
    #     tablename = 'Blocks_%s' % i
    #     sql = "DROP TABLE WSMT3.%s" % tablename
    #     cursor.execute(sql)
    # db.commit()
    # print("clear done!")

    merging2Blocks(db, db2, 'Blocks_182', 'Blocks_183', 185)

    merging2Blocks(db, db2, 'Blocks_184', 'Blocks_185', 186)

    db.close()
