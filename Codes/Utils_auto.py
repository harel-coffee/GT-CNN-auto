from __future__ import print_function

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.nn import init
from torch.utils.data import Dataset, DataLoader

import pickle
import numpy as np
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

from fastai import *
from fastai.text import *
from fastai.vision import *
from fastai.imports import *

from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

from imblearn.over_sampling import RandomOverSampler

from collections import OrderedDict
import json
import subprocess
import sys
import time
import xml.etree.ElementTree

import os
import io
import random

from scipy.stats import norm
from scipy.stats import genextreme

######################################################################
# multitask dataset overwrite of Dataset
class MultitaskDataset(Dataset):
    "`Dataset` for joint single and multi-label image classification."
    def __init__(self, data, labels_fold, labels_fam, paddings, cuda = True):   
        self.data = torch.FloatTensor(data.float())
        self.y_fam = torch.FloatTensor(labels_fam.float())
        self.y_fold = torch.FloatTensor(labels_fold.float())
        self.paddings = torch.FloatTensor(798-2*paddings.float())
        
        self.cuda = cuda
    
    def __len__(self): return len(self.data)
    
    def __getitem__(self,i:int): 
        if self.cuda:
            return torch.FloatTensor(self.data[i]).float().cuda(), torch.FloatTensor([self.y_fold[i], self.y_fam[i]]).float().cuda(),  self.paddings[i].cuda()
        else:
            return torch.FloatTensor(self.data[i]).float(), torch.FloatTensor([self.y_fold[i], self.y_fam[i]]).float(), self.paddings[i]

# a helper function to load the data into custom dataset

def Dataset_Loader(df, le_fam, le_fold, vocab, BATCH_SIZE, cuda = True):
    x_train = torch.LongTensor(Map_Tokens(df.q3seqTokens, vocab))
    y_train_fold = torch.LongTensor(le_fold.fit_transform(df["fold"].values.ravel()))
    y_train_fam = torch.LongTensor(le_fam.fit_transform(df["family"].values.ravel()))
    paddings = torch.LongTensor(df["paddings"].values.ravel())
    
    ds = MultitaskDataset(x_train, y_train_fold, y_train_fam, paddings, cuda)
    dl = DataLoader(
        ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        pin_memory=False)
    return ds, dl

# a helper function for mapping strings to onehot code
def Map_Tokens(data, vocab):
    indexed_tokens = []
    
    for tokens in data:
        indexed_token = []
        for token in tokens:
            if token in vocab:
                indexed_token.append(vocab[token])
        indexed_tokens.append(indexed_token)
    return indexed_tokens


# a helper function for train test validation split
def Train_Test_Val_split(df, strantify_type="fold", split_rate=0.1, random_state=2020):
    train_df, test_df = train_test_split(df, test_size=split_rate, random_state=random_state, 
                               stratify=df[strantify_type])
    train_df, val_df = train_test_split(train_df, test_size=(split_rate)/(1-split_rate), random_state=random_state, 
                               stratify=train_df[strantify_type])
    print(str(len(train_df))+" "+str(len(test_df))+" "+str(len(val_df)))
    return train_df, test_df, val_df


# a helper function to plot confuction matrix
def plot_confusion_matrix(cm, labels_name, title):
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]    # 归一化
    plt.imshow(cm, interpolation='nearest')    # 在特定的窗口上显示图像
    plt.title(title)    # 图像标题
    plt.colorbar()
    num_local = np.array(range(len(labels_name)))    
    plt.xticks(num_local, labels_name, rotation=90)    # 将标签印在x轴坐标上
    plt.yticks(num_local, labels_name)    # 将标签印在y轴坐标上
    plt.ylabel('True label')    
    plt.xlabel('Predicted label')
    plt.grid(b=True)
    plt.plot()
    
# Evaluation the model
def model_evaluation(model, le_fam, le_fold, Test_dl, cm = "fold"):
    try:
        model.eval()
        with torch.no_grad():
            _predictions_1 = []
            _predictions_2 = []
            _gt_1 = []
            _gt_2 = []
            for xb, yb in Test_dl:
                output1, output2, _ = model(xb)
                _, predicted1 = torch.max(output1, 1)
                _, predicted2 = torch.max(output2, 1)
                _predictions_1.extend(predicted1.cpu().numpy())
                _predictions_2.extend(predicted2.cpu().numpy())
                _gt_1.extend(yb[:,0].cpu().numpy())
                _gt_2.extend(yb[:,1].cpu().numpy())

            _predictions_1 = le_fold.inverse_transform(_predictions_1)
            _predictions_2 = le_fam.inverse_transform(_predictions_2)
            #print(_gt_2)
            _gt_1 = list(map(int, _gt_1))
            _gt_1 = le_fold.inverse_transform(_gt_1)

            _gt_2 = list(map(int, _gt_2))
            _gt_2 = le_fam.inverse_transform(_gt_2)

            print(classification_report(_gt_1, _predictions_1))
            print(classification_report(_gt_2, _predictions_2))
            #plot confusion matrix
            if cm == "fold":
                cm1 = plot_confusion_matrix(confusion_matrix(_gt_1, _predictions_1), df_large_zero["fold"].unique(), "Confusion Matrix Fold")
            else:
                cm2 = plot_confusion_matrix(confusion_matrix(_gt_2, _predictions_2), df_large_zero["family"].unique(), "Confusion Matrix Family")
    except RuntimeError as exception:
        if "out of memory" in str(exception):
            print("WARNING: out of memory")
            if hasattr(torch.cuda, 'empty_cache'):
                torch.cuda.empty_cache()
        else:
            raise exception

####################################################
## Functino for plotting the boxplot of RE scores
def gen_boxplot(train,test):
    train_all_fold=train.copy() # train_all
    train_all_fold['Family']=train_all_fold['Family'].map(lambda x: x.split('-')[1])
    data = pd.concat([train_all_fold, test]) 
    ordered_list=test.groupby('Family').median().sort_values('Err').index.tolist()
    ordered_list[:0] = ['A','B','C','lyso']
    plt.figure(figsize=(15,15))
    g=sns.boxplot(x='Err', y='Family', data=data,order=ordered_list)
    g.axvline(0.107, alpha = 0.9, linestyle = ":",linewidth=3,color="red")
    g.axvline(0.127, alpha = 0.9, linestyle = ":",linewidth=1,color="blue")
    g.axvline(0.147, alpha = 0.9, linestyle = ":",linewidth=3,color="red")
    g.set_xlim(0,0.5)
    return(g)

####################################################
## Calculate the FAS scores 
def calcSubScore(row,re_values):
    allval=list()
    for i in range(1,10):
        cname=row.index[i]
        val=float(row[i])
        sc=float(re_values['SC'][cname])
        ooc=float(re_values['OOC'][cname])
        oof=float(re_values['OOF'][cname])
        score=((((ooc-val)/(oof-sc))*(oof-ooc))-0.014)*100
        
        allval.append(score)
    return(pd.Series(allval))