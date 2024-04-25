import pandas as pd
import json
import time
from insight import get_insight
from visualization import get_visualization
from graph import get_node, get_links, get_state_links, get_id
import itertools
import os
import copy
import pickle

# subspace_list = {}
cnt_insight_num = 0
cnt_header_num = 0

class HierarchicalTable:
    def __init__(self, data_source):
        self.data_source = data_source
        self.value_col_index = -1
        self.origin_data = self.get_origin_data()
        self.header_dict = self.get_header_dict()
        # self.unique_value_dict = self.get_unique_value_dict(
        #     self.origin_data.columns[:-1])
        self.all_nodes = None
        self.all_links = None
        self.block_has_insight = None

    def get_origin_data(self):
        data_source = self.data_source
        if (data_source.name_suffix == 'csv'):
            return pd.read_csv(data_source.source_path, header=0).fillna(0)
        elif (data_source.name_suffix == 'xlsx'):
            return pd.read_excel(
                data_source.source_path, header=0).fillna(0)
            # return pd.read_excel(
            #     data_source.source_path, header=data_source.header_row, index_col=data_source.header_col).fillna(0)
        else:
            return None

    def generate_all_results(self):
        self.generate_blocks()
        # self.generate_links()

        graph = self.generate_graph()
        filepath = self.data_source.get_result_path()
        with open(filepath, mode='w') as f:
            json.dump(graph, f)
            print('done')

    def generate_blocks(self):
        self.all_nodes = []
        # self.block_has_insight = []

        src_data = self.origin_data
        header_dict = self.header_dict

        print('processing blocks...')
        # no multi-processing
        # start here
        global cnt_insight_num, cnt_header_num, subspace_insight, this_insight
        cnt_insight_num = 0
        cnt_header_num = 0
        if os.path.exists('headers.txt'):
            os.remove('headers.txt')
        with open('headers.txt', 'w') as file:
            for key in header_dict.keys():
                file.write(str(key) + '\n')

        if os.path.exists('vis_list.txt'):
            os.remove('vis_list.txt')
        for header in header_dict:
            subspace_insight = self.process_block(header)
            # if node != None:
            #     # if set(idx+col) in curr_focus_headers:
            #     #     continue
            #     self.all_nodes.append(node)
            # self.block_has_insight.append(header)
        vis_list = get_visualization(subspace_insight)
        cnt_header_num = 0
        cnt_insight_num = 0
        if any(vis_list.values()):
            result_file = "vis_list_VegaLite.txt"
            with open(result_file, 'w') as file:

                for header, insights_list in vis_list.items():
                    cnt_header_num += 1
                    file.write('=' * 100 + '\nHeader: ' + str(header) + '\n')
                    # file.write('='*30 + ' [Header] ' + str(cnt_header_num) + ' ' + str(header) + '='*30 + '\n')
                    for insight in insights_list:
                        cnt_insight_num += 1
                        file.write(f"Insight num: {cnt_insight_num}\n")
                        # file.write(f"Data: \n{insight.data}\n")
                        file.write(f"Type: {insight.insight_type}\n")
                        file.write(f"Score: {insight.insight_score}\n")
                        file.write(f"Category: {insight.insight_category}\n")
                        file.write(f"Description: {insight.description}\n")
                        file.write(f"Vega-Lite Json: {insight.vega_json}\n")
                        file.write("\n")
        if any(vis_list.values()):
            result_file = "vis_list.txt"
            with open(result_file, 'w') as file:
                for header, insights_list in vis_list.items():
                    file.write('=' * 100 + '\nHeader: ' + str(header) + '\n')
                    cnt_ins = 0
                    for insight in insights_list:
                        cnt_ins += 1
                        file.write(f"Insight{cnt_ins}: \n")
                        file.write(f"Type: {insight.insight_type}\n")
                        file.write(f"Score: {insight.insight_score}\n")
                        file.write(f"Category: {insight.insight_category}\n")
                        file.write(f"Description: {insight.description}\n")
                        file.write("\n")
        # file_path = 'subspace_list.txt'
        # with open(file_path, 'w') as file:
        #     json.dump(subspace_list, file, indent=4)

        # end here
        # print(self.all_nodes)

    def generate_links(self):
        print('processing links...')
        blocks = self.block_has_insight
        # grp_list = list(blocks)
        self.all_links = get_links([(0, list(blocks))])
        # print(self.all_links)

    def process_block(self, header):
        global cnt_insight_num, cnt_header_num
        s_time = time.time()
        src_data = self.origin_data
        header_dict = self.header_dict

        # get raw data through header
        block_data = self.get_block_data(header)

        aggregated_header = ""

        block_insight, subspace_insight = get_insight(header, block_data)
        # self.block_insight[header] = insight_list   # save the insight of the block
        # vis_list = get_visualization(subspace_insight)
        # self.block_vis[header] = vis_list   # save the visulization of the block

        node = None

        file_name = os.path.join('all_result_insights', str(header) + '.txt')
        header_str = '-'.join(map(str, header))
        result_file = "subspace_insight.txt"


        if any(block_insight.values()):
            pass
            # node = get_node(header, vis_list)
            # print("header:\n", header)
            # print('row data:\n', block_data)
            # print("------------------\n")
            # print('insights:\n', insight_list)
            #
            # with open(file_name, 'w') as file:
            #     file.write("header:\n" + str(header) + "\n")
            #     file.write('row data:\n' + str(block_data) + "\n")
            #     file.write('------------------\n')
            #     file.write('insights:\n' + str(block_insight) + "\n")

            # with open(result_file, 'a') as file:
            #     cnt_insight_num += 1
            #     file.write("Number" + str(cnt_insight_num) + "\n")
            #     file.write("header:" + str(header) + "\n")
            #     file.write('insights:\n' + str(block_insight) + "\n")

        # else:
        #     cnt_none_insight_num += 1
        #     print("No.", cnt_none_insight_num, "header: ", header)
        if any(subspace_insight.values()):
            pass
            # print("------------------\n")
            # print('aggregated header:\n', aggregated_header)
            # print('aggregated data:\n', aggregated_data)
            # print("------------------\n")
            # print('aggregated insights:\n', aggregated_insight_list)
            # print("---------------------------------------------------")

            # file_name = os.path.join('all_result_insights', str(header) + '.txt')
            # with open(file_name, 'a') as file:
            #     file.write('---------------------------\n')
            #     file.write('aggregated header:\n' + str(aggregated_header) + "\n")
            #     file.write('aggregated data:\n' + str(subspace_insight) + "\n")
            #     file.write('------------------\n')
            #     file.write('aggregated insights:\n' + str(subspace_insight) + "\n")

            # with open(result_file, 'a') as file:
                # # cnt_insight_num += 1
                # for header, insights_list in subspace_insight.items():
                #     file.write('-'*100)
                #     file.write("\n")
                #     cnt_header_num += 1
                #     file.write(f"Header num: {cnt_header_num}\n")
                #     file.write(f"Header: {header}\n")
                #     for insight in insights_list:
                #         cnt_insight_num += 1
                #         file.write(f"Insight num: {cnt_insight_num}\n")
                #         file.write(f"Scope Data: \n{insight.scope_data}\n")
                #         file.write(f"Type: {insight.type}\n")
                #         file.write(f"Score: {insight.score}\n")
                #         file.write(f"Category: {insight.category}\n")
                #         # file.write(f"Context: {insight.context}\n")
                #         file.write(f"Description: {insight.description}\n")
                #         file.write("\n")

            # aggregated_header_str = '-'.join(map(str, aggregated_header))
            # subspace_list.setdefault(header_str, {})['aggregated_header'] = aggregated_header_str
            # subspace_list.setdefault(header_str, {}).setdefault('aggregated_insight_list', []).extend(
            #     aggregated_insight_list_str)

        # print('node complete!')
        e_time = time.time()

        # return node
        return subspace_insight

    def get_block_data(self, header):
        '''
        get the data of a block from flat table, and get rid of fixed columns
        '''
        df = self.origin_data
        header_dict = self.header_dict
        condition, fixed_columns = header_dict[header]

        return df[condition].drop(list(fixed_columns), axis=1).reset_index(drop=True)

    def get_header_condition(self, header):
        df = self.origin_data
        # check if header is correspond to data blocks
        condition = pd.Series([True] * len(df))
        for column in header.index:
            condition &= (df[column] == header[column])
        return condition

    def get_header_dict(self):
        df = self.origin_data
        value_label = df.columns[self.value_col_index]
        columns_new = [col for col in df.columns if col != value_label]

        all_fixed_combinations = []
        for length in range(1, len(columns_new)):
            combinations = itertools.combinations(columns_new, length)
            all_fixed_combinations.extend(combinations)

        res = {}
        for index, row in df.iterrows():
            for combination in all_fixed_combinations:
                header = row.loc[list(combination)]
                header_tuple = None
                if isinstance(header, pd.Series):
                    header_tuple = tuple(header)
                else:
                    header_tuple = (header,)
                if header_tuple not in res:
                    condition = self.get_header_condition(header)
                    if sum(condition) > 1:
                        res[header_tuple] = (condition, combination)

        return res

        # for i in range(len(header_list)):
        #     header = header_list[i]
        #     if type(header) == tuple:
        #         for j in range(1, len(header)):
        #             new_header = header[:j]
        #             if new_header not in result_insights:   # avoid duplicate
        #                 result_insights.append(new_header)
        #     else:   # header is a list
        #         header_list[i] = (header,)
        # result_insights.extend(header_list)
        # return list(result_insights)

    # def get_unique_value_dict(self, non_value_columns):
    #     df = self.origin_data
    #     unique_value_dict = {}
    #     for column in non_value_columns:
    #         unique_value_dict[column] = df[column].unique()
    #     print(unique_value_dict)
    #     return unique_value_dict

    def generate_graph(self):
        # generate result json
        graph = {}
        graph['nodes'] = self.all_nodes
        return graph
