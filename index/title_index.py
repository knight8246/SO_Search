import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
from os import listdir
import sys
import os
import json
import time
import MySQLdb

from invertedindex import InvertedIndex
from text2index import text2index

def saveBlockDict2DB(db, index, block_id):
    ## sava the block to the db
    ## term, {doc_id, \t, frequency}\n,
    ## doc_id, length
    ## do NOT sort for term

    # cursor = db.cursor()
    # sql = "CREATE TABLE IF NOT EXISTS WSMT.TitleSum (\
    #      QuestionID  VARCHAR(10) NOT NULL,\
    #      TitleLen SMALLINT,\
    #      PRIMARY KEY (QuestionID))"
    # cursor.execute(sql)

    cursor = db.cursor()
    tablename = 'Blocks_%s' % block_id
    sql = "CREATE TABLE %s (\
         Term  VARCHAR(250) NOT NULL,\
         PostingList LONGTEXT,\
         PRIMARY KEY (Term))" % tablename
    cursor.execute(sql)

    for term in index.items().keys():
        plist = ""
        for doc in index.items()[term].keys():
            posting = ""
            posting += str(doc) + '\t'
            posting += str(index.items()[term][doc])+'\n'
            # posting += str(index.items()[term][doc])+'\t'
            # posting += '\t'.join([str(x) for x in index.items_pos()[term][doc]])+'\n'
            plist += posting

        sql = "INSERT INTO %s(Term, PostingList)\
            VALUES (\"%s\", \"%s\")" % (tablename, term, plist)
        cursor.execute(sql)

    # for doc in index.documents().keys():
    #     titlelen = index.documents()[doc]
    #     sql = "INSERT INTO WSMT.TitleSum(QuestionID, TitleLen)\
    #         VALUES (%s, %d)" % (str(doc), titlelen)
    #     cursor.execute(sql)

    db.commit()


def invert_block(db, blockCapacityLimit=50000):
    ## Read data from db & create invert blocks
    ## TODO: k-gram or stemming

    ## Inverted block
    counter = 0
    block_id = 0
    index = InvertedIndex()

    cursor = db.cursor()
    cursor.execute("select Title,Id from WSMJ.PostsJ where PostTypeId=1") 
    res = cursor.fetchone()
    while res:
        filetext = res[0]
        fileid = res[1]
        text2index(filetext, fileid, index)
        counter += 1
        if(counter%blockCapacityLimit==0):
            print(counter, ' files have been read. ')
            saveBlockDict2DB(db, index, block_id)
            index = InvertedIndex()
            block_id += 1
            print(block_id, ' block has been writen. ')
        res = cursor.fetchone()
    if(counter%blockCapacityLimit!=0):
        saveBlockDict2DB(db, index, block_id)
        block_id += 1
        print(counter, ' files have been read. ')
        print('There are ', block_id, ' blocks.')


def getSortedBlockNames(db):
    ## return blockNames, n_blocks from DB
    cursor = db.cursor()
    cursor.execute("show tables") 
    res = cursor.fetchall()
    blockNames = []
    for table in res:
        table = table[0].encode('utf-8')
        blockNames.append(table)
    blockNames_pos = [(int(filter(str.isdigit, blockName)), blockName) for blockName in blockNames]  # (Block id, names)
    sorted_blockID_Names = sorted(blockNames_pos, key=lambda x: x[0])  # Sort based on block id
    blockNames = [name for id, name in sorted_blockID_Names]  # Grab only block name from (block id, name) tuple
    n_blocks = len(blockNames)  # Number of blocks
    return blockNames, n_blocks


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


def mergeAllBlocks(db, db2):
    blockNames, n_blocks = getSortedBlockNames(db)
    block_id = n_blocks
    prev_blocks = 0

    # Merge blocks until there are one big merged block left
    while n_blocks > 1:
        print(n_blocks, ' blocks to merge. ')
        if n_blocks % 2 == 0: # If number of blocks are even
            block_couples = [(i, i + 1) for i in range(0, n_blocks, 2)]
        else:
            block_couples = [(i, i + 1) for i in range(0, n_blocks - 1, 2)]

        for couple in block_couples:
            block1 = blockNames[couple[0]]
            block2 = blockNames[couple[1]]
            merging2Blocks(db, db2, block1, block2, block_id)  # Merge two blocks
            block_id += 1
            prev_blocks += 2

        blockNames, n_blocks = getSortedBlockNames(db)
        blockNames = blockNames[prev_blocks:]
        n_blocks = n_blocks - prev_blocks


if __name__ == "__main__":
    db = MySQLdb.connect("localhost", "teacat", 
                "123456", "WSMT3", charset='utf8' )
    db2 = MySQLdb.connect("localhost", "teacat", 
                "123456", "WSMT3", charset='utf8', 
                cursorclass = MySQLdb.cursors.SSCursor)
    print("Successfully connected. ")
    # cursor = db.cursor()
    # for i in range(176):
    #     tablename = 'Blocks_%s' % i
    #     sql = "DROP TABLE WSMT2.%s" % tablename
    #     cursor.execute(sql)
    # db.commit()
    # print("clear done!")

    time_start=time.time()
    invert_block(db)
    time_end=time.time()
    print('Construct Index done! Time: %.2f' % float(time_end-time_start))

    mergeAllBlocks(db, db2)
    print('Write files done! Time: %.2f' % float(time.time()-time_end))

    db.close()

