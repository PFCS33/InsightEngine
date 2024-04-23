import os
import uuid
from dataSource import DataSource
from table import HierarchicalTable

filename = 'console_sales_flat.csv'
filepath = os.path.join('data', filename)

if __name__ == '__main__':
    #  get dataSource
    name = filename
    req_id = str(uuid.uuid4())
    data_source = DataSource(name, filepath, req_id)
    data_table = HierarchicalTable(data_source)
    result = data_table.generate_all_results()