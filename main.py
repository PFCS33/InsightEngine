import json
import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from dataSource import DataSource
from table import HierarchicalTable
from connect_LLM_sample_test import *
from query_for_server import *

global data_table
global node_id
global header_list
global insight_list

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = 'uploads'

filename = 'console_sales_flat.csv'
filepath = os.path.join('data', filename)

def upload_table():
    # if 'file' not in request.files:
    #     return jsonify({'error': 'No file part'})
    #
    # file = request.files['file']
    #
    # if file.filename == '':
    #     return jsonify({'error': 'No selected file'})
    #
    # if file:
    #     filename = secure_filename(file.filename)
    #     folder = app.config['UPLOAD_FOLDER']
    #     if not os.path.exists(folder):
    #         os.makedirs(folder)
    #     filepath = os.path.join(folder, filename)
    #     file.save(filepath)
    #
    #     # process the uploading table
    #     req_id = str(uuid.uuid4())
    #     result = create_table(filename, filepath, req_id)
    #
    #     # return the result to frontend
    #     return jsonify(result)

    req_id = str(uuid.uuid4())
    result = create_table(filename, filepath, req_id)

    # return the result to frontend
    return jsonify(result)


@app.route('/filter/id', methods=['GET'])
@cross_origin()
def get_node_id():
    global node_id
    node_id += 1
    response = {
        "code": 200,
        "msg": "",
        "data": {
            "id": node_id
        }
    }
    return jsonify(response)


@app.route('/panel/<int:id>', methods=['GET'])
@cross_origin()
def get_node_detail(realid):
    item = get_insight_by_id(insight_list, realid)
    data_scope = convert_header_to_data_scope(item['Header'])

    response = {
        "code": 200,
        "msg": "",
        "data": {
            "dataScope": data_scope,
            "type": item['Type'],
            "score": item['Score'],
            "category": item['Category'],
            "description": item['Description']
        }
    }
    return jsonify(response)


@app.route('/filter/scope', methods=['POST'])
@cross_origin()
def post_data_scope(data_scope):
    header = convert_data_scope_to_header(data_scope)
    header = str(header)

    insights_info = get_insight_vega_by_header(header, insight_list)

    response = {
        "code": 200,
        "msg": "",
        "data": {
            "insights": insights_info
        }
    }
    return jsonify(response)


@app.route('/panel/id-list', methods=['POST'])
@cross_origin()
def post_id_list():
    id_list = request.json
    vl_list = []

    for id in id_list:
        vl_spec = get_vega_lite_spec_by_id(id, insight_list)
        vl_list.append(vl_spec)

    response = {
        "code": 200,
        "msg": "",
        "data": {
            "vlList": vl_list
        }
    }

    return jsonify(response)


@app.route('/question/data', methods=['POST'])
@cross_origin()
def get_next_insights():
    data = request.json
    question_id = data.get('id')
    question_content = data.get('content')

    # 假设 nodes 是包含所有 insight 信息的列表
    # 这里需要根据你的实际数据结构来获取 nodes
    nodes = {...}  # 假设这里是你的 insight 列表

    # 构建响应的 nodes 列表
    next_nodes = []
    for node in nodes:
        next_node = {
            "id": node.get('id'),
            "real_id": node.get('real_id'),
            "type": node.get('type'),
            "category": node.get('category'),
            "relationship": node.get('relationship'),
            "vega-lite": node.get('vega-lite')
        }
        next_nodes.append(next_node)

    # 构建响应
    response = {
        "code": 200,
        "msg": "",
        "data": {
            "nodes": next_nodes
        }
    }
    return jsonify(response)


def create_table(name, path, req_id):
    data_source = DataSource(name, path, req_id)
    global data_table
    data_table = HierarchicalTable(data_source)
    global node_id
    node_id = 0
    result = data_table.generate_all_results()

    return jsonify(result)

if __name__ == '__main__':
    file_path = 'vis_list.txt'
    header_list = read_vis_list(file_path)
    insight_list = read_vis_list_into_insights('vis_list_VegaLite.txt')

    app.run(debug=True)


# if __name__ == '__main__':
#     #  get dataSource
#     name = filename
#     req_id = str(uuid.uuid4())
#     data_source = DataSource(name, filepath, req_id)
#     data_table = HierarchicalTable(data_source)
#     result = data_table.generate_all_results()