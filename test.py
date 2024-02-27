import numpy as np
import pandas as pd
from io import StringIO
from insightCalculator import check_is_temporal, calc_point_insight, calc_outlier, calc_outlier_temporal, calc_shape_insight, calc_compound_insight, calc_distribution_insight

data = {
    'Company': ['Nintendo'] * 16,
    'Location': ['Europe', 'Europe', 'Europe', 'Europe',
                 'Japan', 'Japan', 'Japan', 'Japan',
                 'North America', 'North America', 'North America', 'North America',
                 'Other', 'Other', 'Other', 'Other'],
    'Season': ['DEC', 'JUN', 'MAR', 'SEP',
               'DEC', 'JUN', 'MAR', 'SEP',
               'DEC', 'JUN', 'MAR', 'SEP',
               'DEC', 'JUN', 'MAR', 'SEP'],
    'Sale': [100, 110, 360, 340,
             90, 100, 500, 140,
             330, 190, 850, 360,
             20, 30, 140, 40]
}



# 使用pd.read_csv读取数据为DataFrame
# df = pd.read_csv(StringIO(data))

df = pd.DataFrame(data)
print(df.columns.tolist())

ins_type = ''
ins_score = 0
ins_description = ""
if check_is_temporal(df):
    ins_type, ins_score, ins_description = calc_shape_insight(df)
    print("(Type: ", ins_type)
    print("Score: ", ins_score)
    print("Category: shape")
    print(f"Description:  {ins_description})")
    print("-------------")
    ins_type, ins_score, ins_description = calc_outlier_temporal(df)
    print("(Type: ", ins_type)
    print("Score: ", ins_score)
    print("Category: point")
    print(f"Description:  {ins_description})")
    print("-------------")
else:
    ins_type, ins_score, ins_description = calc_point_insight(df, False)
    print("(Type: ", ins_type)
    print("Score: ", ins_score)
    print("Category: point")
    print(f"Description:  {ins_description})")
    print("-------------")
    ins_type, ins_score, ins_description = calc_outlier(df)
    print("(Type: ", ins_type)
    print("Score: ", ins_score)
    print("Category: point")
    print(f"Description:  {ins_description})")
    print("-------------")

    # remove all zeros when calculating distribution insight
    scope_data = df[df != 0]
    ins_type, ins_score, ins_description = calc_distribution_insight(scope_data)
    print("(Type: ", ins_type)
    print("Score: ", ins_score)
    print("Category: shape")
    print(f"Description:  {ins_description})")
    print("-------------")




