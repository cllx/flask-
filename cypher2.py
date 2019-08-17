from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_from_directory,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from py2neo import Graph,Node,Relationship,cypher
from pandas import DataFrame
import random
import os
import json
from json_to_csv import json_to_csv
import alignment_boshihou_pre_deal
import xiaoqi
app = Flask(__name__)

def get_files(path='static/TransE_img/', rule=".png"):
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk获取所有的目录
        for f in fs:
            filename = os.path.join(fpathe,f)
            if filename.endswith(rule):  # 判断是否是".png"结尾
                all.append(filename)
    return all

def get_node_link(res):
    temp = res.iloc[:,:]
    for i in range(0,len(temp)):
        tmp = {}
        id_list = []
        for dic in node:
            id_list.append(dic['name'])
        if temp.iloc[i]['Person']['id'] not in id_list:
            tmp['name'] = temp.iloc[i]['Person']['id']
            tmp['label'] = temp.iloc[i]['Person']['name']
            tmp['category'] = random.randint(1,10)
            tmp['value'] = random.randint(1,3)
            node.append(tmp)
        tmp = {}
        if temp.iloc[i]['tail']['id'] not in id_list:
            tmp['name'] = temp.iloc[i]['tail']['id']
            tmp['label'] = temp.iloc[i]['tail']['name']
            tmp['category'] = random.randint(1,10)
            tmp['value'] = random.randint(1,3)
            node.append(tmp)
        rela = {}
        rela['source'] = temp.iloc[i]['Person']['id']
        rela['target'] = temp.iloc[i]['tail']['id']
        rela['label'] = temp.iloc[i]['r']['pro1']
        rela['value'] = random.randint(1,10)
        link.append(rela)
    node_link['node'] = node
    node_link['link'] = link

@app.route('/get_align_json')
def get_align_json():
    return render_template('align_download.html') 

@app.route('/align')
def align():
    filename = request.args.get('filename')
    filename = filename+'.json'
    fname = filename.encode('utf-8').decode('utf-8')
    dirpath = 'static/align_json/'
    response = make_response(send_from_directory(dirpath, fname, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(dirpath.encode().decode('latin-1'))
    return send_from_directory(dirpath, fname)

@app.route('/get_xiaoqi_json')
def get_xiaoqi_json():
    return render_template('xiaoqi_download.html')

@app.route('/xiaoqi')
def xiaoqi():
    filename = request.args.get('filename')
    filename = filename+'_bom.json'
    fname = filename.encode('utf-8').decode('utf-8')
    dirpath = 'static/xiaoqi_json/'
    response = make_response(send_from_directory(dirpath, fname, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(dirpath.encode().decode('latin-1'))
    return send_from_directory(dirpath, fname)

@app.route('/get_query')
def get_relation_page():
    return render_template('query.html')

@app.route('/get_attribute', methods=['GET', 'POST'])
def get_attribute():
    if request.method == 'POST':
        filename = request.form['filename']
        attribute = request.form["attribute"]
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query = "MATCH (Person {name:'"+filename+"'})-[r:rel{pro1:'"+attribute+"'}]->(tail) with Person,r,tail RETURN Person,r,tail"
        res = test_graph.run(query).data()
        res = DataFrame(res)
        get_node_link(res)
        if len(node_link['node'])==0 or len(node_link['link'])==0:
            node_link = False
            return render_template('yuanshi_map.html', yuanshi_info=node_link)
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
        return render_template('index.html', yuanshi_info=node_link, filename=filename)

@app.route('/get_relation', methods=['GET', 'POST'])
def get_relation():
    if request.method == 'POST':
        filename1 = request.form['filename1']
        filename2 = request.form['filename2']
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query1 = "MATCH (Person {name:'"+filename1+"'})-[r]-(tail) with Person,r,tail return Person,r,tail"
        query2 = "MATCH (Person {name:'"+filename2+"'})-[r]-(tail) with Person,r,tail return Person,r,tail"
        res1 = test_graph.run(query1).data()
        res1 = DataFrame(res1)
        res2 = test_graph.run(query2).data()
        res2 = DataFrame(res2)
        get_node_link(res1)
        get_node_link(res2)
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
        return render_template('index.html', yuanshi_info=node_link, filename=filename1)

@app.route('/get_single_page')
def get_single_page():
    return render_template('single_person.html')

@app.route('/single_info', methods=['GET', 'POST'])
def single_info():
    if request.method == 'POST':
        filename1 = request.form['filename']
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query = "MATCH (Person {name:'"+filename1+"'})-[r]-(tail) with Person,r,tail return Person,r,tail"
        res = test_graph.run(query).data()
        res = DataFrame(res)
        get_node_link(res)
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
        return render_template('index.html', yuanshi_info=node_link, filename=filename1)

@app.route('/single_info2', methods=['GET', 'POST'])
def single_info2():
    filename = request.args.get('filename')
    global node
    global link
    global node_link
    node = []
    link = []
    node_link = {}
    test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
    query = "MATCH (Person {name:'"+filename+"'})-[r]-(tail) with Person,r,tail return Person,r,tail"
    res = test_graph.run(query).data()
    res = DataFrame(res)
    get_node_link(res)
    node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
    return render_template('index.html', yuanshi_info=node_link, filename=filename)
		
@app.route('/select_TransE')
def select_TransE():
    return render_template('transe_entreace.html')
	
@app.route('/transe_generate_deal_csv')
def transe_generate_deal_csv():
    filename = request.args.get('filename')
    imgname = filename+'.png'
    transeimg = get_files()
    for i in transeimg:
        savedimg = i.split('/')[-1]
        if imgname==savedimg:
            respath = 'static/TransE_img/'+imgname
            return render_template('index.html', transe_res=respath, filename=filename)
    json2csv = json_to_csv()
    json2csv.main(filename)
    respath = 'static/TransE_img/'+imgname
    return render_template('index.html', transe_res=respath, tips='time_wait', filename=filename)

@app.route('/get_haved_yuanshi')
def get_haved_yuanshi():
    test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
    all_yuanshi_name = test_graph.run("MATCH (n:yuanshi) RETURN n").data()
    all_yuanshi_name = DataFrame(all_yuanshi_name)
    temp = all_yuanshi_name.iloc[:,:]
    yuanshi_name_list = []
    for i in range(0,len(temp)):
        yuanshi_name_list.append(temp.iloc[i]['n']['name'])
    return render_template('index.html', haved_yuanshi=yuanshi_name_list)

@app.route('/get_new_yuanshi')
def get_new_yuanshi():
    return render_template('get_new.html')

@app.route('/generate_resume', methods=['GET', 'POST'])
def generate_resume():
    if request.method == 'POST':
        filename = request.form['filename']
        xiaoqi_res = alignment_boshihou_pre_deal.main(filename)
        print("***********消歧处理结果：",xiaoqi_res)
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query = "MATCH (Person {name:'"+filename+"'})-[r]-(tail) with Person,r,tail return Person,r,tail"
        res = test_graph.run(query).data()
        res = DataFrame(res)
        get_node_link(res)
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
        return render_template('index.html', yuanshi_info=node_link, filename=filename, generate_resume="success")
 
if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(debug = True, threaded=True)