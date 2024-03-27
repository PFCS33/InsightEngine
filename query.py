import ast


def parse_subspace_list(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    subspace_list = {}
    current_header = None
    current_insight_type = None
    current_insight = []
    current_aggregated_header = None
    current_aggregated_insight_type = None
    current_aggregated_insight = []

    for line in lines:
        line = line.strip()
        if line.startswith("Number"):
            current_header = None
            current_insight_type = None
            current_insight = []
            current_aggregated_header = None
            current_aggregated_insight_type = None
            current_aggregated_insight = []
        elif line.startswith("header:"):
            current_header = line.split(":")[1].strip()
            subspace_list[current_header] = {'insight_list': [], 'aggregated_header': None,
                                             'aggregated_insight_list': []}
        elif line.startswith("insights:"):
            current_insight_type = 'insight_list'
        elif line.startswith("aggregated header:"):
            current_aggregated_header = line.split(":")[1].strip()
        elif line.startswith("aggregated insights:"):
            current_insight_type = None
            current_aggregated_insight_type = 'aggregated_insight_list'
        elif line:
            if current_insight_type:
                current_insight.append(line)
            elif current_aggregated_insight_type:
                current_aggregated_insight.append(line)

        if current_header:
            subspace_list[current_header]['insight_list'] = current_insight
        if current_aggregated_header:
            subspace_list[current_header]['aggregated_header'] = current_aggregated_header
        if current_aggregated_insight_type:
            subspace_list[current_header]['aggregated_insight_list'] = current_aggregated_insight

    return subspace_list


def query_subspace(header, subspace_list):
    if header in subspace_list:
        result = {
            'header': header,
            'insight_list': subspace_list[header]['insight_list'],
            'aggregated_header': subspace_list[header]['aggregated_header'],
            'aggregated_insight_list': subspace_list[header]['aggregated_insight_list']
        }
        return result
    else:
        return None


def get_related_headers(input_header, header_dict):
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
    return same_level_headers, elaboration_headers, generalization_headers


if __name__ == "__main__":
    file_path = 'vis_list.txt'
    subspace_list = parse_subspace_list(file_path)

    # test
    input_header_str = "('Nintendo', 'Europe', 'DEC', 2013)"
    check_header = query_subspace(input_header_str, subspace_list)
    if not check_header:
        print("Header not found.")

    with open('headers.txt', 'r') as file:
        header_dict = [eval(line.strip()) for line in file]
    input_header = ast.literal_eval(input_header_str)
    same_level_headers, elaboration_headers, generalization_headers = get_related_headers(input_header, header_dict)

    merged_headers = same_level_headers + elaboration_headers + generalization_headers

    result_headers = []
    for header in merged_headers:
        result = query_subspace(str(header), subspace_list)
        if result is not None:
            result_headers.append(result)

    if not result_headers:
        print("Related header not found.")
    else:
        cnt = 0
        for result in result_headers:
            cnt += 1
            print("Subspace", cnt, ": ", result['header'])
            print("Insight List:")
            for insight in result['insight_list']:
                print("  ", insight)
            if result['aggregated_header'] != None:
                print("Aggregated Header:", result['aggregated_header'])
                print("Aggregated Insight List:")
                for insight in result['aggregated_insight_list']:
                    print("  ", insight)
