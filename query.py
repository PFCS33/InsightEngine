from table import subspace_list


def query_subspace(subspace_list, query_header):

    # Query the subspace_list for a specific header and print its corresponding information

    if query_header in subspace_list:
        print(f"Header: {query_header}")
        header2 = subspace_list[query_header].get('header2', 'N/A')
        print(f"  Header2: {header2}")
        insight_list = subspace_list[query_header].get('insight_list', [])
        if insight_list:
            print("  Insight List:")
            for insight in insight_list:
                print(f"    - {insight}")
        aggregated_insight_list = subspace_list[query_header].get('aggregated_insight_list', [])
        if aggregated_insight_list:
            print("  Aggregated Insight List:")
            for insight in aggregated_insight_list:
                print(f"    - {insight}")
    else:
        print("Header not found.")


# Example usage
if __name__ == "__main__":
    query_header = "('DEC', 2015)"
    query_subspace(subspace_list, query_header)
