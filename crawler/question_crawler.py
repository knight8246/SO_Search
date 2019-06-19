import requests
from bs4 import BeautifulSoup
import operator
import os
import sys
import random
import time
import json
import re


send_headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
	"Accept-Language": "zh-CN,zh;q=0.8"
	}


def get_mainbar(elements, type='q'):
	info = {}
	if type == 'q': # if elements are from question
		info['stars'] = elements.select('.js-favorite-count')[0].text # stars
		info['tags'] = [] # tags
		for item in elements.select('.post-taglist')[0].find_all('a'):
			info['tags'].append(item.text)
	elif type == 'a':
		if elements['itemprop'] == 'acceptedAnswer':
			info['ac_flag'] = 1
		else:
			info['ac_flag'] = 0
	else:
		raise Exception
	info['votes'] = elements.select('.js-vote-count')[0].text # votes
	info['text'] = str(elements.select('.post-text')[0]) # main text
	# author
	author = elements.select('.post-signature')[-1].select('.user-details')[-1]
	info['author'] = {}
	if author.find('span', itemprop='name'): # name
		info['author']['name'] = author.find('span', itemprop='name').text
		info['author']['score'] = author.select('.reputation-score')[0].text # reputation score
		if author.find('span', title=re.compile('gold')): # gold badge
			info['author']['gold'] = author.find('span', title=re.compile('gold')).select('.badgecount')[0].text
		else:
			info['author']['gold'] = 0
		if author.find('span', title=re.compile('silver')): # silver badge
			info['author']['silver'] = author.find('span', title=re.compile('silver')).select('.badgecount')[0].text
		else:
			info['author']['silver'] = 0
		if author.find('span', title=re.compile('bronze')): # bronze badge
			info['author']['bronze'] = author.find('span', title=re.compile('bronze')).select('.badgecount')[0].text
		else:
			info['author']['bronze'] = 0
	else:
		info['author']['name'] = author.find_all('a')[-1].text
		info['author']['score'] = 0
		info['author']['gold'] = 0
		info['author']['silver'] = 0
		info['author']['bronze'] = 0
	# comment
	comment_url = 'https://stackoverflow.com/posts/'+elements.select('.comments')[0]['data-post-id']+'/comments'
	source_code_comment = requests.get(comment_url, send_headers).text
	soup_comment = BeautifulSoup(source_code_comment, 'html.parser')
	li_comments = soup_comment.find_all('li')
	info['n_comment'] = len(li_comments)
	info['comments'] = []
	for item in li_comments:
		info['comments'].append({'score':item.select('.comment-score')[0].text.strip(), 'comment':str(item.select('.comment-copy')[0]), 'user':item.select('.comment-user')[0].text})
	return info


def get_sidebar(elements, info):
	info['viewed'] = elements.select('.question-stats')[0].find_all('b')[1].text.strip().split()[0]
	# Linked questions
	info['linked'] = []
	if elements.select('.linked'):
		linked = elements.select('.linked')[0].select('.spacer')
		for item in linked:
			url_split = item.find_all('a')[-1]['href'].split('/')
			info['linked'].append(url_split[url_split.index('questions')+1])
	# Related questions
	info['related'] = []
	if elements.select('.related'):
		related = elements.select('.related')[0].select('.spacer')
		for item in related:
			url_split = item.find_all('a')[-1]['href'].split('/')
			info['related'].append(url_split[url_split.index('questions')+1])
	return info


def parse_question(start, end):
	file_size = 10000
	f1 = open('question_list.txt')
	if not os.path.exists('stackoverflow'):
		os.mkdir('stackoverflow')
	unsolved = open('unsolved.txt', 'a')
	log = open('log.txt', 'a+')
	output_file = ''
	log.seek(0, 0)
	log_lines = log.readlines()
	if log_lines:
		idx = 0
		start, valid_cnt, unsolved_cnt = list(map(int, log_lines[-1].strip().split('\t')))
		out_file = open('stackoverflow/info'+str(valid_cnt//file_size)+'.json', 'a+')
	else:
		idx = valid_cnt = unsolved_cnt = 0
	while True:
		if idx < start:
			line = f1.readline()
			idx = idx + 1
			if idx % file_size == 0:
				print(idx, valid_cnt, unsolved_cnt)
			continue
		elif idx >= end:
			break
		else:
			time.sleep(random.random()*1.5)
			if idx % file_size == 0:
				print(idx, valid_cnt, unsolved_cnt)
			line = f1.readline()
			if not line:
				break
			line_split = line.strip().split()
			page_url = 'http://stackoverflow.com' + line_split[0]
			source_code = requests.get(page_url, send_headers).text
			soup = BeautifulSoup(source_code, 'html.parser')
			try:
				# ----------question----------
				# mainbar
				question = soup.select('.question')[0]
				q_info = get_mainbar(question, 'q')
				# id, title, time
				q_info = {}
				q_info['id'] = line_split[0].split('/')[2]
				q_info['title'] = ' '.join(line_split[1:-2])
				q_info['time'] = ' '.join(line_split[-2:])
				# sidebar
				question_sidebar = soup.find('div', id='sidebar')
				q_info = get_sidebar(question_sidebar, q_info)
				# ----------answer----------
				q_info['n_answer'] = soup.select('.subheader')[0].find('span').text # the number of answers
				answers = soup.select('.answer')
				a_list = []
				for ans in answers:
					a_list.append(get_mainbar(ans, 'a'))
				q_info['answers'] = a_list
				# output file
				if valid_cnt % file_size == 0:
					out_file = open('stackoverflow/info'+str(valid_cnt//file_size)+'.json', 'w+')
				json.dump(q_info, out_file)
				out_file.write('\n')
				log.write(str(idx) + '\t' + str(valid_cnt) + '\t' + str(unsolved_cnt) + '\n')
				out_file.flush()
				log.flush()
				valid_cnt += 1
			except:
				unsolved.write(page_url + '\n')
				unsolved_cnt += 1
				pass
		idx += 1
		'''
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
		'''
	print(unsolved_cnt, 'unsolved urls.')


if __name__ == '__main__':
	parse_question(0, 2000000-1)
	# parse_question(1, sys.maxsize)

