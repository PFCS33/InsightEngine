import openai
import ast
import os
import config_api

proxy = {
    'http': 'http://localhost:7890',
    'https': 'http://localhost:7890'
}

openai.proxy = proxy

# gpt4.0 key

openai.api_key = config_api.api_key

question1 = """
You are assisting me in exploring a dataset to analyze patterns and extract insights. Data exploration involves filtering data to extract subspaces and analyzing these subspaces to identify important patterns, known as insights.
There are eight types of insights, divided into two categories: point insights and shape insights. Point insights include dominance, top2, outlier, and outlier-temporal, while shape insights include trend, kurtosis, skewness, and evenness.
The data analysis process is divided into two iterative steps. The first step is to select a data subspace to be explored (this step is selected by LLM), and the second step is to calculate the existing insights in this subspace (this step is done by an external actuator).

I will provide you with the structure of the original data table, including column names and the attribute list for \
each column, with the last column representing sales value (not listed), which can help you better understand the table content.
Table structure: {
'Company': ['Nintendo', 'Sony', 'Microsoft'],
'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)', \
'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)', 'Xbox 360 (X360)', 'Xbox One (XOne)'],
'Location': ['Europe', 'Japan', 'North America', 'Other'],
'Season': ['DEC', 'JUN', 'MAR', 'SEP'],
'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']}

Next, please assist me in conducting data exploration. In each round, I will provide you with the questions I want to explore, \
the current data subspace under exploration, and the insights within this subspace. \
Please utilize your knowledge to guide me in conducting deep exploration to find data story. Do you understand your task?
"""

# """
# I will first provide you with the question I want to explore in the data table, the current exploration status, and the data table structure. I will present this information to you in the following format, where the information after the # sign can help you understand the meaning of each item:
# "
# Question: {} # A problem I want to analyze in the data table.
# Current subspace: () # Current exploration status
# Insight: # The insight in the current subspace
# {
# Filter condition: [] # Explains how to filter the original data table to obtain this subspace
# Type: {} # Insight type
# Score: {} # The range of insight score is [0, 1], where a higher score indicates a more significant insight.
# Category: {} # Insight category
# Description:{} # Insight description
# }
# """


question2_prompt = """
Next, I will provide you with some other subspaces related to the current subspace in terms of header structure. 
"""

question3_prompt = """
Your task is to organize and select subspaces which related to the current data subspace to analyze the data \
from different perspectives and approach the answer to the question.

You already know the current data subspace and a problem that needs to be solved, and next we need to constantly \
change the data subspace to analyze the data. I will provide you with a "Related Subspaces List," \
which lists other subspaces related to the current subspace. 
However, not every related subspace is helpful for answering the current question. Some subspaces may need to be \
combined to provide key information. Therefore, you need to identify some groups of subspaces, \
each consisting of multiple subspaces, which are grouped according to certain criteria. 
These criteria can be semantics, relation to the current subspace, and relevance to the question. \
Each group will be analyzed from a different perspective to approach finding the answer to the question. \
It should be noted that a subspace can belong to no group (not helpful for solving the problem) or \
belong to multiple groups (key data subspaces).

After categorizing them, please rank the groups in order of how closely they match the query so that \
the first group is the answer that best matches the question., your answer must follow the format below: 
Results after grouping and sorting: 
Group1: {Subspaces belonging to Group1, divided by ", ", no line breaks}
Group2: {Subspaces belonging to Group2, divided by ", ", no line breaks}
... 
Please note that the braces "{}" cannot be omitted. For example, "Group1: {('Nintendo', 'Europe'), ('Nintendo', 'Japan'), ('Nintendo', 'North America'), ('Nintendo', 'Other')}".
"""
# for example,
# Results after grouping and sorting:
# Group1: {('Nintendo', 'Europe'), ('Nintendo', 'Japan'), ('Nintendo', 'North America'), ('Nintendo', 'Other')}

get_query_prompt = """
I have identified a main question that needs to be addressed: "{}". The current subspace of exploration is {}. \
Next, I will select a data subspace {} for future exploration. In this future subspace, please help me find \
a specific and targeted small question that can assist in addressing the main question. 
This small question should focus on a specific aspect or particular data points within the future subspace, \
rather than being computational in nature (e.g., "total", "sum", etc.). 
The purpose of proposing a small question is to gradually explore the data and ultimately find the key to solving \
the main question. So please reconsider the main question, the current subspace, and the future subspace, \
and finally propose a specific and targeted small question. 
Please follow the response format below: 
Question: {}
"""

global insight_list
global header_dict


def read_vis_list(file_path):
    global insight_list
    insight_list = []

    with open('vis_list.txt', 'r') as file:
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
                        insight_description = lines[i + 3].split(":")[1].strip()
                        insights.append(
                            {"Type": insight_type, "Score": insight_score, "Description": insight_description})
                        i += 4
                    else:
                        i += 1
                insight_list.append({"Header": header, "Insights": insights})
            else:
                i += 1
    return insight_list


def get_completion_from_messages(messages, temperature):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        # model="gpt-3.5-turbo-0613",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=temperature,
        timeout=1000,
    )
    # print(str(response.choices[0].message))
    return response.choices[0].message["content"]


def get_insights_for_header(header_str, insight_list):
    header = eval(header_str)
    # sort for matching
    header = tuple(sorted(map(str, header)))
    for item in insight_list:
        if item['Header'] == header:
            insights_info = []
            for i, insight in enumerate(item['Insights'], start=1):
                insight_info = {
                    'Insight': f"Insight {i}",
                    'Type': insight['Type'],
                    'Score': insight['Score'],
                    'Description': insight['Description']
                }
                insights_info.append(insight_info)
            return insights_info
    return None


def combine_question2(query, crt_header, insights_info):
    if insights_info:
        question2 = "Question: " + query + "\n"
        question2 += "Current Subspace: " + str(crt_header) + "\n"
        for info in insights_info:
            question2 += info['Insight'] + ":\n"
            question2 += "Type: " + info['Type'] + "\n"
            question2 += "Score: " + str(info['Score']) + "\n"
            question2 += "Description: " + info['Description'] + "\n"
        question2 += question2_prompt
    else:
        question2 = "Invalid Current Subspace."

    return question2


table_structure = {
    'Company': ['Nintendo', 'Sony', 'Microsoft'],
    'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)',
              'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)', 'Xbox 360 (X360)',
              'Xbox One (XOne)'],
    'Location': ['Europe', 'Japan', 'North America', 'Other'],
    'Season': ['DEC', 'JUN', 'MAR', 'SEP'],
    'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
}


def group_same_level_headers(input_header, same_level_headers, attribute_to_column):
    # Group same_level_headers based on attribute value
    groups = {}
    for header in same_level_headers:
        # Find which element is different from input_header
        diff_index = -1
        for i, (input_item, item) in enumerate(zip(input_header, header)):
            if input_item != item:
                diff_index = i
                break

        # Determine grouping criteria
        if diff_index != -1:
            group_criteria = attribute_to_column.get(header[diff_index])
        else:
            group_criteria = "False"

        # Add header to the corresponding group
        if (group_criteria,) in groups:
            groups[(group_criteria,)]["headers"].append(header)
        else:
            groups[(group_criteria,)] = {"headers": [header], "template_sentence":
                f"This group of subspaces replaces the attribute values of the '{group_criteria}' column in the current subspace."}

    return groups


def group_elaboration_headers(input_header, elaboration_headers, attribute_to_column):
    # Grouping based on the additional element's column
    groups = {}
    for header in elaboration_headers:
        # Find the additional element in header that is not in input_header
        additional_element = set(header) - set(input_header)
        if len(additional_element) == 1:
            additional_element = additional_element.pop()
            group_key = attribute_to_column.get(additional_element, "False")

            # Add header to the corresponding group
            if group_key in groups:
                groups[group_key]["headers"].append(header)
            else:
                groups[group_key] = {"headers": [header], "template_sentence":
                    f"This group is a subdivision of the current subspace in the '{group_key}' column dimension."}

    return groups


def get_related_subspace(input_header_str, header_dict):
    # transform to tuple
    input_header = ast.literal_eval(input_header_str)
    same_level_headers = []
    elaboration_headers = []  # find child
    generalization_headers = []  # find parent

    # Create a mapping from attribute value to column name
    attribute_to_column = {}
    for column, attributes in table_structure.items():
        for attribute in attributes:
            attribute_to_column[attribute] = column

    for header in header_dict:
        if len(header) == len(input_header) and sum([1 for i, j in zip(header, input_header) if i == j]) == len(
                input_header) - 1:
            # Find the index of the differing element
            diff_index = [i for i, (x, y) in enumerate(zip(header, input_header)) if x != y][0]

            column_input_header = attribute_to_column[input_header[diff_index]]
            column_header = attribute_to_column[header[diff_index]]

            if column_input_header == column_header:
                same_level_headers.append(header)
        if len(header) == len(input_header) + 1 and all(item in header for item in input_header):
            elaboration_headers.append(header)
        if len(header) == len(input_header) - 1 and all(item in input_header for item in header):
            generalization_headers.append(header)

    output_string = ""

    # Group same_level_headers
    same_level_groups = group_same_level_headers(input_header, same_level_headers, attribute_to_column)
    same_level_explanation = "\nThe following are groups of same-level headers, which have the same level of subdivision as the current data subspace. Each group consists of headers that are identical to the current data subspace in all elements except one, which represents a different attribute of the data subspace in a particular column."
    output_string += same_level_explanation + "\n"
    output_string += "Same-level groups:\n"
    for (group_criteria,), group_info in same_level_groups.items():
        output_string += f"Group Criteria: {group_criteria}\n"
        output_string += f"Explanation: {group_info['template_sentence']}\n"
        output_string += "Headers:\n"
        for header in group_info["headers"]:
            output_string += str(header) + "\n"
        output_string += "\n"

    # Group generalization_headers
    generalization_groups = generalization_headers
    generalization_explanation = "\nThe following is the group of generalization headers, which represent the parent or immediate higher-level region of the current data subspace. These headers can be used to expand the context of the current data subspace or provide more general background information."
    output_string += generalization_explanation + "\n"
    output_string += "Generalization group:\n"
    output_string += "Group Criteria: parent headers of current header\n"
    output_string += "Headers:\n"
    for header in generalization_groups:
        output_string += str(header) + "\n"

    # Group elaboration_headers
    elaboration_groups = group_elaboration_headers(input_header, elaboration_headers, attribute_to_column)
    elaboration_explanation = "\nThe following are groups of elaboration headers, which represent the next level of detail beneath the current data subspace. These headers provide specific details about certain aspects of the current data subspace, helping to drill down into a specific aspect of the data."
    output_string += elaboration_explanation + "\n"
    output_string += "Elaboration groups:\n"
    for group_key, group_info in elaboration_groups.items():
        output_string += f"Group Criteria: {group_key}\n"
        output_string += f"Explanation: {group_info['template_sentence']}\n"
        output_string += "Headers:\n"
        for header in group_info["headers"]:
            output_string += str(header) + "\n"
        output_string += "\n"

    # related_headers_list = [same_level_headers, elaboration_headers, generalization_headers]
    # return related_headers_list

    return output_string

def combine_question3(crt_header, query):
    # question contains only the related headers not insight-info
    question3 = """You already know the current data subspace and a problem that needs to be solved, and next we need to constantly \
change the data subspace to analyze the data. I will provide you with a "Related Subspaces List," \
which lists other subspaces related to the current subspace.
These subspaces are categorized into three types based on their hierarchical relationship with the current subspace: \
same-level, elaboration, and generalization. Please select a group that is most likely to solve my current problem \
as the next direction for exploration, and provide the reason."""
    question3 += "Related Subspaces List:\n"
    grouping_string = get_related_subspace(crt_header, header_dict)
    # for i, headers in enumerate(related_headers_list, start=1):
    #     # if i == 1:
    #     #     question3 += "Same Level Headers:\n"
    #     # elif i == 2:
    #     #     question3 += "Elaboration Headers:\n"
    #     # elif i == 3:
    #     #     question3 += "Generalization Headers:\n"
    #     for header in headers:
    #         question3 += str(header) + "\n"
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
Reason: The reason for choosing this group is that the question is specifically about the brand PlayStation 4 (PS4). By comparing the sales of PS4 with other brands in the same month ('JUN') and location ('Europe'), we can better understand what makes PS4 an outlier. For example, if PS4 has significantly higher sales than other brands, it could be due to factors like more popular games, better marketing, or superior hardware.
"""
    question3 += response_format
    return question3


def get_response(question):
    messages = [
        {"role": "system", "content": "You are a tabular data analysis expert."},
        {"role": "user", "content": question},
    ]
    response = get_completion_from_messages(messages, temperature=0)
    return response


def get_query(question):
    messages = [
        {"role": "system", "content": "You are a tabular data analysis expert."},
        {"role": "user", "content": question},
    ]
    response = get_completion_from_messages(messages, temperature=0)
    return response


def parse_response_subspace(response):
    response_list = []
    subspace_reason_info = {}
    for line in response.split("\n"):
        line = line.strip()
        if line.startswith("Subspace"):
            if subspace_reason_info:
                response_list.append(subspace_reason_info)
            subspace_reason_info = {"subspace": line.split(":")[1].strip().strip('"')}
        elif line.startswith("Reason"):
            subspace_reason_info["reason"] = line.split(":")[1].strip().strip('"')
        elif line.startswith("Query"):
            subspace_reason_info["query"] = line.split(":")[1].strip().strip('"')
    if subspace_reason_info:
        response_list.append(subspace_reason_info)
    return response_list


def parse_response_group(response):
    response_list = {}
    start_parsing = False
    group_texts = response.splitlines()
    for line in group_texts:
        if start_parsing and not line.startswith("Group"):
            break
        if line.startswith("Group"):
            start_parsing = True
            group_info = line.split(": ")
            group_name = group_info[0]
            subspace_str = group_info[1].strip("{}")
            subspace_list = [tuple(elem.strip("'") for elem in subspace.strip("()").split(", ")) for subspace in
                             subspace_str.split("), (")]
            response_list[group_name] = subspace_list
    return response_list


def from_header_get_query(main_query, crt_header, next_header):
    query_prompt = get_query_prompt.format(main_query, crt_header, next_header, '')
    response = get_query(query_prompt)

    # parse_response_query
    next_query = None  # LLM response format error later in qa_process()
    text = response.splitlines()
    for line in text:
        if line.startswith("Question: "):
            next_query = line.split(":")[1].strip()
            break
    return next_query


def qa_process():
    file_path = 'qa_log_group_back_end.txt'
    query = "I want to analyze the Sales among"
    crt_header = "('Nintendo 3DS (3DS)', 'MAR', '2014')"
    main_query = query

    with open(file_path, 'w') as f:
        response = get_response(question1)
        f.write('=' * 100)
        f.write("\n")
        f.write(f"Q: {question1}\nA: {response}\n")

    iteration = 0
    while iteration < 3:
        iteration += 1
        insights_info = get_insights_for_header(crt_header, insight_list)
        question2 = combine_question2(query, crt_header, insights_info)
        if question2 != "Invalid Current Subspace.":
            question3 = combine_question3(crt_header, query)
            response = get_response(question2 + question3)
        else:
            print("Invalid Current Subspace. Ending conversation.")
            break

        with open(file_path, 'a') as f:
            f.write('=' * 100)
            f.write("\n")
            f.write(f"Q: {question2 + question3}\nA: {response}\n")
        print(f"Conversation {iteration} ended.")

        question4 = """You have selected a group of headers that best match the question: 
Group Criteria: Brand
Explanation: This group is a subdivision of the current subspace in the 'Brand' column dimension.
Headers:
('Nintendo 3DS (3DS)', 'Europe', 'JUN')
('Nintendo DS (DS)', 'Europe', 'JUN')
('Nintendo Switch (NS)', 'Europe', 'JUN')
('Wii (Wii)', 'Europe', 'JUN')
('Wii U (WiiU)', 'Europe', 'JUN')
('PlayStation 3 (PS3)', 'Europe', 'JUN')
('PlayStation 4 (PS4)', 'Europe', 'JUN')
('PlayStation Vita (PSV)', 'Europe', 'JUN')
('Xbox 360 (X360)', 'Europe', 'JUN')
('Xbox One (XOne)', 'Europe', 'JUN')
         
        Next, you need to sort the headers within the group. \
        Considering the current subspace: "('Europe', 'JUN')", and the question: "I want to know why the sale of the brand PlayStation 4 (PS4) is an outlier, what caused the unusually large value of this point? ", which header is most likely to contain key information for answering the question? \
        Please sort the headers within the group in order of importance, from highest to lowest."""
        response = get_response(question4)

        with open(file_path, 'a') as f:
            f.write('=' * 100)
            f.write("\n")
            f.write(f"Q: {question4}\nA: {response}\n")

        # parse structured info from response
        response_list = parse_response_group(response)

        found_valid_subspace = False
        for group, subspaces in response_list.items():
            if found_valid_subspace:
                break
            for subspace in subspaces:
                next_header = str(subspace)
                insights_info = get_insights_for_header(next_header, insight_list)
                if insights_info:
                    found_valid_subspace = True
                    break
        next_query = from_header_get_query(main_query, crt_header, next_header)
        crt_header = next_header
        query = next_query
        if crt_header is None or query is None:
            print("No valid subspace or query found. Ending conversation.")
            break

        # response_list = parse_response_subspace(response)
        # choose the 1st answer as default to start next qa process
        # next_header = None
        # next_query = None
        # for i in range(len(response_list)):
        #     next_header = response_list[i].get("subspace")
        #     next_query = response_list[i].get("query")
        #     if combine_question2(next_query, next_header) != "Invalid Current Subspace.":
        #         break
        #
        # crt_header = next_header
        # query = next_query
        # if crt_header is None or query is None:
        #     print("No valid question found. Ending conversation.")
        #     break

    print("Conversation closed.")


if __name__ == "__main__":
    # read in vis_list
    file_path = 'vis_list.txt'
    insight_list = read_vis_list(file_path)

    # read in header for search (external part of ReAct)
    with open('headers.txt', 'r') as file:
        header_dict = [tuple(str(item) if isinstance(item, int) else item for item in eval(line.strip())) for line in
                       file]

    # iterative q&a
    qa_process()
