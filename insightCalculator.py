import os

import numpy as np
import pandas as pd
from scipy.stats import linregress, pearsonr, skewtest, kurtosistest, skew, kurtosis, zscore, kstest


def calc_point_insight(d, no_aggr):
    ins_type = ''
    ins_score = 0
    description = ""

    # sort according to the last value, sales in this case
    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    # the value column
    sorted_values = sorted_d.iloc[:, -1].values

    # if len(sorted_values) < 3 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0 or no_aggr:
    if len(sorted_values) < 3 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0:
        return ins_type, ins_score, description  # too few data or all zero

    if dominance_detection(sorted_values):
        ins_type = 'dominance'
        ins_score = sorted_values[0] / np.sum(sorted_values)
        # ins_score = 0.4 * (ins_score - 0.5) + 0.6     # enlarge to 0.6
        min_score = 0.5
        max_score = 1.0
        ins_score = (ins_score - min_score) / (max_score - min_score)      # Normalize
        description = generate_dominance_description(sorted_d)
    elif top2_detection(sorted_values):
        ins_type = 'top2'
        ins_score = (sorted_values[0] + sorted_values[1]) / np.sum(sorted_values)
        min_score = 0.6
        max_score = 1.0
        ins_score = (ins_score - min_score) / (max_score - min_score)        # Normalize
        description = generate_top2_description(sorted_d)

    return ins_type, ins_score, description


def calc_outlier(d):
    ins_type = ''
    ins_score = 0
    description = ""
    insights = []

    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    sorted_values = sorted_d.iloc[:, -1].values

    if len(sorted_values) < 8 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0:
        return insights  # too few data or all zero

    result = outlier_detection(sorted_values, 2)
    if result:
        outliers, lower_threshold, upper_threshold = result
        if len(outliers) != 0 and len(outliers) < 3:
            ins_type = 'outlier'
            for outlier in outliers:
                index = np.where(sorted_values == outlier)[0]
                if outlier < lower_threshold:
                    ins_score = (outlier - sorted_values.mean()) / sorted_values.std()
                    ins_score = -ins_score
                    # ins_score = min(ins_score, 3)  # Cap at 3
                    # ins_score = ins_score / 3  # Normalize to [0, 1]
                    min_score = 0.6
                    max_score = 3.7
                    ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
                    ins_score = max(0, min(1, ins_score))
                    description = generate_outlier_description(sorted_d, index, 'lower')
                    insights.append({"ins_type": ins_type, "ins_score": ins_score, "ins_description": description})
                elif outlier > upper_threshold:
                    ins_score = (outlier - sorted_values.mean()) / sorted_values.std()
                    min_score = 0.6
                    max_score = 3.7
                    ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
                    ins_score = max(0, min(1, ins_score))
                    description = generate_outlier_description(sorted_d, index, 'higher')
                    insights.append({"ins_type": ins_type, "ins_score": ins_score, "ins_description": description})

            return insights
        else:
            # else no outlier
            return insights
    else:
        # else no outlier
        return insights


def calc_outlier_temporal(d):
    ins_type = ''
    ins_score = 0
    description = ""
    insights = []

    sorted_d = d.sort_values(by=d.columns[-1], ascending=False)
    sorted_values = sorted_d.iloc[:, -1].values

    if len(sorted_values) < 5 or np.sum(sorted_values) == 0 or np.std(sorted_values) == 0:
        return insights  # too few data or all zero

    result = outlier_detection(sorted_values, 1.5)
    if result:
        outliers, lower_threshold, upper_threshold = result
        if len(outliers) != 0 and len(outliers) < 3:
            ins_type = 'outlier-temporal'
            # max_ins_score = 0
            for outlier in outliers:
                index = np.where(sorted_values == outlier)[0]
                if outlier < lower_threshold:
                    ins_score = (sorted_values[-1] - sorted_values.mean()) / sorted_values.std()
                    ins_score = -ins_score
                    # ins_score = min(ins_score, 3)  # Cap at 3
                    # ins_score = ins_score / 3  # Normalize to [0, 1]
                    min_score = 0.6
                    max_score = 3.7
                    ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
                    ins_score = max(0, min(1, ins_score))
                    description = generate_outlier_description(sorted_d, index, 'lower')
                    insights.append({"ins_type": ins_type, "ins_score": ins_score, "ins_description": description})
                elif outlier > upper_threshold:
                    ins_score = (sorted_values[0] - sorted_values.mean()) / sorted_values.std()
                    min_score = 0.6
                    max_score = 3.7
                    ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
                    ins_score = max(0, min(1, ins_score))
                    description = generate_outlier_description(sorted_d, index, 'higher')
                    insights.append({"ins_type": ins_type, "ins_score": ins_score, "ins_description": description})
                # if ins_score > max_ins_score:
                #     max_ins_score = ins_score
            return insights
        else:
            # else no outlier
            return insights
    else:
        # else no outlier
        return insights




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
    return f"The {value_name} of {top1_name} dominates among all {main_column_name}s."


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
    return f"The {value_name} proportion of {top1_name} and {top2_name} is significantly higher than that of other {main_column_name}s."


def outlier_detection(d, threshold=3):
    zero_count = np.sum(d == 0)
    if check_zero(d) > 0.1 or len(d) - zero_count < 4:  # too many zeros
        return False
    # d = d[d != 0]   # remove zero
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
    description += f"The {value_name} of {main_column_name} {main_column_index_value} "
    if data.shape[1] > 2:
        for col_index in range(1, data.shape[1] - 1):
            column_name = data.columns[col_index]
            index_value = data.iloc[index, col_index].values[0]
            description += f"of {column_name} {index_value} "
    # print(description)
    description += "is an outlier, which is significantly "
    description += "lower " if outlier_type == 'lower' else "higher "
    description += f"than the normal {value_name} of other {main_column_name}s"
    # print(description)
    if data.shape[1] > 2:
        description += " in the corresponding "
        for col_index in range(1, data.shape[1] - 2):
            column_name = data.columns[col_index]
            description += f"{column_name}s, "
        column_name = data.columns[data.shape[1] - 2]
        description += f"{column_name}s"
    description += "."

    return description


def z_score_outlier_detection(data, threshold=3.5):
    """
    使用Z-score方法进行离群值检测
    :param data: 数据集
    :param threshold: Z-score阈值，默认为3
    :return: 离群值的索引
    """
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return []
    else:
        z_scores = [(x - mean) / std for x in data]
        return np.where(np.abs(z_scores) > threshold)[0]


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
        ins_type = 'trend'
        ins_score = trend
        min_score = 0.7
        max_score = 1.0
        ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
        description = f"{value_name}s exhibit a clear {trend_direction} trend over the {main_col_name}s from {start_year} to {end_year}."

    return ins_type, ins_score, description


def test_slope(d):
    if np.std(d) == 0:  # all the same, no slope
        return "no_slope", 0
    # Fit X to a line by linear regression
    _, _, r_value, p_value, _ = linregress(np.arange(len(d)), d)
    trend_direction = "upward" if r_value > 0 else "downward"
    trend_strength = r_value ** 2
    confidence = 1 - p_value
    trend = trend_strength * confidence
    return trend_direction, trend

    # # Calculate the p-value
    # n = len(d)
    # t_statistic = slope / (np.std(d) / np.sqrt(n))
    # degrees_of_freedom = n - 2
    # p_value = 2 * (1 - t.cdf(abs(t_statistic), df=degrees_of_freedom))


def check_is_temporal(data, is_month=False):
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

    if is_month:
        return True

    # for every row in column 1
    result = data.iloc[:, 0].apply(process_value)
    if result.all():
        return True
    else:
        return False

    # if data.columns[0] == 'Year':
    #     return True
    # else:
    #     return False


def check_zero(d):
    return np.sum(d == 0) / len(d)


def calc_compound_insight(d):
    ins_type = ''
    ins_score = 0
    description = ""
    if d.shape[0] <= 10 or (d.shape[0] <= 20 and not check_is_temporal(d)):
        return ins_type, ins_score, description  # too few data
    if check_zero(d.iloc[:, 0]) > 0.5 or check_zero(d.iloc[:, 1]) > 0.5:
        return ins_type, ins_score, description  # too many zero

    # calculate the relevance between 1st column and 2nd column
    corr, p_value = correlation_detection(d.iloc[:, 0], d.iloc[:, 1])
    score = corr ** 2 * (1 - p_value)
    # if check_is_temporal(d):
    #     if abs(corr) > 0.7 and p_value < 0.05:
    #         ins_score = abs(corr)
    #         ins_type = 'correlation-temporal'
    # else:   # different threshold for non-temporal data
    #     if abs(corr) > 0.75 and p_value < 0.05:
    #         ins_score = abs(corr)
    #         ins_type = 'correlation'
    if score > 0.7:
        ins_type = 'correlation-temporal' if check_is_temporal(
            d) else 'correlation'
        ins_score = score

    return ins_type, ins_score, description


def correlation_detection(x, y):
    return 0, 0
    # TODO temporal annotate in 3.21

    # if len(np.unique(x)) > 1 and len(np.unique(y)) > 1:
    #     corr_coef, p_value = pearsonr(x, y)
    # else:
    #     corr_coef = 0
    #     p_value = 1
    # return corr_coef, p_value


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
        ins_type = 'evenness'
        ins_score = 1 - e
        min_score = 0.5
        max_score = 1.0
        ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
        column_name = d.columns[0]
        description = f"The {value_col_name}s are relatively evenly distributed across different {column_name}s"
        if d.shape[1] > 2:
            for col_index in range(1, d.shape[1] - 2):
                column_name = d.columns[col_index]
                description += f", {column_name}s"
            column_name = d.columns[d.shape[1] - 2]
            description += f" and {column_name}s"
        description += "."
        return ins_type, ins_score, description

    elif d_value.shape[0] <= 20:
        return '', 0, ""

    elif d_value.shape[0] > 20:
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

    # if abs(s) >= thres_s and abs(k) < thres_k:
    #     return 'skewness', abs(s)/10
    # elif abs(s) < thres_s and abs(k) >= thres_k:
    #     return 'kurtosis', abs(k)/10
    # else:
    #     return '', 0


def set_skew(p_s, s, value_col_name):
    ins_type = 'skewness'
    ins_score = (1 - p_s) * abs(s)
    # ins_score = min(ins_score, 3.5)  # Cap at 3.5
    # ins_score = ins_score / 3.5  # Normalize to [0, 1]
    min_score = 1.94
    max_score = 3.6
    ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
    ins_score = max(0, min(1, ins_score))
    if s > 0:
        description = (f"The {value_col_name} has a positively skewed distribution, "
                       f"which means that there are more extreme {value_col_name} values "
                       "on the right side, and the distribution is skewed to the right.")
    else:
        description = (f"The {value_col_name} has a negatively skewed distribution, "
                       f"which means that there are more extreme {value_col_name} values "
                       "on the left side, and the distribution is skewed to the left.")
    return ins_type, ins_score, description


def set_kurtosis(p_k, k, value_col_name):
    ins_type = 'kurtosis'
    ins_score = (1 - p_k) * abs(k)
    # ins_score = min(ins_score, 4)  # Cap at 4
    # ins_score = ins_score / 4  # Normalize to [0, 1]
    min_score = 2.85
    max_score = 4.3
    ins_score = (ins_score - min_score) / (max_score - min_score)  # Normalize
    ins_score = max(0, min(1, ins_score))
    if k > 0:
        description = (f"The {value_col_name} exhibit leptokurtic behavior with heavy tails and a sharp peak, "
                       "indicating a distribution with positive kurtosis.")
    else:
        description = (f"The {value_col_name} exhibit platykurtic behavior with light tails and a flat peak, "
                       "indicating a distribution with negative kurtosis.")
    return ins_type, ins_score, description


def outlier_score(data_point, data):
    z_scores = zscore(data)
    min_z = np.min(z_scores)
    max_z = np.max(z_scores)
    outlier_score = (data_point - min_z) / (max_z - min_z)
    return outlier_score
