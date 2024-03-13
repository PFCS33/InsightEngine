import numpy as np
import pandas as pd
from scipy.stats import linregress, pearsonr, skewtest, kurtosistest, skew, kurtosis, zscore, kstest

text_data = """
Company,Location,Year,Sale
Nintendo,Europe,2013,950
Nintendo,Europe,2014,951
Nintendo,Europe,2015,951
Nintendo,Europe,2016,952
Nintendo,Europe,2017,953
Nintendo,Europe,2018,954
Nintendo,Europe,2019,952
Nintendo,Europe,2020,951
Nintendo,Japan,2013,952
Nintendo,Japan,2014,953
Nintendo,Japan,2015,955
Nintendo,Japan,2016,956
Nintendo,Japan,2017,956
Nintendo,Japan,2018,957
Nintendo,Japan,2019,951
Nintendo,Japan,2020,954
Nintendo,North America,2017,954
Nintendo,North America,2018,953
Nintendo,North America,2019,952
Nintendo,North America,2020,956
Nintendo,Other,2013,954
Nintendo,Other,2014,956
Nintendo,Other,2015,954
Nintendo,Other,2017,957
Nintendo,Other,2018,959
Nintendo,Other,2020,952
"""

data = [dict(zip(text_data.strip().split(','), line.strip().split(','))) for line in text_data.strip().split('\n')[1:]]
d = pd.DataFrame(data)



def calc_distribution_insight(d):
    d_value = d.iloc[:, -1].values
    # remove all zeros when calculating distribution insight
    d_value = d_value[d_value != 0]
    d_value = d_value.astype(float)
    _, p_s = skewtest(d_value)
    s = skew(d_value)
    _, p_k = kurtosistest(d_value)
    k = kurtosis(d_value)
    a = d_value.std()
    b = d_value.mean()
    e = abs(a/b)         # evenness
    # _, p_e = kstest(d_value, 'uniform', args=(0, 1))
    has_skew = p_s < 0.03 and abs(s) > 2
    has_kurtosis = p_k < 0.05 and abs(k) > 3 and abs(s) < 3
    has_evenness = e < 0.1
    print(has_evenness)


calc_distribution_insight(d)
