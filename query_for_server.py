import json
from connect_LLM_sample_test import get_related_subspace, get_response, parse_response_select_group, read_vis_list, \
    parse_response_select_insight
from asyncio import run

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
                                             "Category": insight_category, "Description": insight_description,
                                             "Vega-Lite": insight_vegalite})
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
                'vegaLite': item['Vega-Lite']
            }
            insights_info.append(insight_info)
    return insights_info


def get_vega_lite_spec_by_id(id, insight_list):
    # id: insight id (node real-id)
    print(id)
    item = insight_list[id]
    vl_spec = item['Vega-Lite']
    print(vl_spec)
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

    for value in header:
        for key, values_list in table_structure.items():
            if value in values_list:
                data_scope[key] = value
                break

    return data_scope


def convert_data_scope_to_header(data_scope):
    data_dict = json.loads(data_scope)
    header = []
    for key in ['Company', 'Brand', 'Location', 'Season', 'Year']:
        value = data_dict.get(key, '*')
        if value != '*':
            header.append(value)
    return tuple(header)


question2_prompt = """
Next, I will provide you with some other subspaces related to the current subspace in terms of header structure. 
"""


async def qa_LLM(query, item, insight_list, node_id):
    question2 = combine_question2(query, item)

    question3 = combine_question3(query, item)
    # let LLM select one group that best matches the question and crt subspace
    response = get_response(question2 + question3)

    insights_info_dict, sort_insight_prompt, reason = parse_response_select_group(response, query, insight_list)

    # let LLM sort insights
    response = get_response(sort_insight_prompt)

    next_nodes, node_id = parse_response_select_insight(response, insights_info_dict, insight_list, node_id)

    print(f"next_nodes: {next_nodes}")
    print("=" * 100)

    return next_nodes, node_id


def combine_question2(query, item):
    crt_header = str(item['Header'])

    question2 = "Question: " + query + "\n"
    question2 += "Current Subspace: " + str(crt_header) + "\n"
    question2 += "Insight: \n"

    question2 += "Type: " + item['Type'] + "\n"
    question2 += "Score: " + str(item['Score']) + "\n"
    question2 += "Description: " + item['Description'] + "\n"
    question2 += question2_prompt

    return question2


def combine_question3(query, item):
    crt_header = str(item['Header'])

    # question contains only the related headers not insight-info
    question3 = """You already know the current data subspace and a problem that needs to be solved, and next we need to constantly \
change the data subspace to analyze the data. I will provide you with a "Related Subspaces List," \
which lists other subspaces related to the current subspace.
These subspaces are categorized into three types based on their hierarchical relationship with the current subspace: \
same-level, elaboration, and generalization. Please select a group that is most likely to solve my current problem \
as the next direction for exploration, and provide the reason."""
    question3 += "Related Subspaces List:\n"
    grouping_string = get_related_subspace(crt_header)
    question3 += grouping_string

    repeat_str = """Please note that my current subspace is: {} , and the question need to be solved is: "{}". \
Considering the subspace groups mentioned above, select one group that best matches the question, and provide the reason for your choice."""
    repeat_str = repeat_str.format(str(crt_header), query)
    question3 += repeat_str

    response_format = """Your answer should follow the format below:
Group type: {}
Group Criteria: {}
Reason: {}
Among them, Group type is used to identify the three categories of Same-level group, Elaboration group, and Generalization group, and Group Criteria is used to determine specific groups within the category.
For example:
Group type: Same-level groups
Group Criteria: Brand
Reason: The reason for choosing this group is that ...
"""
    question3 += response_format
    return question3


# test

#
# insight_list = read_vis_list_into_insights('vis_list_VegaLite.txt')
#
# insight_id = 195
# query = "I want to know why the sale of the brand PlayStation 4 (PS4) is an outlier, what caused the unusually large value of this point?"
#
# node_id = 0
# item = insight_list[insight_id]
# next_nodes = run(qa_LLM(query, item, insight_list, node_id))
# insights_info = get_insight_vega_by_header(header, insight_list)
#
# response = {
#     "code": 200,
#     "msg": "",
#     "data": {
#         "insights": insights_info
#     }
# }
# print(f"response: {response}")


# #
# # print(next_nodes)

