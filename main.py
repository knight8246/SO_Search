# coding:utf-8
from flask import Flask, request, render_template, redirect, url_for
import re
from title_query import TQ
from text2index import text2index
from urllib import parse
import json

app = Flask(__name__, static_url_path='')
qt = TQ()

# Main Pages
@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search1', query=query))
    # return render_template('index.html')
    return render_template('home.html')

@app.route("/t2", methods=['POST', 'GET'])
def home2():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search2', query=query))
    # return render_template('index.html')
    return render_template('home2.html')

@app.route("/t3", methods=['POST', 'GET'])
def home3():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search3', query=query))
    # return render_template('index.html')
    return render_template('home3.html')

@app.route("/t4", methods=['POST', 'GET'])
def home4():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search4', query=query))
    # return render_template('index.html')
    return render_template('home4.html')

@app.route("/t5", methods=['POST', 'GET'])
def home5():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search5', query=query))
    # return render_template('index.html')
    return render_template('home5.html')


# Search Results
@app.route("/q/<query>", methods=['POST', 'GET'])
def search1(query):
    docs, terms, time = qt.related_query(query)
    docs = parse(docs, terms)
    return render_template('results.html', docs=docs, value=query, length=len(docs), time=time)

@app.route("/q2/<query>", methods=['POST', 'GET'])
def search2(query):
    docs, terms, time = qt.linked_query(query)
    docs = parse(docs, terms)
    return render_template('results2.html', docs=docs, value=query, length=len(docs), time=time)

@app.route("/q3/<query>", methods=['POST', 'GET'])
def search3(query):
    docs, terms, time = qt.title_query(query)
    docs = parse(docs, terms)
    return render_template('results3.html', docs=docs, value=query, length=len(docs), time=time)

@app.route("/q4/<query>", methods=['POST', 'GET'])
def search4(query):
    docs, terms, time = qt.body_query(query)
    docs = parse(docs, terms)
    return render_template('results4.html', docs=docs, value=query, length=len(docs), time=time)

@app.route("/q5/<query>", methods=['POST', 'GET'])
def search5(query):
    docs, terms, time = qt.title_query(query)
    docs = parse(docs, terms)
    return render_template('results5.html', docs=docs, value=query, length=len(docs), time=time)


@app.route("/ans/<id>", methods=['POST', 'GET'])
def getAnswers(id):
    question, docs = qt.get_answers(id)
    return render_template('answers.html', q=question, docs=docs, length=len(docs))

@app.route("/comm/<id>", methods=['POST', 'GET'])
def getComments(id):
    docs = qt.get_comments(id)
    return render_template('comments.html', docs=docs, length=len(docs))


def parse(docs, terms):
    for doc in docs:
        # -----highlight-----
        content = doc['title']
        content_array = content.split(' ')
        for term in terms:
            for i in range(len(content_array)):
                if (term.lower()==content_array[i].lower()):
                    content_array[i] = '<em><font color="red">{}</font></em>'.format(content_array[i])
        doc['title'] = ' '.join(content_array)
            # reg = re.compile(re.escape(term), re.IGNORECASE)
            # if (reg.search(content) != None):
            #     content = reg.sub('<em><font color="red">{}</font></em>'.format(reg.search(content).group()), content)
            # content = content.replace(term, '<em><font color="red">{}</font></em>'.format(term))
        doc['link'] = 'https://stackoverflow.com/questions/' + str(doc['id'])
    return docs


# index = Indexer("docs.txt")
# searcher = Searcher(index)

if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=False)