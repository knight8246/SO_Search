import requests
from bs4 import BeautifulSoup
import operator
import os
import sys
import random
import time

def get_question_list():
    send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.8"
    }

    o1 = open('question_list.txt', 'a+')
    log = open('log.txt', 'a+')
    page_num = 52354
    stop = False
    while True:
        time.sleep(random.random()*1.5)
        page_url = 'http://stackoverflow.com/questions?page=' + str(page_num) + '&sort=newest'
        source_code = requests.get(page_url, send_headers).text
        #i1 = open('output.txt')
        #source_code = i1.read()
        #print(source_code)
        soup = BeautifulSoup(source_code, 'html.parser')
        q_summary = soup.select('.summary')
        num_per_page = 0
        for q_item in q_summary:
            try:
                q_info = q_item.find('h3').find('a')
                q_href = q_info['href']
                q_text = q_info.text
                q_time = q_item.select('.user-action-time')[0].find('span')['title']
                if(page_num>60000):
                    stop = True
                    break
                o1.write(q_href + '\t' + q_text + '\t' + q_time + '\n')
                num_per_page = num_per_page + 1
            except:
                continue
        if(stop):
            break
        log.write(str(page_num) + '\t' + str(num_per_page) + '\n')   
        log.flush()
        o1.flush()
        page_num = page_num + 1 
        


if __name__ == '__main__':
    get_question_list()

