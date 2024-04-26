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

    # TODO set init nodes
    # insights_info = get_insight_vega_by_header("()", insight_list)

    nodes = [
        {
            "id": 1,
            "realId": 1,
            "type": "dominance",
            "category": "point",
            "vegaLite": "{'data': {'values': [{'category': 'MAR', 'value': 1300.0}, {'category': 'JUN', 'value': 360.0}, {'category': 'SEP', 'value': 390.0}, {'category': 'DEC', 'value': 440.0}]}, 'mark': {'type': 'arc', 'innerRadius': 5, 'stroke': '#fff'}, 'encoding': {'theta': {'field': 'value', 'type': 'quantitative', 'stack': true}, 'color': {'field': 'category', 'type': 'nominal', 'legend': null}, 'order': {'field': 'value', 'type': 'quantitative', 'sort': 'descending'}, 'radius': {'field': 'value', 'scale': {'type': 'linear', 'zero': true, 'rangeMin': 20}}, 'tooltip': [{'field': 'category', 'type': 'nominal'}, {'field': 'value', 'type': 'quantitative'}]}}"
        },
        {
            "id": 2,
            "realId": 2,
            "type": "skewness",
            "category": "shape",
            "vegaLite": "{'data': {'values': [{'category': 'MAR', 'value': 1300.0}, {'category': 'JUN', 'value': 360.0}, {'category': 'SEP', 'value': 390.0}, {'category': 'DEC', 'value': 440.0}]}, 'mark': {'type': 'arc', 'innerRadius': 5, 'stroke': '#fff'}, 'encoding': {'theta': {'field': 'value', 'type': 'quantitative', 'stack': true}, 'color': {'field': 'category', 'type': 'nominal', 'legend': null}, 'order': {'field': 'value', 'type': 'quantitative', 'sort': 'descending'}, 'radius': {'field': 'value', 'scale': {'type': 'linear', 'zero': true, 'rangeMin': 20}}, 'tooltip': [{'field': 'category', 'type': 'nominal'}, {'field': 'value', 'type': 'quantitative'}]}}"
        },
        {
            "id": 3,
            "realId": 10,
            "type": "compound",
            "category": "correlation",
            "vegaLite": "{'data': {'values': [{'category': 'MAR', 'value': 1300.0}, {'category': 'JUN', 'value': 360.0}, {'category': 'SEP', 'value': 390.0}, {'category': 'DEC', 'value': 440.0}]}, 'mark': {'type': 'arc', 'innerRadius': 5, 'stroke': '#fff'}, 'encoding': {'theta': {'field': 'value', 'type': 'quantitative', 'stack': true}, 'color': {'field': 'category', 'type': 'nominal', 'legend': null}, 'order': {'field': 'value', 'type': 'quantitative', 'sort': 'descending'}, 'radius': {'field': 'value', 'scale': {'type': 'linear', 'zero': true, 'rangeMin': 20}}, 'tooltip': [{'field': 'category', 'type': 'nominal'}, {'field': 'value', 'type': 'quantitative'}]}}"
        }
    ]

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
    insight_id = data.get('id')
    query = data.get('content')

    item = insight_list[insight_id]
    next_nodes = qa_LLM(query, item)

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
    insight_list = read_vis_list_into_insights('vis_list_VegaLite.txt')

    app.run(debug=True, port=5000)


