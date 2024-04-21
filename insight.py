import numpy as np
import pandas as pd
import heapq
import copy
from insightCalculator import check_is_temporal, calc_outlier, calc_outlier_temporal, calc_point_insight, \
    calc_shape_insight, calc_compound_insight, calc_distribution_insight

month2letter = {'JAN': 'a', 'FEB': 'b', 'MAR': 'c', 'APR': 'd', 'MAY': 'e',
                'JUN': 'f', 'JUL': 'g', 'AUG': 'h', 'SEP': 'i', 'OCT': 'j', 'NOV': 'k', 'DEC': 'l'}
letter2month = {'a': 'JAN', 'b': 'FEB', 'c': 'MAR', 'd': 'APR', 'e': 'MAY',
                'f': 'JUN', 'g': 'JUL', 'h': 'AUG', 'i': 'SEP', 'j': 'OCT', 'k': 'NOV', 'l': 'DEC'}

table_structure = {
    'Company': ['Nintendo', 'Sony', 'Microsoft'],
    'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)',
              'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)',
              'Xbox 360 (X360)', 'Xbox One (XOne)'],
    'Location': ['Europe', 'Japan', 'North America', 'Other'],
    'Season': ['DEC', 'JUN', 'MAR', 'SEP'],
    'Year': ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
}

subspace_insight = {}

class Insight:
    def __init__(self, scope_data, breakdown=None, aggregate=None):
        self.scope_data = scope_data
        self.breakdown = breakdown  # the column index of the breakdown in block_data
        self.aggregate = aggregate  # the aggregate function to generate scope data

        self.type = None
        self.score = None
        self.category = None
        # self.table_structure = table_structure
        self.context = None  # header description, which is the filter condition of subspace
        self.description = None

    def __lt__(self, other):
        return self.score < other.score

    def __str__(self) -> str:
        return f"\nType: {self.type}\nScore: {self.score}\nCategory: {self.category}\nDescription: {self.description}\n"

    def __repr__(self):
        return f"\nType: {self.type}\nScore: {self.score}\nCategory: {self.category}\nDescription: {self.description}\n"


def get_insight(header, block_data):
    aggregate = 'sum'
    global block_insight  # record the insights for the current block # group by insight type
    global subspace_insight
    # contains three types of insight
    block_insight = {'point': [], 'shape': [], 'compound': []}

    # change categorical to string
    for col in block_data.columns:
        if pd.api.types.is_categorical_dtype(block_data[col]):
            block_data[col] = block_data[col].astype(str)

    # no breakdown, consider all data together
    get_scope_no_breakdown(header, block_data)

    # aggregate by every column
    for i in range(len(block_data.columns) - 1):
        get_scope_with_aggregate(header, block_data, i, aggregate)  # i is the breakdown index

    get_scope_for_compound(header, block_data)
    # consider all layers and generate groups, no aggregate, compound insights
    # get_scope_rearrange(header, block_data)

    return block_insight, subspace_insight


def merge_columns(block_data, start, end, name='Merged'):
    data = copy.deepcopy(block_data)
    merged_col = data.iloc[:, start:end].apply(
        lambda x: ' - '.join(x.astype(str)), axis=1)
    merged_col.name = name
    res = pd.concat([data.iloc[:, :start], merged_col,
                     data.iloc[:, end:]], axis=1)

    return res


def get_scope_no_breakdown(header, block_data):
    # scope_data = None
    # # merge the first [merge_num] columns as the breakdown column
    # merge_num = block_data.shape[1] - 1
    # scope_data = merge_columns(block_data, 0, merge_num)
    # # merged_column = block_data.iloc[:, :merge_num].apply(lambda x: ' - '.join(x.astype(str)), axis=1)
    # # scope_data = pd.concat([merged_column, block_data.iloc[:, merge_num]], axis=1)
    #
    # # set the breakdown column as index
    # scope_data = scope_data.set_index(scope_data.columns[0])
    # # turn the dataframe to series
    # scope_data = scope_data[scope_data.columns[0]]

    scope_data = copy.deepcopy(block_data)
    # check if main column has only one entity
    abstract_header = ""
    if len(set(scope_data.iloc[:, 0])) == 1 and len(scope_data.columns) > 2:
        while len(set(scope_data.iloc[:, 0])) == 1 and len(scope_data.columns) > 2:
            abstract_header += scope_data.iloc[0, 0] + ","
            scope_data = scope_data.drop(columns=scope_data.columns[0])
        abstract_header = abstract_header[:-1]
        abstract_header_tuple = (abstract_header,)
        aggregated_header = header + abstract_header_tuple
    else:
        aggregated_header = header

    is_month = False
    if (scope_data.iloc[:, 0] == 'MAR').any(): # Check if 'MAR' is in the first column
        # record the origin order
        scope_data.iloc[:, 0] = scope_data.iloc[:, 0].replace(month2letter, regex=True)
        # sort the data by origin order
        scope_data = scope_data.sort_values(by=scope_data.columns[0])
        # change back to the origin name
        scope_data.iloc[:, 0] = scope_data.iloc[:, 0].replace(letter2month, regex=True)
        is_month = True

    scope_data = scope_data.reset_index(drop=True)

    numeric_columns = scope_data.select_dtypes(include='number').columns
    scope_data[numeric_columns] = scope_data[numeric_columns].apply(lambda x: round(x, 2))

    calc_insight(aggregated_header, scope_data, None, None, True, is_month=is_month)


def get_scope_with_aggregate(header, block_data, breakdown, aggregate):
    scope_data = copy.deepcopy(block_data)

    # make the breakdown_column be the main col
    breakdown_col = scope_data.columns[breakdown]
    scope_data.insert(0, breakdown_col, scope_data.pop(breakdown_col))

    # check if main column has only one entity
    abstract_header = ""
    if len(set(scope_data.iloc[:, 0])) == 1 and len(scope_data.columns) > 2:
        while len(set(scope_data.iloc[:, 0])) == 1 and len(scope_data.columns) > 2:
            abstract_header += scope_data.iloc[0, 0] + ","
            scope_data = scope_data.drop(columns=scope_data.columns[0])
        abstract_header = abstract_header[:-1]
        abstract_header_tuple = (abstract_header,)
        aggregated_header = header + abstract_header_tuple
    else:
        aggregated_header = header

    # merge the main col
    scope_data = scope_data.groupby(scope_data.columns[0]).agg('sum')

    # -----process duplicated content in cell-----
    columns_to_update = scope_data.columns[0:-1]

    def replace_value(cell_value, column_name):
        return 'all ' + column_name + 's'

    for column in columns_to_update:
        scope_data[column] = scope_data[column].apply(lambda x: replace_value(x, column))

    # avoid duplication
    # scope_data = scope_data.applymap(lambda x: ', '.join(sorted(set(x.split(',')))) if isinstance(x, str) else x)
    # print(scope_data)


    is_month = False
    if scope_data.index.__contains__('MAR'):  # trick to sort months
        # record the origin order
        scope_data.index = scope_data.index.to_series().replace(month2letter, regex=True)
        # sort the data by origin order
        scope_data = scope_data.sort_index()
        # change back to the origin name
        scope_data.index = scope_data.index.to_series().replace(letter2month, regex=True)
        is_month = True

    scope_data = scope_data.reset_index()

    numeric_columns = scope_data.select_dtypes(include='number').columns
    scope_data[numeric_columns] = scope_data[numeric_columns].apply(lambda x: round(x, 2))

    calc_insight(aggregated_header, scope_data, breakdown, aggregate, is_month=is_month)


def get_scope_for_compound(header, block_data):
    """
    枚举列表头中所有能作为x轴，z轴的表头对（x，z）
    对每一个表头对（x，z），把x和z对应的data从header的date中提取出来
    计算任意两组z属性（zi，zj）间的相关性
    如果具有相关性（score > 0.7），就把（x，（zi，zj））加入到该header的compound insight里

    """
    pass


def get_scope_rearrange_old(header, block_data, header_split):
    scope_data = copy.deepcopy(block_data)
    # concat row and column headers to one level if needed
    if block_data.shape[1] - 1 - header_split > 1:
        scope_data = merge_columns(
            scope_data, header_split, block_data.shape[1] - 1, 'Merged_col')
    if header_split > 1:
        scope_data = merge_columns(scope_data, 0, header_split, 'Merged_idx')

    # group by columns
    scope_data.set_index(scope_data.columns[0], inplace=True)
    scope_data = scope_data.pivot(
        columns=scope_data.columns[0], values=scope_data.columns[-1])
    get_scope_rearrange_more(scope_data)

    # group by rows
    scope_data = scope_data.T
    if check_is_temporal(scope_data):
        # for temporal data, record the origin order
        scope_data.index = scope_data.index.to_series().replace(month2letter, regex=True)
        # sort the data by origin order
        scope_data = scope_data.sort_index()
        # change back to the origin name
        scope_data.index = scope_data.index.to_series().replace(letter2month, regex=True)
    get_scope_rearrange_more(scope_data)


def get_scope_rearrange(header, block_data):
    origin_data = copy.deepcopy(block_data)
    # in order to avoid repated calculation inside groups
    # # group by columns
    # header_col_name = origin_data.columns[header_split]
    # get_scope_rearrange_advanced(
    #     origin_data, header_col_name, header_split, 0, 1)
    # group by rows
    header_row_name = origin_data.columns[0]
    get_scope_rearrange_advanced(
        origin_data, header_row_name, 1, 0)


def get_scope_rearrange_advanced(origin_data, header_name, idx_num, col_num):
    grouped_data = dict(list(origin_data.groupby(header_name))).values()
    grouped_data_processed = []
    for g_data in grouped_data:
        print(g_data)
        if g_data.shape[1] - 1 > 1:  # many col headers, concat them
            g_data = merge_columns(g_data, 0,
                                   origin_data.shape[1] - 1, 'Merged_col')
        print(g_data)
        g_data = g_data.pivot(
            index=g_data.columns[idx_num],
            columns=g_data.columns[col_num],
            values=g_data.columns[-1]
        )
        if check_is_temporal(g_data):
            # for temporal data, record the origin order
            g_data.index = g_data.index.to_series().replace(month2letter, regex=True)
            # sort the data by origin order
            g_data = g_data.sort_index()
            # change back to the origin name
            g_data.index = g_data.index.to_series().replace(letter2month, regex=True)
        grouped_data_processed.append(g_data)
    tmp_corr_list = []
    tmp_scope_list = []
    tmp_score = float('inf')
    for i in range(len(grouped_data_processed) - 1):
        for k in range(len(grouped_data_processed[i].columns)):
            tmp_corr_vars = [(i, k)]
            scope_data = grouped_data_processed[i].iloc[:, k]
            for j in range(i + 1, len(grouped_data_processed)):
                for l in range(len(grouped_data_processed[j].columns)):
                    scope_data_subset = pd.concat(
                        [grouped_data_processed[i].iloc[:, k], grouped_data_processed[j].iloc[:, l]], axis=1)
                    ins_type, ins_score, ins_description = calc_compound_insight(
                        scope_data_subset)

                    if ins_type == 'correlation-temporal':  # only merge when temporal data
                        tmp_corr_vars.append((j, l))
                        tmp_score = min(tmp_score, ins_score)
                        scope_data = pd.concat(
                            [scope_data, grouped_data_processed[j].iloc[:, l]], axis=1)
                    elif ins_type == 'correlation':  # no merge, directly save the insight
                        save_insight(scope_data_subset,
                                     'compound', ins_type, ins_score)
            if len(tmp_corr_vars) > 1:
                tmp_corr_list.append(tmp_corr_vars)
                tmp_scope_list.append(scope_data)
    if len(tmp_corr_list) > 0:
        # tmp_list = merge_lists_with_common_element(tmp_list)
        # TODO simply pick the longest list, may cause problems
        scope_data = max(tmp_scope_list, key=len)
        save_insight(scope_data, 'compound', 'correlation-temporal', tmp_score)


def insight_exists(header, insight):
    global subspace_insight
    for existing_insight in subspace_insight[header]:
        if existing_insight.type == insight.type \
           and existing_insight.scope_data.equals(insight.scope_data) \
           and existing_insight.score == insight.score \
           and existing_insight.category == insight.category \
           and existing_insight.description == insight.description:
            return True
    return False


def save_insight(header, scope_data, ins_category, ins_type, ins_score, header_description, ins_description, breakdown=None,
                 aggregate=None):
    global subspace_insight

    # avoid duplicate headers caused by different orders
    sorted_header = tuple(sorted(map(str, header)))
    insight = Insight(scope_data, breakdown, aggregate)
    insight.type = ins_type
    insight.score = ins_score
    insight.category = ins_category
    insight.context = header_description
    insight.description = ins_description

    if sorted_header not in subspace_insight:
        subspace_insight[sorted_header] = []
    if not insight_exists(sorted_header, insight):
        subspace_insight[sorted_header].append(insight)

    # # keep the top1 insight for each category
    # if block_insight[ins_category] is None:
    #     block_insight[ins_category] = insight
    # elif block_insight[ins_category].score < insight.score:
    #     block_insight[ins_category] = insight

    # keep_top_k(ins_category, insight, 3)


    # sort the insight list
    # if len(block_insight[ins_category]) > 1:
    #     block_insight[ins_category].sort(key=lambda x: x.score, reverse=True)


def get_scope_rearrange_more(d):
    for i in range(len(d.columns)):
        for j in range(i + 1, len(d.columns)):
            scope_data = pd.concat([d.iloc[:, i], d.iloc[:, j]], axis=1)
            calc_insight(scope_data, None, 'compound')


def calc_insight(header, scope_data, breakdown, aggregate, no_aggreate=False, is_month=False):
    ins_type = ''
    ins_score = 0
    header_description = "Filtered the original data table with the conditions: "
    header_description += generate_header_template(table_structure, header)

    # ins_des = "The insight of the filtered subspace is: \n"

    if check_is_temporal(scope_data, is_month):
        # shape only temporal
        ins_type, ins_score, ins_description = calc_shape_insight(scope_data)
        if ins_score > 0:
            save_insight(header, scope_data, 'shape', ins_type,
                         ins_score, header_description, ins_description, breakdown, aggregate)

        # outlier_temporal
        insights = calc_outlier_temporal(scope_data)
        for insight in insights:
            save_insight(header, scope_data, 'point', insight['ins_type'],
                         insight['ins_score'], header_description, insight['ins_description'], breakdown, aggregate)

        # point
        ins_type, ins_score, ins_description = calc_point_insight(scope_data, no_aggreate)
        if ins_score > 0:
            save_insight(header, scope_data, 'point', ins_type,
                         ins_score, header_description, ins_description, breakdown, aggregate)

        # distribution
        # remove all zeros when calculating distribution insight
        # scope_data = scope_data[scope_data != 0]
        ins_type, ins_score, ins_description = calc_distribution_insight(scope_data)
        if ins_score > 0:
            save_insight(header, scope_data, 'shape', ins_type,
                         ins_score, header_description, ins_description, breakdown, aggregate)
    else:
        # point
        ins_type, ins_score, ins_description = calc_point_insight(scope_data, no_aggreate)
        if ins_score > 0:
            save_insight(header, scope_data, 'point', ins_type,
                         ins_score, header_description, ins_description, breakdown, aggregate)

        # outlier
        insights = calc_outlier(scope_data)
        for insight in insights:
            save_insight(header, scope_data, 'point', insight['ins_type'],
                         insight['ins_score'], header_description, insight['ins_description'], breakdown, aggregate)

        # distribution
        # remove all zeros when calculating distribution insight
        # scope_data = scope_data[scope_data != 0]
        ins_type, ins_score, ins_description = calc_distribution_insight(scope_data)
        if ins_score > 0:
            save_insight(header, scope_data, 'shape', ins_type,
                         ins_score, header_description, ins_description, breakdown, aggregate)


def generate_header_template(table_structure, filter_condition):
    def convert_filter_condition_to_string(condition):
        attribute_names = list(table_structure.keys())
        explanations = []
        for i, value in enumerate(condition):
            if value in table_structure[attribute_names[i]]:
                explanations.append(f"{attribute_names[i]} = {value}")
            else:
                for key, values in table_structure.items():
                    if value in values:
                        explanations.append(f"{key} = {value}")
                        break
        return ', '.join(explanations)

    description = convert_filter_condition_to_string(filter_condition)
    return f"[{description}]"


def keep_top_k(category, insight, k=3):
    # add the new insight element
    heapq.heappush(block_insight[category], insight)
    if len(block_insight[category]) > k:
        heapq.heappop(block_insight[category])  # pop the smallest element


def merge_lists_with_common_element(lists):
    merged_lists = []
    for new_list in lists:
        merged = False
        for old_list in merged_lists:
            if set(new_list).intersection(set(old_list)):
                old_list.extend(new_list)
                merged = True
                break
        if not merged:
            merged_lists.append(new_list)
    return merged_lists
