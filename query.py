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


if __name__ == "__main__":
    file_path = 'subspace_list.txt'
    subspace_list = parse_subspace_list(file_path)

    header = "('Nintendo', 'Europe', 'DEC', 2013)"
    result = query_subspace(header, subspace_list)

    if result:
        print("Header:", result['header'])
        print("Insight List:")
        for insight in result['insight_list']:
            print("  ", insight)
        print("Aggregated Header:", result['aggregated_header'])
        print("Aggregated Insight List:")
        for insight in result['aggregated_insight_list']:
            print("  ", insight)
    else:
        print("Header not found.")
