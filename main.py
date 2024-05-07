import json
import os
import random
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from dataSource import DataSource
from table import HierarchicalTable
from connect_LLM_sample_test import *
from query_for_server import *
from asyncio import run

global data_table
global node_id
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


@app.route('/graph/data', methods=['GET'])
@cross_origin()
def get_graph_data():
    columnInfo = {
        "Company": ["*", "Nintendo", "Sony", "Microsoft"],
        "Brand": ["*", "Nintendo 3DS (3DS)", "Nintendo DS (DS)", "Nintendo Switch (NS)", "Wii (Wii)", "Wii U (WiiU)", "PlayStation 3 (PS3)", "PlayStation 4 (PS4)", "PlayStation Vita (PSV)", "Xbox 360 (X360)", "Xbox One (XOne)"],
        "Location": ["*", "Europe", "Japan", "North America", "Other"],
        "Season": ["*", "MAR", "JUN", "SEP", "DEC"],
        "Year": ["*", 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    }

    # set init nodes
    nodes = []
    global node_id

    # global insights of source table
    insights_info = get_insight_vega_by_header("()", insight_list)
    for item in insights_info:
        node_id += 1
        node = {
            "id": node_id,
            "realId": item['realId'],
            "type": item['type'],
            "category": item['category'],
            "vegaLite": item['vegaLite']
        }
        nodes.append(node)

    # insights with the highest score
    k = 50
    insights_info = get_top_k_insights(k, insight_list)

    random_selection = random.sample(insights_info, 5)
    for item in random_selection:
        if not any(node['realId'] == item['realId'] for node in nodes):
            node_id += 1
            node = {
                "id": node_id,
                "realId": item['realId'],
                "type": item['type'],
                "category": item['category'],
                "vegaLite": item['vegaLite']
            }
            nodes.append(node)

    response = {
        "code": 200,
        "msg": "",
        "data": {
            "columnInfo": columnInfo,
            "nodes": nodes
        }
    }
    return jsonify(response)


@app.route('/filter/id', methods=['GET'])
@cross_origin()
def get_node_id():
    print("--------------------------------------------")
    print("get_node_id")
    global node_id
    node_id += 1
    response = {
        "code": 200,
        "msg": "",
        "data": {
            "id": node_id
        }
    }
    print(f"node_id: {node_id}")
    return jsonify(response)


@app.route('/panel/<int:realid>', methods=['GET'])
@cross_origin()
def get_node_detail(realid):
    print("--------------------------------------------")
    print("get_node_detail")
    print(f"realid: {realid}")
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
    print(f"response: {response}")
    return jsonify(response)


@app.route('/filter/scope', methods=['POST'])
@cross_origin()
def post_data_scope():
    print("--------------------------------------------")
    print("post_data_scope")
    print(f"data_scope: {request.data}")
    data_scope = request.data
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
    print(f"response: {response}")
    return jsonify(response)


@app.route('/panel/id-list', methods=['POST'])
@cross_origin()
def post_id_list():
    print("--------------------------------------------")
    print("post_id_list")
    print(f"id_list: {request.json}")
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
    print(f"response: {response}")
    return jsonify(response)


@app.route('/question/data', methods=['POST'])
@cross_origin()
def get_next_insights():
    print("--------------------------------------------")
    print("get_next_insights")
    print(f"data: {request.json}")

    data = request.json
    insight_id = data.get('id')
    query = data.get('content')

    print(f"insight_id: {insight_id}")
    print(f"query: {query}")

    global node_id
    item = insight_list[insight_id]
    next_nodes, node_id = run(qa_LLM(query, item, insight_list, node_id))

    response = {
        "code": 200,
        "msg": "",
        "data": {
            "nodes": next_nodes
        }
    }
    print(f"response: \n{response}")
    return jsonify(response)


def create_table(name, path, req_id):
    data_source = DataSource(name, path, req_id)
    global data_table
    data_table = HierarchicalTable(data_source)
    result = data_table.generate_all_results()

    return jsonify(result)

if __name__ == '__main__':
    global node_id
    node_id = 0

    file_path = 'vis_list.txt'
    insight_list = read_vis_list_into_insights('vis_list_VegaLite.txt')

    app.run(debug=True, port=5000)


