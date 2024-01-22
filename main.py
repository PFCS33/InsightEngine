import os
import uuid
from dataSource import DataSource
from table import HierarchicalTable

file_name = 'console_sales2.xlsx'
file_path = os.path.join('data', file_name)

if __name__ == '__main__':
    #  get dataSource
    name_no_suffix = file_name.split('.')[0]
    req_id = str(uuid.uuid4())
    data_source = DataSource(name_no_suffix, file_path, req_id)
    data_table = HierarchicalTable(data_source)
    result = data_table.generate_all_results()
