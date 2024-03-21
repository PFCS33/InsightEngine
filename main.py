import os
import uuid
from dataSource import DataSource
from table import HierarchicalTable

file_name = 'console_sales_flat.csv'
file_path = os.path.join('data', file_name)

if __name__ == '__main__':
    #  get dataSource
    name = file_name
    req_id = str(uuid.uuid4())
    data_source = DataSource(name, file_path, req_id)
    data_table = HierarchicalTable(data_source)
    result = data_table.generate_all_results()
