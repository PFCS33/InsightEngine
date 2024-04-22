import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from dataSource import DataSource
from table import HierarchicalTable
from connect_LLM_sample_test import read_vis_list

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
def get_node_detail(id):
    # 在这里编写查询指定 id 的详细信息的逻辑
    # 这里假设根据 id 查询到的详细信息如下
    data_scope = {
        "Company": "Sony",
        "Brand": "*",
        "Location": "*",
        "Season": "DEC",
        "Year": 2013
    }
    response = {
        "code": 200,
        "msg": "",
        "data": {
            "dataScope": data_scope,
            "type": "dominance",
            "score": 0.878957,
            "category": "point",
            "description": "Culpa Lorem laboris tempor exercitation magna tempor tempor exercitation velit veniam elit ut.Culpa Lorem laboris tempor exercitation magna tempor tempor exercitation velit veniam elit ut."
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
    insight_list = read_vis_list(file_path)

    app.run(debug=True)


# if __name__ == '__main__':
#     #  get dataSource
#     name = filename
#     req_id = str(uuid.uuid4())
#     data_source = DataSource(name, filepath, req_id)
#     data_table = HierarchicalTable(data_source)
#     result = data_table.generate_all_results()