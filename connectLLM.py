import openai
import os
import config

proxy = {
'http': 'http://localhost:7890',
'https': 'http://localhost:7890'
}

openai.proxy = proxy

# gpt4.0 key

openai.api_key = config.api_key

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

question2 = """
Question: I want to analyze Nintendo's sales performance in different locations.

Current subspace: ('Nintendo', 'Europe', 'DEC', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe, Season = DEC]
In the filtered subspace, the insight is: 
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Table structure: {
'Company': ['Nintendo', 'Sony', 'Microsoft'], 
'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)', 'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)', 'Xbox 360 (X360)', 'Xbox One (XOne)'], 
'Location': ['Europe', 'Japan', 'North America', 'Other'], 
'Season': ['DEC', 'JUN', 'MAR', 'SEP'], 
'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']}

Do you understand the questions I want to explore and the current exploration status? Next, I will provide you with some other subspaces related to the current exploration. Based on my question, analyze the information presented in the following subspaces. Choose three subspaces that are most relevant to the question as the next exploration directions.
"""


question3 = """
Subspace 1 :  ('Nintendo', 'Europe', 'DEC', 2017)
Insight:
{Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe, Season = DEC]
In the filtered subspace, the insight is:
Type: top2
Category: point
Description: The Sale proportion of Nintendo 3DS (3DS) and Nintendo Switch (NS) is significantly higher than that of other Brands.)
}

Subspace 2 :  ('Nintendo', 'Europe', 'JUN', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe, Season = JUN]
In the filtered subspace, the insight is:
Type: top2
Category: point
Description: The Sale proportion of Nintendo 3DS (3DS) and Wii (Wii) is significantly higher than that of other Brands.)
}

Subspace 3 :  ('Nintendo', 'Europe', 'MAR', 2013)
Insight: 
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe, Season = MAR]
In the filtered subspace, the insight is:
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Subspace 4 :  ('Nintendo', 'Europe', 'SEP', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe, Season = SEP]
In the filtered subspace, the insight is:
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Subspace 5 :  ('Nintendo', 'Japan', 'DEC', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Japan, Season = DEC]
In the filtered subspace, the insight is:
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Subspace 6 :  ('Nintendo', 'North America', 'DEC', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = North America, Season = DEC]
In the filtered subspace, the insight is:
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Subspace 7 :  ('Nintendo', 'Wii (Wii)', 'DEC', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Brand = Wii (Wii), Season = DEC]
In the filtered subspace, the insight is:
Type: top2
Category: point
Description: The Sale proportion of Europe and North America is significantly higher than that of other Locations.)
}

Subspace 8 :  ('Nintendo', 'Europe', 'DEC')
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe, Season = DEC]
In the filtered subspace, the insight is:
Type: top2
Category: point
Description: The Sale proportion of Nintendo Switch (NS) and Nintendo 3DS (3DS) is significantly higher than that of other Brands.)
}

Subspace 9 :  ('Nintendo', 'Europe', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Location = Europe]
In the filtered subspace, the insight is:
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Subspace 10 :  ('Nintendo', 'DEC', 2013)
Insight:
{
Filtered the original data table with the conditions: [Company = Nintendo, Season = DEC]
In the filtered subspace, the insight is:
Type: dominance
Category: point
Description: The Sale of Nintendo 3DS (3DS) dominates among all Brands.)
}

Subspace 11 :  ('Europe', 'DEC', 2013)
Insight:
{
Context: Filtered the original data table with the conditions: [Location = Europe, Season = DEC]
In the filtered subspace, the insight is:
Type: top2
Category: point
Description: The Sale proportion of Nintendo and Sony is significantly higher than that of other Companys.)
}

Now based on my question: "I want to analyze Nintendo's sales performance in different locations.”, analyze the information presented in the insights of the above subspaces. Choose three subspaces that are most relevant to the question as the next exploration directions. Please reply to me with the selected subspace numbers and their names in the recommended order, for example, 'Subspace 8: ('Nintendo', 'Europe', 'DEC'),' and explain the reasons for your selection.
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

questions = []
questions.append(question1)
questions.append(question2)
questions.append(question3)

# 多轮问答
with open('qa_log.txt', 'a') as f:
    for question in questions:
        messages = [
            {"role": "system", "content": "You are a tabular data analysis expert."},
            {"role": "user", "content": question},
        ]
        response = get_completion_from_messages(messages, temperature=0)

        print('-'*30)
        print(f"Q: {question1}\n"
                f"A: {response}\n\n")


        f.write(f"{'-'*30}\n"
                f"Q: {question1}\n"
                f"A: {response}\n\n")

print("Conversation ended.")