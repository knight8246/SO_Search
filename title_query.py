import pymysql
import time
import re
from copy import copy
from string import ascii_letters, digits, punctuation
from collections import Counter
import math
import numpy as np
from text2index import text2index

big_num = 4689857

def cos_sim(vector_a, vector_b):
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim

class TQ(object):
    def __init__(self):
        start = time.time()
        db = pymysql.connect("localhost","bert","123456","WSMT")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM TitleSum")
        res = cursor.fetchall()
        doc_len = {}
        for item in res:
            doc_len[item[0]] = item[1]
        cursor.execute("SELECT * FROM ContentSum")
        res = cursor.fetchall()
        doc_len2 = {}
        for item in res:
            doc_len2[item[0]] = item[1]
        end = time.time()
        print('initial %f seconds' % (end-start))
        self.doc_len = doc_len
        self.cursor = cursor
        self.db = db
        self.doc_len2 = doc_len2

    def title_query(self, q):
        cursor = self.cursor
        doc_len = self.doc_len

        start = time.time()

        words = text2index(q).split()
        words_freq = Counter(words)
        word_list = list(words_freq.keys())
        word_list.sort()

        doc_list = []
        doc2idx = {}
        doc_word_freq = []

        sen_ori = "SELECT Term, PostingList FROM TitleIndex WHERE"
        for i in range(len(word_list)-1):
            sen_ori = sen_ori + " Term = \'" + word_list[i] + "\' OR"
        sen_ori = sen_ori + " Term = \'" + word_list[len(word_list)-1] + "\'"
        sql_res = cursor.execute(sen_ori)
        res = cursor.fetchall()
        term2content = {}
        for item in res:
            term2content[item[0]] = item[1]
        for i in range(len(word_list)):
            doc_word_freq.append({})
            if word_list[i] in term2content.keys():
                tmp_cnt = 0
                for item in term2content[word_list[i]].split('\n')[:-1]:
                    if(item.split('\t')[0] not in doc_list):
                        tmp_cnt = tmp_cnt + 1
                        if(tmp_cnt>2000):
                            break
                        doc_list.append(item.split('\t')[0])
                        doc2idx[item.split('\t')[0]] = len(doc2idx)
                    doc_word_freq[i][item.split('\t')[0]] = int(item.split('\t')[1])
        #print(len(doc_list))
        # calculate tf-idf for query
        vec_q = []
        for i in range(len(word_list)):
            tf = words_freq[word_list[i]]/float(len(words))
            idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
            vec_q.append(tf*idf)
        # calculate tf-idf for documents
        vec_d = [[0 for i in range(len(word_list))] for j in range(len(doc_list))]
        for i in range(len(word_list)):
            for item in doc_word_freq[i]:
                tf = doc_word_freq[i][item]/float(doc_len[item])
                idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
                vec_d[doc2idx[item]][i] = tf*idf

        val = []
        for i in range(len(doc_list)):
            val.append(cos_sim(vec_q, vec_d[i]))

        doc_order = []
        tf_idf_order = np.argsort(-np.array(val))
        for item in tf_idf_order:
            doc_order.append(doc_list[item])
        end = time.time()
        #print('search %f seconds' % (end-start))

        sen_ori = "SELECT Id, Title FROM WSMJ.QuestionsJ WHERE"
        res_num = min(20, len(doc_order))
        if(res_num>0):
            for i in range(res_num-1):
                sen_ori = sen_ori + " Id = " + doc_order[i] + ' OR'
            sen_ori = sen_ori + " Id = " + doc_order[res_num-1]
            cursor.execute(sen_ori)
            res = cursor.fetchall()
            id2title = {}
            for item in res:
                id2title[int(item[0])] = item[1]

            res_for_return = []
            for item in doc_order[:res_num]:
                sub_res = {}
                sub_res['id'] = item
                sub_res['title'] = id2title[int(item)]
                res_for_return.append(sub_res)
            #print(res_for_return)
            return res_for_return, words, str(end-start)[:str(end-start).find('.')+3]
        else:
            return [], words, str(end-start)[:str(end-start).find('.')+3]

    def related_query(self, q):
        cursor = self.cursor
        doc_len = self.doc_len
        start = time.time()
        words = text2index(q).split()
        words_freq = Counter(words)
        word_list = list(words_freq.keys())
        word_list.sort()

        sen_ori = "SELECT Term, PostingList FROM TitleIndex WHERE"
        for i in range(len(word_list)-1):
            sen_ori = sen_ori + " Term = \'" + word_list[i] + "\' OR"
        sen_ori = sen_ori + " Term = \'" + word_list[len(word_list)-1] + "\'"
        sql_res = cursor.execute(sen_ori)
        res = cursor.fetchall()
        if(len(res)==0):
            end = time.time()
            return [], words, str(end-start)[:str(end-start).find('.')+3]
        term2content = {}
        for item in res:
            term2content[item[0]] = item[1].count('\n')
        new_word_list = []
        for item in word_list:
            if(term2content[item]<1000):
                new_word_list.append(item)
        word_list = new_word_list

        if(len(word_list)==0):
            tmp_end = time.time()
            return [], words, str(tmp_end-start)[:str(tmp_end-start).find('.')+3]
        doc_list = []
        doc2idx = {}
        doc_word_freq = []

        sen_ori = "SELECT Term, PostingList FROM TitleIndex WHERE"
        for i in range(len(word_list)-1):
            sen_ori = sen_ori + " Term = \'" + word_list[i] + "\' OR"
        sen_ori = sen_ori + " Term = \'" + word_list[len(word_list)-1] + "\'"
        sql_res = cursor.execute(sen_ori)
        res = cursor.fetchall()
        term2content = {}
        for item in res:
            term2content[item[0]] = item[1]
        for i in range(len(word_list)):
            doc_word_freq.append({})
            if word_list[i] in term2content.keys():
                tmp_cnt = 0
                for item in term2content[word_list[i]].split('\n')[:-1]:
                    if(item.split('\t')[0] not in doc_list):
                        tmp_cnt = tmp_cnt + 1
                        if(tmp_cnt>2000):
                            break
                        doc_list.append(item.split('\t')[0])
                        doc2idx[item.split('\t')[0]] = len(doc2idx)
                    doc_word_freq[i][item.split('\t')[0]] = int(item.split('\t')[1])

        # calculate tf-idf for query
        vec_q = []
        for i in range(len(word_list)):
            tf = words_freq[word_list[i]]/float(len(words))
            idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
            vec_q.append(tf*idf)
        # calculate tf-idf for documents
        vec_d = [[0 for i in range(len(word_list))] for j in range(len(doc_list))]
        for i in range(len(word_list)):
            for item in doc_word_freq[i]:
                tf = doc_word_freq[i][item]/float(doc_len[item])
                idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
                vec_d[doc2idx[item]][i] = tf*idf

        val = []
        for i in range(len(doc_list)):
            val.append(cos_sim(vec_q, vec_d[i]))

        doc_order = []
        tf_idf_order = np.argsort(-np.array(val))
        for item in tf_idf_order:
            doc_order.append(doc_list[item])
        end = time.time()
        #print('search %f seconds' % (end-start))

        sen_ori = "SELECT Id, Title FROM WSMJ.QuestionsJ WHERE"
        res_num = min(10, len(doc_order))
        if(res_num>0):
            for i in range(res_num-1):
                sen_ori = sen_ori + " Id = " + doc_order[i] + ' OR'
            sen_ori = sen_ori + " Id = " + doc_order[res_num-1]
            cursor.execute(sen_ori)
            res = cursor.fetchall()
            id2title = {}
            for item in res:
                id2title[int(item[0])] = item[1]

            res_for_return = []
            for item in doc_order[:res_num]:
                sub_res = {}
                sub_res['id'] = item
                sub_res['title'] = id2title[int(item)]
                res_for_return.append(sub_res)

            # print res_for_return
            return res_for_return, words, str(end-start)[:str(end-start).find('.')+3]
        else:
            return [], words, str(end-start)[:str(end-start).find('.')+3]

    def linked_query(self, q):
        cursor = self.cursor
        doc_len = self.doc_len
        start = time.time()
        words = text2index(q).split()
        words_freq = Counter(words)
        word_list = list(words_freq.keys())
        word_list.sort()

        doc_list = []
        doc2idx = {}
        doc_word_freq = []

        sen_ori = "SELECT Term, PostingList FROM TitleIndex WHERE"
        for i in range(len(word_list)-1):
            sen_ori = sen_ori + " Term = \'" + word_list[i] + "\' OR"
        sen_ori = sen_ori + " Term = \'" + word_list[len(word_list)-1] + "\'"
        sql_res = cursor.execute(sen_ori)
        res = cursor.fetchall()
        term2content = {}
        for item in res:
            term2content[item[0]] = item[1]
        for i in range(len(word_list)):
            doc_word_freq.append({})
            if word_list[i] in term2content.keys():
                tmp_cnt = 0
                for item in term2content[word_list[i]].split('\n')[:-1]:
                    if(item.split('\t')[0] not in doc_list):
                        tmp_cnt = tmp_cnt + 1
                        if(tmp_cnt>2000):
                            break
                        doc_list.append(item.split('\t')[0])
                        doc2idx[item.split('\t')[0]] = len(doc2idx)
                    doc_word_freq[i][item.split('\t')[0]] = int(item.split('\t')[1])
        # calculate tf-idf for query
        vec_q = []
        for i in range(len(word_list)):
            tf = words_freq[word_list[i]]/float(len(words))
            idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
            vec_q.append(tf*idf)
        # calculate tf-idf for documents
        vec_d = [[0 for i in range(len(word_list))] for j in range(len(doc_list))]
        for i in range(len(word_list)):
            for item in doc_word_freq[i]:
                tf = doc_word_freq[i][item]/float(doc_len[item])
                idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
                vec_d[doc2idx[item]][i] = tf*idf

        val = []
        for i in range(len(doc_list)):
            val.append(cos_sim(vec_q, vec_d[i]))

        doc_order = []
        tf_idf_order = np.argsort(-np.array(val))
        for item in tf_idf_order:
            doc_order.append(doc_list[item])
        end = time.time()
        #print('search %f seconds' % (end-start))
        if(len(doc_order)>0):
            sen_ori = "SELECT RelatedPostId FROM WSM.PostLinks WHERE PostId = " + doc_order[0]
            cursor.execute(sen_ori)
            linkedId_res = cursor.fetchall()
            if(len(linkedId_res)>0):
                sen_ori = "SELECT Id, Title FROM WSMJ.QuestionsJ WHERE"
                for i in range(len(linkedId_res)-1):
                    sen_ori = sen_ori + " Id = " + str(linkedId_res[i][0]) + ' OR'
                sen_ori = sen_ori + " Id = " + str(linkedId_res[len(linkedId_res)-1][0])

                cursor.execute(sen_ori)
                res = cursor.fetchall()
                if(len(res)==0):
                    return [], words, str(end-start)[:str(end-start).find('.')+3]

                id2title = {}
                for item in res:
                    id2title[int(item[0])] = item[1]

                res_for_return = []
                for item in id2title:
                    sub_res = {}
                    sub_res['id'] =  str(item)
                    sub_res['title'] = id2title[item]
                    res_for_return.append(sub_res)

                    # print res_for_return
                return res_for_return, words, str(end-start)[:str(end-start).find('.')+3]
            else:
                return [], words, str(end-start)[:str(end-start).find('.')+3]
        else:
            return [], words, str(end-start)[:str(end-start).find('.')+3]

    def body_query(self, q):
        cursor = self.cursor
        doc_len = self.doc_len2

        start = time.time()

        words = text2index(q).split()
        words_freq = Counter(words)
        word_list = list(words_freq.keys())
        word_list.sort()

        doc_list = []
        doc2idx = {}
        doc_word_freq = []

        sen_ori = "SELECT Term, PostingList FROM WSMT.ContentIndex WHERE"
        for i in range(len(word_list)-1):
            sen_ori = sen_ori + " Term = \'" + word_list[i] + "\' OR"
        sen_ori = sen_ori + " Term = \'" + word_list[len(word_list)-1] + "\'"
        sql_res = cursor.execute(sen_ori)
        res = cursor.fetchall()
        term2content = {}
        for item in res:
            term2content[item[0]] = item[1]
        for i in range(len(word_list)):
            doc_word_freq.append({})
            if word_list[i] in term2content.keys():
                tmp_cnt = 0
                for item in term2content[word_list[i]].split('\n')[:-1]:
                    if(item.split('\t')[0] not in doc_list):
                        tmp_cnt = tmp_cnt + 1
                        if(tmp_cnt>2000):
                            break
                        doc_list.append(item.split('\t')[0])
                        doc2idx[item.split('\t')[0]] = len(doc2idx)
                    doc_word_freq[i][item.split('\t')[0]] = int(item.split('\t')[1])
        #print(len(doc_list))
        # calculate tf-idf for query
        vec_q = []
        for i in range(len(word_list)):
            tf = words_freq[word_list[i]]/float(len(words))
            idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
            vec_q.append(tf*idf)
        # calculate tf-idf for documents
        vec_d = [[0 for i in range(len(word_list))] for j in range(len(doc_list))]
        for i in range(len(word_list)):
            for item in doc_word_freq[i]:
                tf = doc_word_freq[i][item]/float(doc_len[item])
                idf = math.log(float(big_num)/(len(doc_word_freq[i])+1))
                vec_d[doc2idx[item]][i] = tf*idf

        val = []
        for i in range(len(doc_list)):
            val.append(cos_sim(vec_q, vec_d[i]))

        doc_order = []
        tf_idf_order = np.argsort(-np.array(val))
        for item in tf_idf_order:
            doc_order.append(doc_list[item])
        end = time.time()
        #print('search %f seconds' % (end-start))

        sen_ori = "SELECT Id, Title FROM WSMJ.QuestionsJ WHERE"
        res_num = min(20, len(doc_order))
        if(res_num>0):
            for i in range(res_num-1):
                sen_ori = sen_ori + " Id = " + doc_order[i] + ' OR'
            sen_ori = sen_ori + " Id = " + doc_order[res_num-1]
            cursor.execute(sen_ori)
            res = cursor.fetchall()
            id2title = {}
            for item in res:
                id2title[int(item[0])] = item[1]

            res_for_return = []
            for item in doc_order[:res_num]:
                sub_res = {}
                sub_res['id'] = item
                sub_res['title'] = id2title[int(item)]
                res_for_return.append(sub_res)
            #print(res_for_return)
            return res_for_return, words, str(end-start)[:str(end-start).find('.')+3]
        else:
            return [], words, str(end-start)[:str(end-start).find('.')+3]

    def get_answers(self, QuestionId):
        cursor = self.db.cursor()
        sql = "SELECT Id,Title,Score,OwnerUserId,CommentCount,\
               CreationDate,AcceptedAnswerId \
               FROM WSMJ.QuestionsJ \
               WHERE Id = %s" % QuestionId
        cursor.execute(sql)
        res = cursor.fetchone()

        qst_info = {}
        qst_info['Id'] = res[0]
        qst_info['Title'] = res[1]
        qst_info['Score'] = res[2]
        qst_info['OwnerUserId'] = res[3]
        qst_info['CommentCount'] = res[4]
        qst_info['CreationDate'] = res[5]
        qst_info['AcceptedAnswerId'] = res[6]
        qst_info['UserName'] = ""

        sql = "SELECT DisplayName FROM WSM.Users \
               WHERE Id = %d" % qst_info['OwnerUserId']
        cursor.execute(sql)
        res = cursor.fetchone()
        if res:
            qst_info['UserName'] = res[0]

        sql = "SELECT Id,Body,Score,OwnerUserId,CommentCount,\
               CreationDate FROM WSMJ.AnswersJ \
               WHERE ParentId = %s" % QuestionId
        cursor.execute(sql)
        res = cursor.fetchall()

        get_name = self.db.cursor()
        ans_list = []
        if not res:
            return qst_info, ans_list
        for ans in res:
            ans_info = {}
            ans_info['Id'] = ans[0]
            ans_info['Body'] = ans[1]
            ans_info['Score'] = ans[2]
            ans_info['OwnerUserId'] = ans[3]
            ans_info['CommentCount'] = ans[4]
            ans_info['CreationDate'] = ans[5]
            ans_info['Accepted'] = False
            ans_info['UserName'] = ""
            sql = "SELECT DisplayName FROM WSM.Users \
               WHERE Id = %d" % ans_info['OwnerUserId']
            get_name.execute(sql)
            name = get_name.fetchone()
            if name:
                ans_info['UserName'] = name[0]
            ans_list.append(ans_info)

        if qst_info['AcceptedAnswerId']:
            for ans in ans_list:
                if ans['Id']==qst_info['AcceptedAnswerId']:
                    ans['Accepted'] = True
                    break

        ans_list.sort(key=lambda ans:ans['CommentCount'], reverse=True)
        ans_list.sort(key=lambda ans:ans['Score'], reverse=True)
        ans_list.sort(key=lambda ans:ans['Accepted'], reverse=True)

        return qst_info, ans_list

    def get_comments(self, PostId):
        cursor = self.db.cursor()
        sql = "SELECT Text,Score,UserId,\
               CreationDate FROM WSMJ.CommentsJ \
               WHERE PostId = %s" % PostId
        cursor.execute(sql)
        res = cursor.fetchall()

        get_name = self.db.cursor()
        ans_list = []
        if not res:
            return ans_list
        for ans in res:
            ans_info = {}
            ans_info['Text'] = ans[0]
            ans_info['Score'] = ans[1]
            ans_info['UserId'] = ans[2]
            ans_info['CreationDate'] = ans[3]
            ans_info['UserName'] = ""
            sql = "SELECT DisplayName FROM WSM.Users \
               WHERE Id = %d" % ans_info['UserId']
            get_name.execute(sql)
            name = get_name.fetchone()
            if name:
                ans_info['UserName'] = name[0]
            ans_list.append(ans_info)

        ans_list.sort(key=lambda ans:ans['Score'], reverse=True)

        return ans_list


if __name__ == '__main__':
    qt = TQ()
    q = 'How do i bypass call instruction suspending program? [duplicate]'
    doc_order =qt.body_query(q)
    # print doc_order[:10]
