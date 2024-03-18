def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    # Find differences
    diff_lines = []
    for i, (line1, line2) in enumerate(zip(lines1, lines2), start=1):
        if line1 != line2:
            diff_lines.append((i, line1, line2))

    return diff_lines

file1_path = r'E:\Github\InsightEngine\vis_list.txt'
file2_path = r'E:\Github\InsightEngine\vis_list1759.txt'
differences = compare_files(file1_path, file2_path)

if differences:
    print("Differences found:")
    for i, line1, line2 in differences:
        print(f"Line {i}:")
        print(f"   File1: {line1.strip()}")
        print(f"   File2: {line2.strip()}")
else:
    print("No differences found.")
