import numpy as np
import pandas as pd
from scipy.stats import linregress, skewtest, kurtosistest, skew, kurtosis

has_insight = False
# file_path = r'your_file.xlsx'
file_path = r'D:\1-WORK\RESEARCH\InsightEngine\Insight_Calculator\examples\异常点.xlsx'

def calc_point_insight(d):
    ins_type = ''
    ins_score = 0
    description = ""

    # sort according to the last value, sales in this case
    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    # the value column
    sorted_values = sorted_d.iloc[:, -1].values

    if len(sorted_values) < 3 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0:
        return ins_type, ins_score, description  # too few data or all zero

    if dominance_detection(sorted_values):
        ins_type = '主导性'
        ins_score = sorted_values[0] / np.sum(sorted_values)
        description = generate_dominance_description(sorted_d)
    elif top2_detection(sorted_values):
        ins_type = 'top2'
        ins_score = sorted_values[0] / np.sum(sorted_values)
        description = generate_top2_description(sorted_d)

    return ins_type, ins_score, description


def calc_outlier(d):
    ins_type = ''
    ins_score = 0
    description = ""

    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    sorted_values = sorted_d.iloc[:, -1].values

    if len(sorted_values) < 8 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0:
        return ins_type, ins_score, description  # too few data or all zero

    result = outlier_detection(sorted_values, 2)
    if result:
        outliers, lower_threshold, upper_threshold = result
        if len(outliers) != 0 and len(outliers) < 3:
            ins_type = '异常点'
            # max_ins_score = 0
            for outlier in outliers:
                index = np.where(sorted_values == outlier)[0]
                if outlier < lower_threshold:
                    ins_score = (outlier - sorted_values.mean()) / sorted_values.std()
                    description = generate_outlier_description(sorted_d, index, 'lower')
                    output_insight(ins_type, ins_score, description)
                elif outlier > upper_threshold:
                    ins_score = (outlier - sorted_values.mean()) / sorted_values.std()
                    description = generate_outlier_description(sorted_d, index, 'higher')
                    output_insight(ins_type, ins_score, description)
                # if ins_score > max_ins_score:
                #     max_ins_score = ins_score
            return ins_type, ins_score, description
        else:
            # else no outlier
            return ins_type, ins_score, description
    else:
        # else no outlier
        return ins_type, ins_score, description


def calc_outlier_temporal(d):
    ins_type = ''
    ins_score = 0
    description = ""

    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    sorted_values = sorted_d.iloc[:, -1].values

    if len(sorted_values) < 5 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0:
        return ins_type, ins_score, description  # too few data or all zero

    result = outlier_detection(sorted_values, 1.5)
    if result:
        outliers, lower_threshold, upper_threshold = result
        if len(outliers) != 0 and len(outliers) < 3:
            ins_type = '时序异常点'
            # max_ins_score = 0
            for outlier in outliers:
                index = np.where(sorted_values == outlier)[0]
                if outlier < lower_threshold:
                    ins_score = (outlier - sorted_values.mean()) / sorted_values.std()
                    description = generate_outlier_description(sorted_d, index, 'lower')
                    output_insight(ins_type, ins_score, description)
                elif outlier > upper_threshold:
                    ins_score = (outlier - sorted_values.mean()) / sorted_values.std()
                    description = generate_outlier_description(sorted_d, index, 'higher')
                    output_insight(ins_type, ins_score, description)
                # if ins_score > max_ins_score:
                #     max_ins_score = ins_score
            return ins_type, ins_score, description
        else:
            # else no outlier
            return ins_type, ins_score, description
    else:
        # else no outlier
        return ins_type, ins_score, description


def dominance_detection(d):
    # d is numeric
    if (d < 0).any():  # ignore when having negative values
        return False
    # d is already sorted descending
    zero_count = np.sum(d == 0)
    sum_d = np.sum(d)
    if d[0] / sum_d > 0.5 and d[0] / sum_d < 1 and d[1] / sum_d < 0.3 and len(d) - zero_count >= 3:
        return True
    else:
        return False


def generate_dominance_description(data):
    main_column_name = data.columns[0]
    top1_name = data.iloc[0, 0]
    value_name = data.columns[-1]
    return f"{value_name}方面，{top1_name}在所有{main_column_name}中占据主导地位。"


def top2_detection(d):
    # d is numeric
    if (d < 0).any():  # ignore when having negative values
        return False
    # d is already sorted descending
    zero_count = np.sum(d == 0)
    sum_d = np.sum(d)
    if d[0] / sum_d > 0.3 and d[1] / sum_d > 0.3 and d[2] / sum_d < 0.3 and len(d) - zero_count >= 3:
        return True
    else:
        return False


def generate_top2_description(data):
    main_column_name = data.columns[0]
    top1_name = data.iloc[0, 0]
    top2_name = data.iloc[1, 0]
    value_name = data.columns[-1]
    return f"{value_name}方面，{top1_name}和{top2_name}的{value_name}远超其他{main_column_name}。"


def outlier_detection(d, threshold=3):
    zero_count = np.sum(d == 0)
    if check_zero(d) > 0.1 or len(d) - zero_count < 4:  # too many zeros
        return False
    d = d[d != 0]   # remove zero
    Q1 = np.percentile(d, 25)
    Q3 = np.percentile(d, 75)
    IQR = Q3 - Q1
    lower_threshold = Q1 - threshold * IQR
    upper_threshold = Q3 + threshold * IQR
    outliers = d[(d < lower_threshold) | (d > upper_threshold)]

    return outliers, lower_threshold, upper_threshold


def generate_outlier_description(data, index, outlier_type):
    description = ""
    main_column_name = data.columns[0]
    main_column_index_value = data.iloc[index, 0].values[0]
    value_name = data.columns[-1]

    # The sale of brand PS4, season MAR is an outlier, which is significantly
    # higher than the normal sales of other brands in the corresponding season.
    description += f"{main_column_name}为{main_column_index_value}"
    if data.shape[1] > 2:
        for col_index in range(1, data.shape[1] - 1):
            column_name = data.columns[col_index]
            index_value = data.iloc[index, col_index].values[0]
            description += f"、{column_name}为{index_value}"
    description += f"的{value_name}是一个异常值点，"
    # print(description)
    description += "其明显"
    description += "低于" if outlier_type == 'lower' else "高于"
    description += f"其他{main_column_name}"
    # print(description)
    if data.shape[1] > 2:
        description += "在相应"
        for col_index in range(1, data.shape[1] - 2):
            column_name = data.columns[col_index]
            description += f"{column_name}、"
        column_name = data.columns[data.shape[1] - 2]
        description += f"{column_name}"
    description += f"的{value_name}。"

    return description


def calc_shape_insight(d):
    ins_type = ''
    ins_score = 0
    description = ""

    d_values = d.iloc[:, -1].values
    main_col_name = d.columns[0]
    value_name = d.columns[1]
    start_year = d.iloc[0, 0]
    end_year = d.iloc[-1, 0]

    trend_direction, trend = test_slope(d_values)
    if trend > 0.7:
        ins_type = '趋势'
        ins_score = trend
        description = f"随着{main_col_name}的增加，{value_name}呈现{trend_direction}趋势。"

    return ins_type, ins_score, description


def test_slope(d):
    if np.std(d) == 0:  # all the same, no slope
        return "no_slope", 0
    # Fit X to a line by linear regression
    _, _, r_value, p_value, _ = linregress(np.arange(len(d)), d)
    trend_direction = "上升" if r_value > 0 else "下降"
    trend_strength = r_value ** 2
    confidence = 1 - p_value
    trend = trend_strength * confidence
    return trend_direction, trend

    # # Calculate the p-value
    # n = len(d)
    # t_statistic = slope / (np.std(d) / np.sqrt(n))
    # degrees_of_freedom = n - 2
    # p_value = 2 * (1 - t.cdf(abs(t_statistic), df=degrees_of_freedom))


def check_is_temporal(data):
    def process_value(value):
        value_str = str(value)
        if len(value_str) < 4:
            return False
        eg_index = str(value_str)[:4]
        if eg_index.isdigit():
            if int(eg_index) >= 1800 and int(eg_index) <= 2300:
                return True
            else:
                return False
        else:
            return False

    # for every row in column 1
    result = data.iloc[:, 0].apply(process_value)
    if result.all():
        return True
    else:
        return False


def check_zero(d):
    return np.sum(d == 0) / len(d)


def calc_distribution_insight(d):
    d_value = d.iloc[:, -1].values
    # remove all zeros when calculating distribution insight
    d_value = d_value[d_value != 0]
    d_value = d_value.astype(float)

    if d_value.shape[0] <= 5:
        return '', 0, ""
    ins_type = ''
    ins_score = 0
    description = ""

    value_col_name = d.columns[-1]

    # evenness
    e = abs(d_value.std() / d_value.mean())
    # _, p_e = kstest(d_value, 'uniform', args=(0, 1))
    if e < 0.2:
        has_evenness = True
        ins_type = '均匀性'
        ins_score = 1 - e
        column_name = d.columns[0]
        description = f"{value_col_name}在不同{column_name}"
        if d.shape[1] > 2:
            for col_index in range(1, d.shape[1] - 2):
                column_name = d.columns[col_index]
                description += f"、{column_name}"
            column_name = d.columns[d.shape[1] - 2]
            description += f"和{column_name}"
        description += f"间的分布相对均匀。"
        return ins_type, ins_score, description

    elif d_value.shape[0] < 20:
        return '', 0, ""

    elif d_value.shape[0] >= 20:
        _, p_s = skewtest(d_value)
        s = skew(d_value)
        _, p_k = kurtosistest(d_value)
        k = kurtosis(d_value)
        has_skew = p_s < 0.03 and abs(s) > 2
        has_kurtosis = p_k < 0.05 and abs(k) > 3 and abs(s) < 3

        if has_skew and has_kurtosis:
            if p_s < p_k:
                ins_type, ins_score, description = set_skew(p_s, s, value_col_name)
            else:
                ins_type, ins_score, description = set_kurtosis(p_k, k, value_col_name)
        elif has_skew:
            ins_type, ins_score, description = set_skew(p_s, s, value_col_name)
        elif has_kurtosis:
            ins_type, ins_score, description = set_kurtosis(p_k, k, value_col_name)
        return ins_type, ins_score, description


def set_skew(p_s, s, value_col_name):
    ins_type = '偏度'
    ins_score = (1 - p_s) * abs(s)
    if s > 0:
        description = f"{value_col_name}呈右偏分布，即大多数{value_col_name}值集中在较小的数值范围内。"
    else:
        description = f"{value_col_name}呈左偏分布，即大多数{value_col_name}值集中在较大的数值范围内。"
    return ins_type, ins_score, description


def set_kurtosis(p_k, k, value_col_name):
    ins_type = '峰度'
    ins_score = (1 - p_k) * abs(k)
    if k > 0:
        description = f"{value_col_name}呈现尖峰态，即其分布曲线比正态分布曲线更尖峭。"
    else:
        description = f"{value_col_name}呈现低峰态，即其分布曲线比正态分布曲线更平坦。"
    return ins_type, ins_score, description


def output_insight(ins_type, ins_score, ins_description):
    global has_insight
    has_insight = True
    print("Insight计算结果如下：")
    print("类型: ", ins_type)
    print("得分: ", ins_score)
    print(f"描述:  {ins_description}\n")


def calc_insight(scope_data):
    ins_type = ''
    ins_score = 0
    ins_description = ""

    if check_is_temporal(scope_data):
        ins_type, ins_score, ins_description = calc_shape_insight(scope_data)
        if ins_score > 0:
            output_insight(ins_type, ins_score, ins_description)
        ins_type, ins_score, ins_description = calc_outlier_temporal(scope_data)
        if ins_score > 0:
            output_insight(ins_type, ins_score, ins_description)
    else:
        ins_type, ins_score, ins_description = calc_point_insight(scope_data)
        if ins_score > 0:
            output_insight(ins_type, ins_score, ins_description)
        ins_type, ins_score, ins_description = calc_outlier(scope_data)
        # if ins_score > 0:
        #     output_insight(ins_type, ins_score, ins_description)
        ins_type, ins_score, ins_description = calc_distribution_insight(scope_data)
        if ins_score > 0:
            output_insight(ins_type, ins_score, ins_description)


if __name__ == '__main__':
    df = pd.read_excel(file_path)
    calc_insight(df)
    if not has_insight:
        print("该数据中未找到insight。")
