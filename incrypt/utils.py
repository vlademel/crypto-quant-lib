import datetime
import collections
import numpy as np

def to_timestamp(x):
    return datetime.datetime.fromtimestamp(x / 1000.0)

def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def string_to_datetime(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')

def numeric_list_to_sql_filter_array(list):
    return ','.join(str(x) for x in set(list))

def varchar_list_to_sql_filter_array(list):
    return ','.join("'" + str(x) + "'" for x in set(list))

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def string_to_float(s):
    try:
        value = float(s)
    except:
        value = np.nan
    return value

def string_to_int(s):
    try:
        value = int(s)
    except:
        value = None
    return value