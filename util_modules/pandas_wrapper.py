# -*- coding: utf-8 -*-

from util_func import *
import pandas as pd
import numpy as np
import os
import ipdb


def pdPickRowsByIndexKeywords(df, keywords):
    if df is None or keywords is None:
        return None

    rows = []
    for index in df.index:
        for keyword in keywords:
            if not index.find(keyword) == -1:
                rows.append(index)
    return rows


def pdColAsIndex(df, col):
    if df is None or col is None:
        return df

    if not col in list(df.columns):
        return df
    df = df.set_index(col)

    return df


def str_to_date(df, cols, errors="coerce"):
    if df is None or cols is None:
        return df
    
    for col in cols:
        df[col] = pd.to_datetime(df[col], errors=errors)

    return df


def sort_bycols(df, cols):
    if df is None or cols is None:
        return None

    df = df.sort_values(by=cols)

    return df


def erase_repeat_rows(df, cols=None, keep="first"):
    if df is None:
        return None

    cols = df.columns if cols is None else cols
    ret = df.drop_duplicates(cols)
    
    return ret


def rename_cols(df, src_cols, dst_cols):
    if df is None or src_cols is None or dst_cols is None:
        return df
    if len(src_cols) != len(dst_cols):
        print "len of src_cols and dst_cols must be same"
        return df

    col_map = {}
    for i in range(len(src_cols)):
        if not src_cols[i] in list(df.columns):
            continue
        col_map[src_cols[i]] = dst_cols[i]

    df.rename(columns=col_map, inplace=True)

    return df


def copy_cols(df, src_cols, dst_cols):
    if df is None or src_cols is None or dst_cols is None:
        return df
    if len(src_cols) != len(dst_cols):
        print "len of src_cols and dst_cols must be same"
        return df
    
    df[dst_cols] = df[src_cols]

    return df

def change_df_dtype(df, dtype):
    if df is None or dtype is None:
        return df

    if not str(dtype).find("int") == -1:
        df = df.astype("float").astype(dtype)
    else:
        df = df.astype(dtype)

    return df


def change_df_dtype_by_col(df, cols, dtypes):
    if df is None or cols is None or dtypes is None \
            or len(cols) != len(dtypes):
        return df
    
    cols, indexes = verifyCols(df, cols)
    dtypes = [dtypes[i] for i in indexes]

    for i in range(len(cols)):
        col = cols[i]
        dtype = dtypes[i]
        null_rows = df[col].isnull()
        nonnull_rows = df[col].notnull()
        if not str(dtype).find("int") == -1:
            df.loc[nonnull_rows, col] = df.loc[nonnull_rows, col]\
                    .astype("float").astype(dtype)
        else:
            df.loc[nonnull_rows, col] = df.loc[nonnull_rows, col].astype(dtype)

    return df


def read_pandas(path, format="csv", erase_strs=None, dtype=object):
    if not os.path.exists(path):
        print "{} not exist".format(path)
        return None
    
    ret = None
    
    if format == "csv":
        ret = pd.read_csv(path, dtype=dtype)
    elif format == "excel":
        ret = pd.read_excel(path, dtype=dtype)
    elif format == "hdf5":
        ret = pd.read_hdf(path, dtype=dtype)
    elif format == "txt":
        lines = read_lines(path, erase_strs=erase_strs)
        arr = []
        cols, parter = split_line(lines[0])
        for line in lines[1:]:
            contents, parter = split_line(line)
            arr.append(contents)
        arr = np.asarray(arr)
        ret = pd.DataFrame(columns=cols, data=arr, dtype=dtype)
    else:
        print "only csv excel or hdf5 format is supported!"
        return None

    return ret


def write_pandas(path, df, format="csv", hdf5_key="df"):
    if not format in ["csv", "excel", "hdf5"]:
        print "only csv excel or hdf5 format is supported!"

    if path is None or df is None:
        return

    try_make_dir(os.path.dirname(path))
    
    if format == "csv":
        df.to_csv(path)
    elif format == "excel":
        df.to_excel(path, sheet_name="Sheet1")
    elif format == "hdf5":
        df.to_hdf(path, hdf5_key)


def dict_to_df(data_dict, col_key, col_val):
    if data_dict is None or col_key is None or col_val is None:
        return None

    data_key, data_val = [], []
    for key, val in data_dict.items():
        data_key.append(key)
        data_val.append(val)

    df = pd.DataFrame(columns=[col_key, col_val])
    df[col_key] = data_key
    df[col_val] = data_val

    return df


def verifyCols(df, cols):
    if df is None or cols is None: 
        return None

    dst_cols = []
    idxes = []
    df_cols = df.columns
    for i, col in enumerate(cols):
        if col in df_cols:
            dst_cols.append(col)
            idxes.append(i)
        else:
            print "verifyCols() => {} missing".format(col)
    
    return dst_cols, idxes


def pick_cols(df, cols, drop_repeat_cols=False):
    if df is None or cols is None:
        return None

    if drop_repeat_cols:
        cols = list(set(cols))
    
    cols, _ = verifyCols(df, cols)

    return df[cols]


def cols_static(df, cols):
    if df is None:
        return None

    cols = df.columns if cols is None else cols
    all_statics = {}
    for col in cols:
        groups = df.groupby(col).groups
        col_stat = {}
        for val in groups.keys():
            col_stat[val] = len(groups[val])
        all_statics[col] = col_stat

    return all_statics


def colValueStatics(df, col):
    if df is None or col is None:
        return None

    groups = df.groupby(col).groups
    all_vals = list(groups.keys())

    return all_vals


def row_opts(df, cols, opts, new_cols, only_new_cols=True):
    if df is None or cols is None or opts is None or new_cols is None:
        return None

    for i, opt in enumerate(opts):
        new_col = new_cols[i]
        if opt == "sum":
            df[new_col] = df[cols].apply(lambda x: x.sum(), axis=1)
        elif opt == "mean":
            df[new_col] = df[cols].apply(lambda x: x.mean(), axis=1)
        elif opt == "max":
            df[new_col] = df[cols].apply(lambda x: x.max(), axis=1)
        elif opt == "min":
            df[new_col] = df[cols].apply(lambda x: x.min(), axis=1)
        else:
            print "Invalid option: {}".format(opt)
            return None

    ret = df[new_cols] if only_new_cols else df

    return ret


def col_group_opts(df, cols_key, col_val, opts, new_cols, only_new_cols=True):
    if df is None or cols_key is None or col_val is None or opts is None:
        return None

    df = drop_null_rows_any(df, cols_key + [col_val])
    df[col_val] = df[col_val].astype("float")
    ret = df
    new_cols_valid = []
    for i in range(len(opts)):
        opt = opts[i]
        new_col = new_cols[i]
        if opt == "sum":
            df_sum = df.groupby(by=cols_key, as_index=False)[col_val].sum()
            rename_cols(df_sum, [col_val], [new_col])
            ret = map_by_cols(ret, df_sum, cols_key)
            new_cols_valid.append(new_col)
        elif opt == "mean":
            df_mean = df.groupby(by=cols_key, as_index=False)[col_val].mean()
            rename_cols(df_mean, [col_val], [new_col])
            ret = map_by_cols(ret, df_mean, cols_key)
            new_cols_valid.append(new_col)
        elif opt == "max":
            df_max = df.groupby(by=cols_key, as_index=False)[col_val].max()
            rename_cols(df_max, [col_val], [new_col])
            ret = map_by_cols(ret, df_max, cols_key)
            new_cols_valid.append(new_col)
        elif opt == "min":
            df_min = df.groupby(by=cols_key, as_index=False)[col_val].min()
            rename_cols(df_min, [col_val], [new_col])
            ret = map_by_cols(ret, df_min, cols_key)
            new_cols_valid.append(new_col)
        else:
            continue
        
    ret = ret[cols_key + new_cols_valid] if only_new_cols else ret

    return ret


def twostage_static(df, col1, col2):
    if df is None or col1 is None or col2 is None:
        return None
    
    df = pick_cols(df, [col1, col2])
    # drop null
    df = df.dropna(axis=0, how="any")
    
    static = {}
    for i in df.index:
        key1 = df.loc[i, col1]
        key2 = df.loc[i, col2]
        if not static.has_key(key1):
            static[key1] = {}
        if not static[key1].has_key(key2):
            static[key1][key2] = 1
        else:
            static[key1][key2] += 1
    
    return static


def twostage_sum(df, col1, col2):
    if df is None or col1 is None or col2 is None:
        return None

    df = df.pick_cols(df, [col1, col2])
    # drop null
    df = df.dropna(axis=0, how="any")

    ret = {}
    for i in df.index:
        key = df.loc[i, col1]
        if not ret.has_key(key):
            ret[key] = df.loc[i, col2]
        else:
            ret[key] += df.loc[i, col2]
    
    return ret


def pick_rows_by_index_keywords(df, keywords):
    all_idxes = list(df.index)
    pick_rows = []
    for idx in all_idxes:
        for key in keywords:
            if idx.find(key) != -1:
                pick_rows.append(idx)
    return df.loc[pick_rows, :]


def pick_rows_byval(df, col, vals):
    if df is None or col is None or vals is None:
        return None

    ret = None
    for i, val in enumerate(vals):
        tmp = df.loc[df.loc[:, col] == val, :]
        if i == 0:
            ret = tmp
        else:
            ret = pd.concat([ret, tmp], axis=0)

    return ret


def drop_rows_with_values(df, col, values):
    if df is None or col is None or values is None:
        return df

    for val in values:
        df = df.drop(df.loc[df[col]==val, :].index)

    return df


def drop_cols(df, cols):
    if df is None or cols is None:
        return df

    df = df.drop(cols, axis=1)

    return df


def drop_null_rows_any(df, reference_cols=None):
    if df is None:
        return None

    reference_cols = df.columns if reference_cols is None else reference_cols
    df_tmp = pick_cols(df, reference_cols)
    df_tmp = df_tmp.dropna(axis=0, how="any")
    df = df.loc[df_tmp.index, :]

    return df


def replace_as_null(df, strs):
    ret = df
    if df is None:
        return ret
    for one in strs:
        ret = ret.replace(one, np.nan)
    return ret


def fill_null_const(df, val, cols=None):
    ret = df
    if val is None or cols is None:
        return df
    else:
        ret[cols] = ret[cols].fillna(val)
    return ret


def fill_null_mean(df, cols=None, dtype=float):
    if df is None:
        return df

    cols = df.columns.values.tolist() if cols is None else cols
    for col in cols:
        mean = df[col].mean()
        mean = change_dtype(mean, dtype)
        df[col] = df[col].fillna(mean)
    
    return df


def fillNullColVary(df, cols, vals, dtypes, cols_isfunc=None):
    if df is None or cols is None or vals is None:
        print "fillNullColVary()--> Invalid inputs"
        return df
    if not len(cols) == len(vals):
        print "fillNullColVary()--> Len of cols and vals must be equal"
        return df

    cols, indexes = verifyCols(df, cols)
    vals = [vals[i] for i in indexes]
    dtypes = [dtypes[i] for i in indexes]
    if not cols_isfunc is None:
        cols_isfunc = [cols_isfunc[i] for i in indexes]

    ret = df

    # get const and functional cols
    func_cols = []
    func_names = []
    const_cols = []
    const_vals = []
    const_indexes = []
    func_indexes = []
    if cols_isfunc is None:
        const_cols = cols
        const_vals = vals
        const_indexes = list(range(len(cols)))
        func_indexes = []
    else:
        for i in range(len(cols_isfunc)):
            if str(cols_isfunc[i]) == "1":
                func_cols.append(cols[i])
                func_names.append(vals[i])
                func_indexes.append(i)
            else:
                const_cols.append(cols[i])
                const_vals.append(vals[i])
                const_indexes.append(i)
    
    # process const cols
    print "fillNullColVary() => Processing const cols"
    for i in range(len(const_cols)):
        col_name = const_cols[i]
        val = const_vals[i]
        ret[col_name] = ret[col_name].fillna(val)

    # process functional cols
    print "fillNullColVary() => Processing functional cols"
    for i in range(len(func_cols)):
        col = func_cols[i]
        cmd = "fill_null_{}(df, cols=[col], dtype=\"{}\")".format(
                func_names[i], dtypes[func_indexes[i]])
        eval(cmd)

    return ret


def add_null_flag_cols(df, cols=None, backend="_flag"):
    if df is None:
        return None, None

    cols = df.columns if cols is None else cols
    add_cols = []
    for col in cols:
        add_col = col + backend
        df[add_col] = 0
        df.loc[df[col].isnull(), add_col] = 1
        add_cols.append(add_col)

    return df, add_cols


def pdDropColsByNaRate(df, thr, cols=None):
    if df is None or thr > 1.0 or thr < 0.0:
        return df

    cols = df.columns if cols is None else cols
    num_rows = df.shape[0]
    to_drop = []
    for col in cols:
        num_na = sum(df.loc[:, col].isnull())
        r = float(num_na) / num_rows
        if r > thr:
            to_drop.append(col)
    df = drop_cols(df, to_drop)
    print "{} dropped".format(to_drop)
    rest_cols = list_sub(cols, to_drop)

    return df, to_drop, rest_cols


def colNaRate(X):
    '''
    dataframe每列的缺失率
    X: DataFrame的数据
    R:各列的缺失率
    '''
    R=pd.DataFrame() #存结果
    rat=[]
    ratnames=[]
    m,n=X.shape
    for i in range(n):   
        n0=sum(X.ix[:,i].isnull())
        r=round(n0*1.0/m,4) #四舍五入保留4位
        ##rat.append(r) #小数形式
        rat.append('%.2f%%'%(r*100)) #百分比字符串形式     
        ratnames.append(X.columns[i])  
    R['names']=ratnames
    R['null_rate']=rat
    return R 


def rowNaRate(X):
    '''
    dataframe每行的缺失率
    X: DataFrame的数据
    R:每行的缺失率
    '''
    R=pd.DataFrame()
    rat=[]
    rownames=[]
    m,n=X.shape
    for i in range(m):
        #当X是从原始数据中抽取的，index不是0-m,不能直接用i
        n0=sum(X.ix[X.index[i],:].isnull())
        r=round(n0*1.0/n,4)
        rat.append(r) #小数形式
        ##rat.append('%.2f%%'%(r*100)) #百分比字符串形式   
        rownames.append(X.index[i])  
    R['rownames']=rownames
    R['null_rate']=rat
    return R


def map_by_cols(df1, df2, map_cols, how="left"):
    if map_cols is None:
        return None
    
    for col in map_cols:
        if not col in df1.columns or not col in df2.columns:
            return None
    
    ret = df1.merge(df2, on=map_cols, how="left")
    
    return ret


def splitByCol(df, col, w1, w2):
    if df is None or w1 is None or w2 is None:
        return None, None
    if w1 < 0 or w2 < 0:
        print "Invalid weight"
        return None, None
    
    # erase repeated
    df = erase_repeat_rows(df, cols=[erase_repeat_bycol], keep="first")

    # modify weights
    w1 = float(w1) / (w1 + w2)
    w2 = float(w2) / (w1 + w2)

    # 


if __name__ == "__main__":
    df = read_pandas("data/test_pandas.csv", format="csv")
    print "ori_df: ", df["card_num"]
    df = replace_as_null(df, ["\N"])
    df = fill_null_mean(df, cols=["card_num"])
    print "df: ", df[["card_num"]]
