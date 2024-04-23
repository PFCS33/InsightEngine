import json

# get header list
def read_vis_list_vegalite(file_path):
    global header_list_vegalite
    header_list_vegalite = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Header:"):
                header = eval(line.split(":")[1].strip())
                insights = []
                i += 1
                while i < len(lines) and not lines[i].startswith("Header:"):
                    if lines[i].startswith("Insight"):
                        insight_type = lines[i + 1].split(":")[1].strip()
                        insight_score = float(lines[i + 2].split(":")[1].strip())
                        insight_category = lines[i + 3].split(":")[1].strip()
                        insight_description = lines[i + 4].split(":")[1].strip()
                        data_str = lines[i + 5]
                        index = data_str.index('Vega-Lite Json: ')
                        insight_vegalite = data_str[index + len('Vega-Lite Json: '):]
                        insights.append(
                            {"Type": insight_type, "Score": insight_score, "Category": insight_category,
                             "Description": insight_description, "Vega-Lite": insight_vegalite})
                        i += 6
                    else:
                        i += 1
                header_list_vegalite.append({"Header": header, "Insights": insights})
            else:
                i += 1
    return header_list_vegalite

# insight list, fully info
def read_vis_list_into_insights(file_path):
    global insight_list
    insight_list = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Header:"):
                header = eval(line.split(":")[1].strip())
                insights = []
                i += 1
                while i < len(lines) and not lines[i].startswith("Header:"):
                    if lines[i].startswith("Insight"):
                        insight_type = lines[i + 1].split(":")[1].strip()
                        insight_score = float(lines[i + 2].split(":")[1].strip())
                        insight_category = lines[i + 3].split(":")[1].strip()
                        insight_description = lines[i + 4].split(":")[1].strip()
                        data_str = lines[i + 5]
                        index = data_str.index('Vega-Lite Json: ')
                        insight_vegalite = data_str[index + len('Vega-Lite Json: '):]
                        insight_list.append({"Header": header, "Type": insight_type, "Score": insight_score,
                                             "Category": insight_category, "Description": insight_description, "Vega-Lite": insight_vegalite})
                        i += 6
                    else:
                        i += 1
            else:
                i += 1
    return insight_list

def get_insight_vega_by_header(header_str, insight_list):
    header = eval(header_str)
    # sort for matching
    header = tuple(sorted(map(str, header)))

    insights_info = []
    for index, item in enumerate(insight_list):
        if item['Header'] == header:
            insight_info = {
                'realId': index,
                'type': item['Type'],
                'category': item['Category'],
                'score': item['Score'],
                'description': item['Description'],
                'vega-lite': item['Vega-Lite']
            }
            insights_info.append(insight_info)
    return insights_info


def get_vega_lite_spec_by_id(id, insight_list):
    # id: insight id (node real-id)
    item = insight_list[id]
    vl_spec = item['Vega-Lite']
    return vl_spec


def get_insight_by_id(insight_list, id):
    # id: insight id (node real-id)
    item = insight_list[id]
    return item


table_structure = {
    'Company': ['Nintendo', 'Sony', 'Microsoft'],
    'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)',
              'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)', 'Xbox 360 (X360)',
              'Xbox One (XOne)'],
    'Location': ['Europe', 'Japan', 'North America', 'Other'],
    'Season': ['DEC', 'JUN', 'MAR', 'SEP'],
    'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
}

def convert_header_to_data_scope(header):
    data_scope = {
        'Company': '*',
        'Brand': '*',
        'Location': '*',
        'Season': '*',
        'Year': '*'
    }

    for key, value in zip(table_structure.keys(), header):
        if value in table_structure[key]:
            data_scope[key] = value

    return {'dataScope': data_scope}

def convert_data_scope_to_header(data_scope):
    data_dict = json.loads(data_scope)
    header = []
    for key in ['Company', 'Brand', 'Location', 'Season', 'Year']:
        value = data_dict.get(key, '*')
        if value != '*':
            header.append(value)
    return tuple(header)


insight_list = read_vis_list_into_insights('vis_list_VegaLite.txt')
id_list = [1, 4, 6, 88]
vl_list = []

for id in id_list:
    vl_spec = get_vega_lite_spec_by_id(id, insight_list)
    vl_list.append(vl_spec)