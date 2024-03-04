import openai
import os

proxy = {
'http': 'http://localhost:7890',
'https': 'http://localhost:7890'
}

openai.proxy = proxy

api_key = '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'
openai.api_key = api_key

# 定义问题和子空间信息
question1 = {
    "question": "I want to analyze Nintendo's sales performance in different locations.",
    "current_subspace": "('Nintendo', 'Europe', 'DEC', 2013)",
    "insight": {
        "filtered_conditions": ["Company = Nintendo", "Location = Europe", "Season = DEC"],
        "type": "dominance",
        "category": "point",
        "description": "The Sale of Nintendo 3DS (3DS) dominates among all Brands."
    },
    "table_structure": {
        "Company": ["Nintendo", "Sony", "Microsoft"],
        "Brand": ["Nintendo 3DS (3DS)", "Nintendo DS (DS)", "Nintendo Switch (NS)", "Wii (Wii)", "Wii U (WiiU)", "PlayStation 3 (PS3)", "PlayStation 4 (PS4)", "PlayStation Vita (PSV)", "Xbox 360 (X360)", "Xbox One (XOne)"],
        "Location": ["Europe", "Japan", "North America", "Other"],
        "Season": ["DEC", "JUN", "MAR", "SEP"],
        "Year": ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    }
}

# 定义其他子空间信息
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

# 使用 ChatGPT API 进行下一步的分析
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Question: " + question1["question"]},
        {"role": "user", "content": "Current subspace: " + question1["current_subspace"]},
        {"role": "system", "content": "Insight: " + str(question1["insight"])},
        {"role": "system", "content": "Table structure: " + str(question1["table_structure"])}
    ],
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0,
    timeout=1000,
)

# 输出分析结果
print("Analysis Result:")
for idx, subspace in enumerate(subspaces, 1):
    print(f"Subspace {idx}: {subspace}")

print("\nChatGPT Response:")
for message in response["choices"]:
    print(message["message"]["content"])
