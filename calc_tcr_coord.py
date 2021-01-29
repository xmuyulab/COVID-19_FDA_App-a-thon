import pandas as pd
import numpy as np
import time
import os 
from tqdm import tqdm
import random


from sklearn import metrics, datasets, manifold
from scipy import optimize
from matplotlib import pyplot
import collections
import click



def cal_B(D):
    (n1, n2) = D.shape
    DD = np.square(D)                    # 矩阵D 所有元素平方
    Di = np.sum(DD, axis=1) / n1         # 计算dist(i.)^2
    Dj = np.sum(DD, axis=0) / n1         # 计算dist(.j)^2
    Dij = np.sum(DD) / (n1 ** 2)         # 计算dist(ij)^2
    B = np.zeros((n1, n1))
    for i in range(n1):
        for j in range(n2):
            B[i, j] = (Dij + DD[i, j] - Di[i] - Dj[j]) / (-2)   # 计算b(ij)
    return B

def MDS(data, n=2):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(t)
    B = cal_B(data)
    Be, Bv = np.linalg.eigh(B)             # Be矩阵B的特征值，Bv归一化的特征向量
    # print numpy.sum(B-numpy.dot(numpy.dot(Bv,numpy.diag(Be)),Bv.T))
    Be_sort = np.argsort(-Be)
    Be = Be[Be_sort]                          # 特征值从大到小排序
    Bv = Bv[:, Be_sort]                       # 归一化特征向量
    Bez = np.diag(Be[0:n])                 # 前n个特征值对角矩阵
    # print Bez
    Bvz = Bv[:, 0:n]                          # 前n个归一化特征向量

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(t)
    Z = np.dot(np.sqrt(Bez), Bvz.T).T
    return Z

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--tcr_dist_path',  required=True, type=click.Path(exists=True), help='TCR distance matrix')
@click.option('--filter_tcr_path', required=True, type=click.Path(exists=True), help='TCR sequence and vdj')
@click.option('--selected_tcrs_path', required=True, type=click.Path(exists=True), help='Sample massage')
@click.option('--status_path', required=True, type=click.Path(exists=True), help='Sample and Label message')
@click.option('--save_path', required=True, type=click.Path(exists=True), help='Save path')

def calc_tcr_coord(tcr_dist_path, filter_tcr_path, selected_tcrs_path, status_path, save_path):
    """
    @param tcr_dist_path: TCR distance matrix
    @param filter_tcr_path: TCR sequence and vdj
    @param selected_tcrs_path: Sample message
    @param status_path: Sample and label message
    @param save_path: TCR coordinate 
    
    """

    tcr_dist = np.loadtxt(tcr_dist_path) 

    status = pd.read_csv(status_path, sep='\t', header=None)
    status.columns = ['sample', 'label']

    filter_tcr = pd.read_csv(filter_tcr_path, sep='\t', header=None)
    filter_tcr.columns = ['V_CDR3']

    selected_tcrs = pd.read_csv(selected_tcrs_path,sep='\t')

    # 首先确定TCR与sample的关系
    _label = []
    for tcr in tqdm(selected_tcrs['V_CDR3'].tolist()):
        _label.append(tcr in filter_tcr['V_CDR3'].tolist())

    sample_message = selected_tcrs[_label]

    # 再对sample进行筛选
    _sam = []
    for samp in tqdm(sample_message['Sample'].tolist()):
        _sam.append(samp in status['sample'].tolist())

    sample_mess = sample_message[_sam]

    _sam_label = []
    for sample in tqdm(sample_mess['Sample'].tolist()):
        _sam_label.append(status[status['sample'] == sample]['label'].values[0])

    sample_mess['label'] = _sam_label

    # 计算坐标点
    tcr_coordinate = MDS(tcr_dist)

    filter_tcr['X'] = tcr_coordinate[:,0]
    filter_tcr['Y'] = tcr_coordinate[:,1]

    X = []
    Y = []
    for idx in tqdm(sample_mess.index):
        tcr = sample_mess.loc[idx, 'V_CDR3']
        x = filter_tcr[filter_tcr['V_CDR3'] == tcr]['X'].values[0]
        y = filter_tcr[filter_tcr['V_CDR3'] == tcr]['Y'].values[0]
        X.append(x)
        Y.append(y)

    sample_mess['X'] = X
    sample_mess['Y'] = Y


    sample_mess.to_csv(save_path, sep='\t')
    



if __name__ == '__main__':
    
    calc_tcr_coord()



