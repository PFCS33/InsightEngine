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
The data analysis process is divided into two iterative steps. The first step is to select a data sub-area to be explored (this step is selected by LLM), and the second step is to calculate the existing insights in this sub-area (this step is done by an external actuator).
I will first provide you with the question I want to explore in the data table, the current exploration status, and the data table structure. I will present this information to you in the following format, where the information after the # sign can help you understand the meaning of each item:
"
Question: {} # A problem I want to analyze in the data table.
Current subspace: () # Current exploration status
Insight: # The insight in the current subspace
{
Filter condition: [] # Explains how to filter the original data table to obtain this subspace
Type: {} # Insight type
Category: {} # Insight category
Description:{} # Insight description
}
Table structure: {} # The structure of the original data table, including column names and the attribute list for each column, with the last column representing sales value (not listed)
"
"""


subspaces = [
    "('Nintendo', 'Europe', 'DEC', 2017)",
    "('Nintendo', 'Europe', 'JUN', 2013)",
    "('Nintendo', 'Europe', 'MAR', 2013)",
    "('Nintendo', 'Europe', 'SEP', 2013)",
    "('Nintendo', 'Japan', 'DEC', 2013)",
    "('Nintendo', 'North America', 'DEC', 2013)",
    "('Nintendo', 'Wii (Wii)', 'DEC', 2013)",
    "('Nintendo', 'Europe', 'DEC')",
    "('Nintendo', 'Europe', 2013)",
    "('Nintendo', 'DEC', 2013)",
    "('Europe', 'DEC', 2013)"
]


question2_prompt = """
Table structure: {
'Company': ['Nintendo', 'Sony', 'Microsoft'], 
'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)', 'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)', 'Xbox 360 (X360)', 'Xbox One (XOne)'], 
'Location': ['Europe', 'Japan', 'North America', 'Other'], 
'Season': ['DEC', 'JUN', 'MAR', 'SEP'], 
'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']}

Do you understand the questions I want to explore and the current exploration status? Next, I will provide you with some other subspaces related to the current exploration. Based on my question, analyze the information presented in the following subspaces. Choose three subspaces that are most relevant to the question as the next exploration directions.
"""

question3_prompt = """
Based on the question and current subspace, I need you to suggest five possible next steps for exploration and explain the reasons for each. Predict the information that may be explored.
You need to reply to me in the following form
subspace: ""
reason: ""
"""

def read_vis_list(file_path):
    insight_list = []
    with open(file_path, 'r') as file:
        header = None
        insight = {}
        for line in file:
            line = line.strip()
            if line.startswith("Header:"):
                if header is not None:
                    insight_list.append({'header': header, 'insights': insight})
                header = tuple(line.split(": ")[1].strip("()").split(", "))
                insight = {}
            elif line.startswith("Insight"):
                insight_type = line.split(": ")[1]
            elif line.startswith("Type:"):
                insight['type'] = line.split(": ")[1]
            elif line.startswith("Score:"):
                insight['score'] = float(line.split(": ")[1])
            elif line.startswith("Description:"):
                insight['description'] = line.split(": ")[1]
        if header is not None:
            insight_list.append({'header': header, 'insights': insight})
    return insight_list


def get_completion_from_messages(messages, temperature=0):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=temperature,
        timeout=1000,
    )
    # print(str(response.choices[0].message))
    return response.choices[0].message["content"]


def get_insights_for_header(header, insight_list):
    for item in insight_list:
        if item['header'] == header:
            insights_info = []
            for i, insight in enumerate(item['insights'].values(), start=1):
                insight_info = {
                    'Insight': f"Insight {i}",
                    'Type': insight['type'],
                    'Score': insight['score'],
                    'Description': insight['description']
                }
                insights_info.append(insight_info)
            return insights_info
    return None


def combine_question2(query, crt_header):
    insights_info = get_insights_for_header(crt_header, insight_list)
    if insights_info:
        question2 = "Queation: " + query + "\n"
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


def get_related_subspace(input_header, header_dict):
    same_level_headers = []
    elaboration_headers = []
    generalization_headers = []
    for header in header_dict:
        if len(header) == len(input_header) and sum([1 for i, j in zip(header, input_header) if i == j]) == len(
                input_header) - 1:
            same_level_headers.append(header)
        if len(header) == len(input_header) - 1 and all(item in input_header for item in header):
            elaboration_headers.append(header)
        if len(header) == len(input_header) + 1 and all(item in header for item in input_header):
            generalization_headers.append(header)
    related_headers_list = [same_level_headers, elaboration_headers, generalization_headers]
    return related_headers_list


def combine_question3(crt_header, insight_list):
    # question contains only the related headers not insight-info
    related_headers_list = get_related_subspace(crt_header, header_dict)
    question3 = "Related Headers List:\n"
    for i, headers in enumerate(related_headers_list, start=1):
        # if i == 1:
        #     question3 += "Same Level Headers:\n"
        # elif i == 2:
        #     question3 += "Elaboration Headers:\n"
        # elif i == 3:
        #     question3 += "Generalization Headers:\n"
        for header in headers:
            question3 += str(header) + "\n"
    return question3




def get_response(question):
    messages = [
        {"role": "system", "content": "You are a tabular data analysis expert."},
        {"role": "user", "content": question},
    ]
    response = get_completion_from_messages(messages, temperature=0)
    return response


def parse_response(response):
    response_list = []
    subspace_reason_info = {}
    for line in response.split("\n"):
        line = line.strip()
        if line.startswith("subspace:"):
            if subspace_reason_info:
                response_list.append(subspace_reason_info)
            subspace_reason_info = {"subspace": line.split(":")[1].strip()}
        elif line.startswith("reason:"):
            subspace_reason_info["reason"] = line.split(":")[1].strip()
    if subspace_reason_info:
        response_list.append(subspace_reason_info)
    return response_list


def qa_process():
    signal_received = False
    iteration = 0

    query = "I want to know the sales information of Nintendo 3DS in different years."
    crt_header = "('Nintendo', 'Nintendo 3DS (3DS)')"

    with open('qa_log.txt', 'w') as f:
        response = get_response(question1)
        f.write(f"Q: {question1}\nA: {response}\n")

        # while not signal_received:
        for _ in range(2):
            iteration += 1
            question2 = combine_question2(query, crt_header)
            question3 = combine_question3(crt_header, insight_list)
            response = get_response(question2 + question3)
            f.write(f"Q: {question2 + question3}\nA: {response}\n")

            # abstract structured info from response
            response_list = parse_response(response)

            # if check_for_signal():
            #     signal_received = True

    print("Conversation ended.")


if __name__ == "__main__":
    # read in vis_list
    file_path = 'vis_list.txt'
    insight_list = read_vis_list(file_path)

    # read in header for search (external part of ReAct)
    with open('headers.txt', 'r') as file:
        header_dict = [eval(line.strip()) for line in file]

    # iterative q&a
    qa_process()