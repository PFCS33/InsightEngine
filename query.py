import ast

def load_subspace_list(file_path):
    with open(file_path, 'r') as f:
        return ast.literal_eval(f.read())

def query_subspace(header1, subspace_list):
    if header1 in subspace_list:
        return subspace_list[header1]['insight_list'], subspace_list[header1]['aggregated_header'], subspace_list[header1]['aggregated_insight_list']
    else:
        return None, None, None

if __name__ == "__main__":
    file_path = 'subspace_list.txt'
    subspace_list = load_subspace_list(file_path)

    # test
    header1 = "Europe-DEC"

    # Query subspace_list
    insight_list, header2, aggregated_insight_list = query_subspace(header1, subspace_list)

    if insight_list is not None:
        print(header1)
        print("Insight List: \n")
        for insight in insight_list:
            print(insight)

        print("------------------\n")
        print(f"Aggregated Header: \n")
        print(f"Aggregated Insight List: \n")
        for insight in aggregated_insight_list:
            print(insight)
    else:
        print("Header not found in subspace_list.")
