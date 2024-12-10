# -*- coding: utf-8 -*-

from util import *
import pandas as pd
import numpy as np
import os


class PandasWrapper:
    def __init__(self):
        pass


    def pick_rows_by_index_keywords(self, df, keywords):
        if df is None or keywords is None:
            return None
    
        rows = []
        for index in df.index:
            for keyword in keywords:
                if not index.find(keyword) == -1:
                    rows.append(index)
        return rows
    
    
    def col_as_index(self, df, col):
        if df is None or col is None:
            return df
        if not col in list(df.columns):
            return df
        df = df.set_index(col)
        
        return df
    
    
    def str_to_date(self, df, cols, errors="coerce"):
        if df is None or cols is None:
            return df
        for col in cols:
            df[col] = pd.to_datetime(df[col], errors=errors)
        
        return df
    
    
    def sort_bycols(self, df, cols):
        if df is None or cols is None:
            return None
        df = df.sort_values(by=cols)
        
        return df
    
    
    def erase_repeat_rows(self, df, cols=None, keep="first"):
        if df is None:
            return None
    
        cols = df.columns if cols is None else cols
        ret = df.drop_duplicates(cols)
        
        return ret
    
    
    def rename_cols(self, df, src_cols, dst_cols):
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
    
    
    def copy_cols(self, df, src_cols, dst_cols):
        if df is None or src_cols is None or dst_cols is None:
            return df
        if len(src_cols) != len(dst_cols):
            print "len of src_cols and dst_cols must be same"
            return df
        
        df[dst_cols] = df[src_cols]
    
        return df
    
    
    def change_df_dtype(self, df, dtype):
        if df is None or dtype is None:
            return df
    
        if not str(dtype).find("int") == -1:
            df = df.astype("float").astype(dtype)
        else:
            df = df.astype(dtype)
    
        return df
    
    
    def change_df_dtype_by_col(self, df, cols, dtypes):
        if df is None or cols is None or dtypes is None \
                or len(cols) != len(dtypes):
            return df
        
        #cols, indexes = verify_cols(df, cols)
        #dtypes = [dtypes[i] for i in indexes]
    
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
    
    
    def read_pandas(self, path, format="csv", erase_strs=None, dtype=object):
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
    
    
    def write_pandas(self, path, df, format="csv", hdf5_key="df"):
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
    
    
    def dict_to_df(self, data_dict, col_key, col_val):
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
    
    
    def verify_cols(self, df, cols):
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
                print "verify_cols() => {} missing".format(col)
        
        return dst_cols, idxes
    
    
    def cols_static(self, df, cols):
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
    
    
    def col_value_statics(self, df, col):
        if df is None or col is None:
            return None
    
        groups = df.groupby(col).groups
        all_vals = list(groups.keys())
    
        return all_vals
    
    
    def row_opts(self, df, cols, opts, new_cols, only_new_cols=True):
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
    
    
    def col_group_opts(self, df, cols_key, col_val, opts, 
            new_cols, only_new_cols=True):
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
    
    
    def twostage_static(self, df, col1, col2):
        if df is None or col1 is None or col2 is None:
            return None
        
        df = df[[col1, col2]]
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
    
    
    def twostage_sum(self, df, col1, col2):
        if df is None or col1 is None or col2 is None:
            return None
    
        df = df[[col1, col2]]
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
    
    
    #def pick_rows_by_index_keywords(self, df, keywords):
    #    all_idxes = list(df.index)
    #    pick_rows = []
    #    for idx in all_idxes:
    #        for key in keywords:
    #            if idx.find(key) != -1:
    #                pick_rows.append(idx)
    #    return df.loc[pick_rows, :]
    
    
    def pick_rows_byval(self, df, col, vals):
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
    
    
    def drop_rows_with_values(self, df, col, values):
        if df is None or col is None or values is None:
            return df
    
        for val in values:
            df = df.drop(df.loc[df[col]==val, :].index)
    
        return df
    
    
    def drop_cols(self, df, cols):
        if df is None or cols is None:
            return df
    
        df = df.drop(cols, axis=1)
    
        return df
    
    
    def drop_null_rows_any(self, df, reference_cols=None):
        if df is None:
            return None
    
        reference_cols = df.columns if reference_cols is None else reference_cols
        df_tmp = df[reference_cols]
        df_tmp = df_tmp.dropna(axis=0, how="any")
        df = df.loc[df_tmp.index, :]
    
        return df
    
    
    def replace_as_null(self, df, strs):
        ret = df
        if df is None:
            return ret
        for one in strs:
            ret = ret.replace(one, np.nan)
        return ret
    
    
    def add_null_flag_cols(self, df, cols=None, backend="_null_flag"):
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
    
    
    def drop_cols_by_na_rate(self, df, thr, cols=None):
        if df is None or thr > 1.0 or thr < 0.0:
            return df
    
        cols = df.columns if cols is None else cols
        num_rows = df.shape[0]
        dropped = []
        for col in cols:
            num_na = sum(df.loc[:, col].isnull())
            r = float(num_na) / num_rows
            if r > thr:
                dropped.append(col)
        df = self.drop_cols(df, dropped)
        print "{} dropped".format(dropped)
        rest = list_sub(cols, dropped)
    
        return df, dropped, rest
    
    
    def col_na_rate(self, X):
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
    
    
    def row_na_rate(self, X):
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
    
    
    def map_by_cols(self, df1, df2, map_cols, how="left"):
        if map_cols is None:
            return None
        
        for col in map_cols:
            if not col in df1.columns or not col in df2.columns:
                return None
        
        ret = df1.merge(df2, on=map_cols, how="left")
        
        return ret
    
    
    def split_by_col(self, df, col, w1, w2):
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


if __name__ == "__main__":
    pass
