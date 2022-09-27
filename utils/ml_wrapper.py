# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')
from base_py_func import *
from pandas_wrapper import *
import pandas as pd
import numpy as np
from sklearn.metrics import roc_curve,auc
from sklearn import cross_validation,metrics
import matplotlib.pyplot as plt
import math
import ipdb 



def mapValues(df, cols, cls_map, null_key="missing"):
    for col in cols:
        if not col in df.columns or not col in cls_map.keys():
            continue
        
        tmp_map = cls_map[col]
        all_vals = colValueStatics(df, col)
        for one  in all_vals:
            if not one in tmp_map.keys():
                df[col] = df[col].replace(null_key, tmp_map[null_key])

        for src, dst in tmp_map.items():
            df[col] = df[col].replace(src, dst)

    return df


def map_class_id(df, cols=None, add_cols=False, new_col_backend="_tmp"):
    if df is None:
        return None, None

    ret = df
    cols = df.columns if cols is None else cols
    cols, _ = verifyCols(df, cols)
    cls_map = {}
    for col in cols:
        cat_num = ret.groupby(col).size().shape[0]
        new_col = col + new_col_backend
        ret[new_col] = ret[col].astype("category")
        ret[new_col].cat.categories = list(range(cat_num))
        
        # get class map
        tmp_map = {}
        for i in ret.index:
            tmp_map[ret.loc[i, col]] = ret.loc[i, new_col]
        cls_map[col] = tmp_map

        if not add_cols:
            # erase move new col to old
            ret[col] = ret[new_col]
            ret = ret.drop(new_col, axis=1)

    return ret, cls_map


def onehot(df, cols, drop_ori_cols=False, check_cols=None):
    if df is None or cols is None:
        return df

    cols, _ = verifyCols(df, cols)

    new_cols = []
    for col in cols:
        dum = pd.get_dummies(df[col], prefix=col)
        df = pd.concat([df, dum], axis=1)
        new_cols += list(dum.columns)

    if not check_cols is None:
        add_cols = list_sub(check_cols, new_cols)
        for col in add_cols:
            df[col] = 0
        new_cols += add_cols

    if drop_ori_cols:
        df = drop_cols(df, cols)

    return df, new_cols
        

def col_normalization(df, cols, dtypes, auto_bound=True):
    if df is None or cols is None or dtypes is None:
        return df

    cols, indexes = verifyCols(df, cols)
    dtypes = [dtypes[i] for i in indexes]

    boundary = {}
    for i in range(len(cols)):
        col = cols[i]
        dtype = dtypes[i]
        col_data = df[col].astype(float)
        mean = col_data.mean()
        std = col_data.std()
        if auto_bound:
            upper = min(mean + 3 * std, df[col].max())
            lower = max(mean - 3 * std, df[col].min())
            df.loc[df.loc[:, col] < lower, col] = lower
            df.loc[df.loc[:, col] > upper, col] = upper
        else:
            upper = df[col].max()
            lower = df[col].min()
        df[col] = (df[col] - lower) / (upper - lower)
        
        if auto_bound:
            boundary[col] = [lower, upper]
        
    return df, boundary


def updown_sample_bycol(df, col, num):
    if df is None or col is None or num is None or num <= 0:
        return None

    ret = None
    src_num = df.shape[0]
    if num > src_num:
        # up sample
        step = int(math.floor(float(num) / src_num))
        for i in range(step):
            ret = pd.concat([ret, df], axis=0)
        rest_num = num - src_num * step
        ret = pd.concat([ret, df.iloc[:rest_num]], axis=0)
    elif num < src_num:
        # down sample
        step = int(math.floor(float(src_num) / num))
        ret = df.iloc[range(0, src_num, step)]
        ret = ret.iloc[:num]

    return ret


def sample_balance(df, target_col, weights=None, multiply=None):
    if df is None or target_col is None:
        return None

    src_statics = cols_static(df, [target_col])[target_col]
    print "src statics: ", src_statics
    if weights is None:
        weights = {}
        for key in src_statics.keys():
            weights[key] = 1
    if len(weights.keys()) != len(src_statics.keys()):
        print "key number of weights and src_statics must be same!"
        return None

    ratios = {}
    for key in src_statics.keys():
        ratios[key] = float(src_statics[key]) / weights[key]
    key_minratio, min_ratio = dict_min(ratios)

    if multiply is None:
        multiply = ratios[key_minratio]

    ret = None
    for i, val in enumerate(weights.keys()):
        num = int(math.floor(weights[val] * multiply))
        df_tmp = df.loc[df[target_col]==val, :]
        df_tmp = updown_sample_bycol(df_tmp, target_col, num)
        ret = pd.concat([ret, df_tmp], axis=0)

    dst_statics = cols_static(ret, [target_col])[target_col]
    print "dst_statics: ", dst_statics

    return ret


def strKmeans(dat,x,y,nclus,seed=123):
    '''
    对类别型feature进行KMeans聚类
    分别统计feature的n个取值下的总人数count及坏用户占比badr,
    按[count,badr]构成n*2列矩阵，对新构成的n个样本进行聚类
    input:
    dat:dataframe数据集
    x:待聚类的feature名称，dat[x]含n个取值
    y:目标变量的名称
    nclus:聚类簇数
    seed:kmeans中的random_state随机选取种子
    return: 
    kcentroids:聚类中心点
    km_mat: n个新样本聚类结果
    kmgroup:每个簇对应的x的取值
    '''
    from sklearn.cluster import KMeans
    uniq_feat=list(np.unique(dat[x]))
    count=[]
    badr=[]
    for f in uniq_feat: 
        #f下的样本的y
        y0=dat[y][dat[x]==f]
        count0=len(y0)            #总数
        badr0=round(sum(y0==1)*1.0/count0,4) #坏账比率    
        count.append(count0)
        badr.append(badr0)
    mat=np.array([count,badr]).T #每列表示一个属性
    #归一化
    mat_norm=mmScaler(mat)  #array
    
    #kmeans聚类
    kmodel=KMeans(n_clusters=nclus,random_state=seed).fit(mat_norm) #random_state设定一个整数，每次种子点不变
    kclus=kmodel.labels_ #每个样本的聚类标签0~nclus
    km_mat=pd.DataFrame(mat_norm,columns=['count','badr'],index=uniq_feat)
    km_mat['clusters']=kclus 
    kcentroids=pd.DataFrame(kmodel.cluster_centers_,columns=['count','badr']) #聚类中心
    
    #存聚类结果
    kmgroup=pd.DataFrame()
    kmg=[]
    clus=[]
    for i in range(nclus):
        km_list=list(km_mat.index[kclus==i])
        kmg.append(km_list)
        clus.append(i)
    kmgroup['clusters']=clus
    kmgroup[x]=kmg 
    return kcentroids,km_mat,kmgroup


'''
说明：
如果y_prepro是预测的坏人概率，threshmethod为gt,概率越高越可能成为坏人（1表示）
如果y_pro传入的是评分（分越低越坏），threshmethod为lt, 分越低越可能成为坏人（1表示）
'''
def rocCurve(y,y_prepro,figSavePath, threshmethod='gt',figSave=False):
    '''
    绘制ROC曲线（函数roc_curve是按照y_prepro降序）
    y:样本集的实际标签，1维array或Series
    y_prepro:模型预测为1的概率,1维array。通过clf.predict_proba(X)[:,1]得到
            :或为某种决策得到的结果，比如score.
             若score大于某个阈值定义为1，那么这里的y_prepro即为score；若score小于某阈值定义为1，那么这里的y_prepro即为-score
    threshmethod:'gt'大于某个阈值预测为1(roc_curve函数的默认方式y_prepro有高到低排序)，'lt' 小于某个阈值预测为1
    figname:模型名称描述，如 'GBDT_train_roc'，默认为空串。为了标注显示
    figSavePath:保存路径 
    
    '''   
#  #  y=np.array(y)  #若为series,则转为array
    
    if threshmethod=='gt':
        y_prepro=y_prepro
    elif threshmethod=='lt':
        y_prepro=-y_prepro
    else:
        print '**********  warning: **********'
        print 'please input the right threshmethod!'
    
    fpr,tpr,thresholds=roc_curve(y,y_prepro)
    roc_auc=auc(fpr,tpr)

    plt.figure()
    plt.plot(fpr,tpr,lw=1.1,label='AUC=%.4f'%roc_auc,color='red')
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('roc')
    plt.xlim(0,1)
    plt.ylim(-0.01,1.01)
    plt.legend(loc='lower right',fontsize=13)    
    if figSave:
        plt.savefig(figSavePath)   #savefig 在show之前
    #plt.show()
     
  
def ksCurve(g_rat_cum,b_rat_cum,figSavePath,figSave=False):
    '''
    绘制KS曲线图
    g_rat_cum: series或list, 累计好用户比率
    bad_rat_cum:series或list,累计坏用户比率
    '''
    #最前面加0,为了画图从0~1.0显示
    g=[0]
    g.extend(g_rat_cum)
    b=[0]
    b.extend(b_rat_cum)
    #ks曲线
    dif=list(pd.Series(b)-pd.Series(g))
    max_idx=np.argmax(dif)
    
    plt.figure()
    x=range(len(g)) #横轴
    plt.plot(x,g,lw=1.1,color='green',label='good')
    plt.plot(x,b,lw=1.1,color='red',label='bad')
    plt.plot(x,dif,lw=1.1,color='blue',label='ks_curve')
    
    #找ks点所在的位置，并标注ks
    plt.plot(max_idx,dif[max_idx],'ks') #最大值点 绘制形状黑色方形
    #s标注，xy位置，xytext：标注的位置
    plt.annotate(s='ks:'+str(dif[max_idx]),xy=(max_idx,dif[max_idx]),
            xytext=(max_idx+0.3,dif[max_idx]+0.02))
    
    plt.xlabel('group')
    plt.ylabel('cum.rate%')
    plt.title('ks')
    plt.xlim(0,10)
    plt.ylim(-0.05,1.05)
    plt.legend(loc='upper left',fontsize=13)
    if figSave:
        plt.savefig(figSavePath)   #savefig 在show之前
    #plt.show()   
    
    return dif[max_idx]

'''
说明：
如果y_pro是预测的坏人概率，则降序排序分组
如果y_pro传入的是评分，分越低越坏，则升序排序
'''
def ksValue(y,y_pro,n=10,ascending=False):
    '''
    求ks统计量及ks值
    input:
    y:数据集的实际目标变量， list 或 1维array 或series
    y_pro:数据集的预测为1的概率 或者某决策函数得到的值比如分值, list 或 1维array 或series
    n:分组数,默认为10
    ascending:排序方式，默认False降序对于（预测为1的概率）
    return:
    ks_stat:按照预测违约率降序后分n组后的统计信息
    ks:ks值
    '''    
#   # y=np.array(y)
    if ascending==False:
        #按照概率 降序后的目标变量 y[ixsort]
        ixsort=np.argsort(-y_pro) #索引 
    else:
        ixsort=np.argsort(y_pro) #升序 
        
    #分组规模:n组中每组人数
    cnt=int(1.0*len(y)/n) #平均每组人数
    gr_cnt=[cnt]*(n-1) 
    gr_cnt.append(len(y)-cnt*(n-1))
    
    bad_cnt=[] #n组坏人数
    good_cnt=[] #n组好人数
    for i in range(n):    
        idx=ixsort[cnt*i:cnt*(i+1)]
        bad_i=sum(y[idx]) #第i组坏人数 ；降序后的目标变量y[idx]
        good_i=cnt-bad_i   
        bad_cnt.append(bad_i)    
        good_cnt.append(good_i)
    ks_stat=pd.DataFrame()
    ks_stat['cnt']=gr_cnt
    ks_stat['bad_cnt']=bad_cnt
    ks_stat['bad_rat']=ks_stat['bad_cnt']*1.0/sum(ks_stat['bad_cnt'])
    ks_stat['bad_rat_cum']=ks_stat['bad_rat'].cumsum()
    ks_stat['good_cnt']=good_cnt
    ks_stat['good_rat']=ks_stat['good_cnt']*1.0/sum(ks_stat['good_cnt'])
    ks_stat['good_rat']
    ks_stat['good_rat_cum']=ks_stat['good_rat'].cumsum()    
    #ks值
    ks=max(ks_stat['bad_rat_cum']-ks_stat['good_rat_cum'])
    return ks,ks_stat


def modelCv(alg,train_X,train_y,cv_folds=5,printCvScore=True):  
    '''
    交叉验证
    alg:算法模型
    train_X:特征
    train_y:目标y
    '''
    alg.fit(train_X,train_y)    
    cv_score=cross_validation.cross_val_score(alg,train_X,train_y,cv=cv_folds,scoring='roc_auc')
    print"CV score: mean - %.7g | std -%.7g |min -%.7g | max -%.7g"%(np.mean(cv_score),np.std(cv_score),np.min(cv_score),np.max(cv_score)) 
    return cv_score
