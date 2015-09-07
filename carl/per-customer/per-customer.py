import pandas as pd
import numpy as np
from sklearn.cross_validation import KFold,StratifiedKFold
from xgb_classifier import xgb_classifier
from sklearn import metrics
def myauc(y,pred):
    fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=1)
    return metrics.auc(fpr, tpr)
def train_predict(X,y,Xt,yt=[],c=1):
    if c==1:
        clf=xgb_classifier(num_round=60,eta=0.1,min_child_weight=5,depth=7, subsample=1,col=1)
        return clf.train_predict(X,y,Xt,yt)
    if c==2:
        clf=RandomForestRegressor(n_estimators=200,n_jobs=-1,max_depth=13,min_samples_split=4,min_samples_leaf=9, max_leaf_nodes= 1100)
        clf.fit(X,y)
        return clf.predict(Xt)    
    if c==3:
        clf=RankSVM()
        clf.fit(X,y)
        return clf.predict(Xt)
def kfold_cv(X_train, y_train,k,xid=None):

    kf=StratifiedKFold(y_train,n_folds=k)
    #pickle.dump(kf,open('kf.p','w'))
    xx=[]
    pred=y_train.copy()

    for train_index, test_index in kf:
        X_train_cv, X_test_cv = X_train[train_index,:],X_train[test_index,:]
        y_train_cv, y_test_cv = y_train[train_index],y_train[test_index]
        yp=train_predict(X_train_cv,y_train_cv,X_test_cv,yt=y_test_cv,c=1)
        #xx.append(normalized_weighted_gini(y_test_cv,yp))
        xx.append(myauc(y_test_cv,yp))
        pred[test_index]=yp
        print xx[-1]
    print xx,' mean:',np.mean(xx)

    print 'overall auc' ,myauc(y_train,pred)
    return pred


user=pd.read_csv('../input/coupon_detail_train.csv')
users=np.array(user['USER_ID_hash'].value_counts().index)

coupon_train=pd.read_csv('../peruser/coupon_train.csv')
coupon_test=pd.read_csv('../peruser/coupon_test.csv')

for ur in users:
    tmp=coupon_train.copy()
    mask=user['USER_ID_hash']==ur
    coupons=np.array(user[mask]['COUPON_ID_hash'].value_counts().index)

    y=np.zeros(coupon_train.shape[0])
    ftmp=np.array(coupon_train['COUPON_ID_hash'].isin(coupons))

    y[ftmp]=1
    if np.sum(y)<30:
        continue
    print ur,np.sum(y)
    names=[i for i in tmp.columns.values if i!='COUPON_ID_hash']
    X=np.array(tmp[names])

    tmpt=coupon_test.copy()
    Xt=np.array(tmpt[names])
    print X.shape, Xt.shape, y.shape
    yt=train_predict(X,y,Xt,c=1)

    tmpt['label']=yt
    tmpt[['label','COUPON_ID_hash']].to_csv('sub2/%s'%ur,index=False)
    del X,y,tmp,Xt,yt,tmpt
