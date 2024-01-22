import pandas as pd
import json
import time
from insight import get_insight
from visualization import get_visualization
from graph import get_node, get_links, get_state_links, get_id


class HierarchicalTable:
    def __init__(self, data_source):
        self.data_source = data_source
        self.origin_data = pd.read_excel(
            data_source.source_path, header=data_source.header_row, index_col=data_source.header_col).fillna(0)
        self.all_nodes = None
        self.all_links = None
        self.block_has_insight = None

    def generate_all_results(self):
        self.generate_blocks()
        self.generate_links()

        graph = self.generate_graph()
        filepath = self.data_source.get_result_path()
        with open(filepath, mode='w') as f:
            json.dump(graph, f)
            print('done')

    def generate_blocks(self):
        self.all_nodes = []
        self.block_has_insight = []
        # all combination of headers
        args_list = []

        src_data = self.origin_data
        columns = src_data.columns.tolist()
        index = src_data.index.tolist()
        all_columns = self.generate_all_headers(columns)
        all_index = self.generate_all_headers(index)

        for idx in all_index:
            for col in all_columns:
                idx_cond = len(idx) == len(src_data.index[0]) or \
                    (len(idx) == 1 and type(src_data.index[0]) != tuple)
                col_cond = len(col) == len(src_data.columns[0]) or \
                    (len(col) == 1 and type(src_data.columns[0]) != tuple)
                if idx_cond and col_cond:
                    continue    # skip the singel cell
                if len(idx) == 0 and len(col) == 0:
                    continue    # skip the whole table
                # iterate all blocks, and keep the column name
                args = (idx, col)
                args_list.append(args)

        print('processing blocks...')
        # # no multi-processing
        # # start here
        for args in args_list:
            node = self.process_block(args)
            if node != None:
                # if set(idx+col) in curr_focus_headers:
                #     continue
                self.all_nodes.append(node)
                self.block_has_insight.append((idx, col))
        # end here
        # print(self.all_nodes)

    def generate_links(self):
        print('processing links...')
        blocks = self.block_has_insight
        # grp_list = list(blocks)
        self.all_links = get_links([(0, list(blocks))])
        # print(self.all_links)

    def process_block(self, args):
        s_time = time.time()
        src_data = self.origin_data
        idx, col = args
        transformed_state = 0

        header = (idx, col)
        block_data = self.get_block_data(src_data, idx, col)
        # print('block data:', block_data)
        # calculate the split of column and row headers in a block data
        header_split = len(src_data.index[0]) - len(idx)

        insight_list = get_insight(
            header, block_data, header_split, transformed_state)
        # self.block_insight[header] = insight_list   # save the insight of the block
        vis_list = get_visualization(insight_list)
        # self.block_vis[header] = vis_list   # save the visulization of the block

        node = None
        if vis_list != []:
            global_state = 0
            node = get_node(idx, col, vis_list, global_state)
            print("header:\n", header)
            print('row data:\n', block_data)
            print('insights:\n', insight_list)

        # print('node complete!')
        e_time = time.time()
        # print('state:', transformed_state, '    block:', idx, col, '    shape:', block_data.shape,'    time:', e_time - s_time)
        return node

    def get_block_data(self, src_data, idx, col):
        '''
        get the data of a block from origin data and convert it to flat table
        idx is the index of the block, e.g. ('Nintendo', '3DS')
        col is the column of the block, e.g. ('2011', 'JUN')
        '''
        # get block data from origin data
        block = None
        if len(idx) == 0:
            block = src_data.sort_index().loc[:, col]
        elif len(col) == 0:
            block = src_data.sort_index().loc[idx, :]
        else:
            block = src_data.sort_index().loc[idx, col]
        res = None
        if isinstance(block, pd.Series):
            res = block.to_frame()   # convert to dataframe
            res.columns = ['value']   # set column name
            res = res.reset_index()  # convert to flat table
        elif block.shape[1] == 1:
            res = block.reset_index()
        else:
            # convert to flat table
            res = block.melt(ignore_index=False).reset_index()

        # # get the length of the original header
        # origin_col_len = len(self.origin_data.columns[0])
        # origin_idx_len = len(self.origin_data.index[0])
        # # if the header is from a higher level, add the higher level header to the flat table
        # if len(idx) < origin_idx_len:
        #     for i in range(len(idx)):
        #         res.insert(i, 'idx'+str(i), idx[i])
        # if len(col) < origin_col_len:
        #     for i in range(len(col)):
        #         res.insert(origin_idx_len+i, 'col'+str(i), col[i])

        # with open('data/all_block.csv', mode='a') as f:
        #     f.write(''+str(idx)+str(col)+'\n')
        #     res.to_csv(f, index=False)
        return res

    def generate_all_headers(self, header_list):
        res = [()]
        for i in range(len(header_list)):
            header = header_list[i]
            if type(header) == tuple:
                for j in range(1, len(header)):
                    new_header = header[:j]
                    if new_header not in res:   # avoid duplicate
                        res.append(new_header)
            else:   # header is a list
                header_list[i] = (header,)
        res.extend(header_list)
        return list(res)

    def generate_graph(self):
        # generate result json
        graph = {}
        graph['nodes'] = self.all_nodes
        graph['links'] = self.all_links
        return graph
