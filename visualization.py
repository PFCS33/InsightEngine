import json
import pandas as pd
import copy



class VisualForm:
    def __init__(self, data, insight_type, insight_category, insight_score, insight_description):
        self.data = data
        self.insight_type = insight_type
        self.insight_category = insight_category
        self.insight_score = insight_score
        self.description = insight_description
        self.vega_json = None
        self.create_vegalite()
    
    def create_vegalite(self):
        func_list= {'outlier': create_box_plot, 
                    'outlier-temporal': create_trail_plot,
                    'dominance':create_pie_chart_dominance,
                    'top2':create_pie_chart_top2,
                    'trend':create_area_chart, 
                    'correlation': create_scatter_plot, 
                    'correlation-temporal': create_multi_line_chart,
                    'kurtosis': create_density_plot_color,
                    'skewness': create_density_plot,
                    'evenness': create_bar_chart
                    }
        # scope_data = None
        # # merge the first [merge_num] columns as the breakdown column
        # merge_num = self.data.shape[1] - 1
        # scope_data = merge_columns(self.data, 0, merge_num)
        #
        # # set the breakdown column as index
        # scope_data = scope_data.set_index(scope_data.columns[0])
        # # turn the dataframe to series
        # scope_data = scope_data[scope_data.columns[0]]

        vega_obj = func_list[self.insight_type](self.data)
        self.vega_json = json.dumps(vega_obj)


def preprocess_data(data):
    scope_data = None
    # merge the first [merge_num] columns as the breakdown column
    merge_num = data.shape[1] - 1
    scope_data = merge_columns(data, 0, merge_num)

    # set the breakdown column as index
    scope_data = scope_data.set_index(scope_data.columns[0])
    # turn the dataframe to series
    scope_data = scope_data[scope_data.columns[0]]

    return scope_data


def merge_columns(block_data, start, end, name='Merged'):
    data = copy.deepcopy(block_data)
    merged_col = data.iloc[:, start:end].apply(
        lambda x: ' - '.join(x.astype(str)), axis=1)
    merged_col.name = name
    res = pd.concat([data.iloc[:, :start], merged_col,
                     data.iloc[:, end:]], axis=1)

    return res


def create_bar_chart(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    if d[d.columns[0]].str.contains('-').any(): # include multiple columns, break it          
        d_tmp = d[d.columns[0]].str.split('-', n=1, expand=True)
        d_tmp.columns = ['var1', 'var2']
        d.drop(columns=d.columns[0], inplace=True)
        d = pd.concat([d_tmp['var1'], d], axis=1)  # only 2 columns
    d.columns = ['variable', 'value']
    for row in d.itertuples(index=False):
        v = {}
        for i in range(len(d.columns)):
            v[d.columns[i]] = row[i]
        values.append(v)
    mark = 'bar'
    encoding = {
        'x': {'field': d.columns[-2], 'type': 'nominal', "title": None},
        'y': {'field': d.columns[-1], 'type': 'quantitative', "title": None},
        'tooltip': [
            {'field': d.columns[-2], 'type': 'nominal'},
            {'field': d.columns[-1], 'type': 'quantitative'}
        ]
    }
    # if len(d.columns)==3:   # breaked columns
    #     encoding["xOffset"] = {"field": d.columns[0]}
    #     encoding['color'] = {'field': d.columns[0],
    #                          'type': 'nominal',
    #                          "legend": {"orient": "bottom"},
    #                          "title": None}
    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def create_pie_chart_dominance(d):
    # get dominance name to create legend
    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    top1_name = sorted_d.iloc[0, 0]

    # merge columns
    d = preprocess_data(d)
    values = []
    d = d.reset_index()

    d.columns = ['category', 'value']
    for row in d.itertuples(index=False):
        # if row[1] == 0:
        #     continue    # ignore zeros
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
    mark = {'type': 'arc', 'innerRadius': 5, 'stroke': '#fff'}
    encoding = {
        'theta': {'field': 'value', 'type': 'quantitative', "stack": True},
        'color': {'field': 'category', 'type': 'nominal'},
        'order': {
            'field': 'value',
            'type': 'quantitative',
            'sort': 'descending'
        },
        "radius": {"field": "value", "scale": {"type": "linear", "zero": True, "rangeMin": 20}},
        'tooltip': [
            {'field': 'category', 'type': 'nominal'},
            {'field': 'value', 'type': 'quantitative'}
        ]
    }

    # Adding legend for dominance categories
    encoding['color']['legend'] = {'title': None, 'symbolType': 'square', 'values': [str(top1_name)]}

    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}


def create_pie_chart_top2(d):
    # get top2 name to create legend
    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    top1_name = sorted_d.iloc[0, 0]
    top2_name = sorted_d.iloc[1, 0]

    # merge columns
    d = preprocess_data(d)
    values = []
    d = d.reset_index()

    d.columns = ['category', 'value']
    for row in d.itertuples(index=False):
        # if row[1] == 0:
        #     continue    # ignore zeros
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
    mark = {'type': 'arc', 'innerRadius': 5, 'stroke': '#fff'}
    encoding = {
        'theta': {'field': 'value', 'type': 'quantitative', "stack": True},
        'color': {'field': 'category', 'type': 'nominal'},
        'order': {
            'field': 'value',
            'type': 'quantitative',
            'sort': 'descending'
        },
        "radius": {"field": "value", "scale": {"type": "linear", "zero": True, "rangeMin": 20}},
        'tooltip': [
            {'field': 'category', 'type': 'nominal'},
            {'field': 'value', 'type': 'quantitative'}
        ]
    }

    # Adding legend for top 2 categories
    encoding['color']['legend'] = {'title': None, 'symbolType': 'square', 'values': [str(top1_name), str(top2_name)]}

    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def create_area_chart(d, color='#4682b4'):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    if d[d.columns[0]].str.contains('-').any(): # include multiple columns, break it
        d_tmp = d[d.columns[0]].str.split('-', n=1, expand=True)
        d_tmp.columns = ['var1', 'var2']
        d.drop(columns=d.columns[0], inplace=True)
        d = pd.concat([d_tmp['var1'], d], axis=1)  # only 2 columns
    d.columns = ['variable', 'value']
    sort = []
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
        sort.append(row[0])
    mark = {
        'type': 'area', 
        'interpolate':'monotone',
        "line": {"color": color},
        "color": {
            "x1": 1,
            "y1": 1,
            "x2": 1,
            "y2": 0,
            "gradient": "linear",
            "stops": [
                {
                    "offset": 0,
                    "color": "white"
                },
                {
                    "offset": 1,
                    "color": color
                }
            ]
        }
    }
    encoding = {
        'x': {'field': d.columns[0], 'type': 'nominal', 'sort': sort, 'axis': {'labelOverlap': True, 'title': None}},
        'y': {'field': d.columns[1], 'type': 'quantitative', "title": None},
        'tooltip': [
            {'field': d.columns[0], 'type': 'nominal'},
            {'field': d.columns[1], 'type': 'quantitative'}
        ]
    }
    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def create_scatter_plot(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1], d.columns[2]: row[2]}
        values.append(v)
    mark = 'point'
    encoding = {
        'x': {'field': d.columns[1], 'type': 'quantitative'},
        'y': {'field': d.columns[2], 'type': 'quantitative'},
        'tooltip': [
            {'field': d.columns[1], 'type': 'quantitative'},
            {'field': d.columns[2], 'type': 'quantitative'}
        ]
    }
    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def create_multi_line_chart(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    d = d.melt(id_vars=[d.columns[0]])
    
    sort = []
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1], d.columns[2]: row[2]}
        values.append(v)
        sort.append(row[0])
    mark = {'type': 'line', 'interpolate':'monotone'}
    encoding = {
        'x': {'field': d.columns[0], 
              'type': 'nominal',
              'axis': {'labelOverlap': True, 'title': None}, 
              'sort':sort
            },
        'y': {'field': d.columns[2], 'type': 'quantitative', 'title': None},
        'color': {'field': d.columns[1], 'type': 'nominal', 'legend': {'orient':'bottom'}, 'title': None},
        'tooltip': [
            {'field': d.columns[0], 'type': 'nominal'},
            {'field': d.columns[2], 'type': 'quantitative'}
        ]
    }
    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def create_box_plot(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    d.columns = ['category', 'value']
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
    mark = {
        "type": "boxplot",
        "extent": 1.5,
        "size": 20,
        "median": {"color": "white"},
        "ticks": True
    }
    encoding = {
        'x': {'field': d.columns[1], 'type': 'quantitative', 'title': None},
        'tooltip': [
            {'field': d.columns[0], 'type': 'nominal'},
            {'field': d.columns[1], 'type': 'quantitative'}
        ]
    }
    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def create_box_and_bar_plot(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    if d[d.columns[0]].str.contains('-').any(): # include multiple columns, break it          
        d_tmp = d[d.columns[0]].str.split('-', n=1, expand=True)
        d_tmp.columns = ['var1', 'var2']
        d.drop(columns=d.columns[0], inplace=True)
        d = pd.concat([d_tmp['var1'], d], axis=1)
    d.columns = ['variable', 'value']
    for row in d.itertuples(index=False):
        v = {}
        for i in range(len(d.columns)):
            v[d.columns[i]] = row[i]
        values.append(v)
    bar_mark = 'bar'
    bar_encoding = {
        'x': {'field': d.columns[-2], 'type': 'nominal', "title": None},
        'y': {'field': d.columns[-1], 'type': 'quantitative', "title": None},
        'tooltip': [
            {'field': d.columns[-2], 'type': 'nominal'},
            {'field': d.columns[-1], 'type': 'quantitative'}
        ]
    }
    if len(d.columns)==3:   # breaked columns
        bar_encoding["xOffset"] = {"field": d.columns[0]}
        bar_encoding['color'] = {'field': d.columns[0], 
                             'type': 'nominal', 
                             "legend": {"orient": "bottom"},
                             "title": None}
    box_mark = {
        "type": "boxplot",
        "extent": 4,
        "size": 20,
        "median": {"color": "white"},
        "ticks": True
    }
    box_encoding = {
        'x': {'field': d.columns[-1], 'type': 'quantitative', 'title': None},
        'tooltip': [
            {'field': d.columns[0], 'type': 'nominal'},
            {'field': d.columns[-1], 'type': 'quantitative'}
        ]
    }
    vconcat = [
        {"mark": box_mark, "encoding": box_encoding}, 
        {"mark": bar_mark, "encoding": bar_encoding}
    ]
    data = {'values': values}
    return {'data': data, "spacing": 15, "bounds": "flush", 'vconcat': vconcat}

def create_density_plot(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    d.columns = ['category', 'value']
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
    transform = [{"density": d.columns[1]}]
    mark = {
        'type': "area",
        "color": {
            "x1": 1,
            "y1": 1,
            "x2": 1,
            "y2": 0,
            "gradient": "linear",
            "stops": [
                {
                    "offset": 0,
                    "color": "white"
                },
                {
                    "offset": 1,
                    "color": 'darkgreen'
                }
            ]
        }
    }
    encoding = {
        "x": {
            "field": d.columns[1],
            "title": None,
            "type": "quantitative"
        },
        "y": {
            "field": "density",
            "type": "quantitative",
        }
    }
    data = {'values': values}
    return {'data': data, 'transform':transform ,'mark': mark, 'encoding': encoding}

def create_density_plot_color(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    d.columns = ['category', 'value']
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
    transform = [{"density": d.columns[1]}]
    mark = {
        'type': "area",
        "color": {
            "x1": 1,
            "y1": 1,
            "x2": 1,
            "y2": 0,
            "gradient": "linear",
            "stops": [
                {
                    "offset": 0,
                    "color": "white"
                },
                {
                    "offset": 1,
                    "color": '#e6550d'
                }
            ]
        }
    }
    encoding = {
        "x": {
            "field": d.columns[1],
            "title": None,
            "type": "quantitative"
        },
        "y": {
            "field": "density",
            "type": "quantitative",
        }
    }
    data = {'values': values}
    return {'data': data, 'transform':transform ,'mark': mark, 'encoding': encoding}

def create_trail_plot(d):
    d = preprocess_data(d)
    values = []
    d = d.reset_index()
    if d[d.columns[0]].str.contains('-').any():  # include multiple columns, break it
        d_tmp = d[d.columns[0]].str.split('-', n=1, expand=True)
        d_tmp.columns = ['var1', 'var2']
        d.drop(columns=d.columns[0], inplace=True)
        d = pd.concat([d_tmp['var1'], d], axis=1)
    d.columns = ['category', 'value']

    sort = []
    for row in d.itertuples(index=False):
        v = {d.columns[0]: row[0], d.columns[1]: row[1]}
        values.append(v)
        sort.append(row[0])
    mark = {
        "type": "trail"
    }
    encoding = {
        'x': {'field': d.columns[0], 'type': 'nominal', 'sort':sort, 'axis': {'labelOverlap': True, 'title': None}},
        'y': {'field': d.columns[1], 'type': 'quantitative', 'title': None},
        'size': {'field': d.columns[1], 'type': 'quantitative', 'legend': None},
        'tooltip': [
            {'field': d.columns[0], 'type': 'nominal'},
            {'field': d.columns[1], 'type': 'quantitative'}
        ]
    }
    data = {'values': values}
    return {'data': data, 'mark': mark, 'encoding': encoding}

def get_visualization(insight_list):
    vis_list = {}
    # if insight_list['point'] != [] \
    #     or insight_list['shape'] != [] \
    #     or insight_list['compound'] != []:
    #     for category in insight_list:
    #         insights = insight_list[category]
    #         for insight in insights:
    #             vis = VisualForm(insight.scope_data, insight.type, insight.category, insight.score)
    #             vis_list.append(vis)
    for sorted_header, insights in insight_list.items():
        if sorted_header not in vis_list:
            vis_list[sorted_header] = []
        for insight in insights:
            vis = VisualForm(insight.scope_data, insight.type, insight.category, insight.score, insight.description)
            vis_list[sorted_header].append(vis)
        # sort the vis_list for each header
        vis_list[sorted_header].sort(key=lambda x: x.insight_score, reverse=True)

    return vis_list