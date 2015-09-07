import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
def getage(date):
    date=date.fillna('2015-08-28 14:14:18')
    year=date.apply(lambda x:x.split()[0].split('-')[0]).astype(int)
    month=date.apply(lambda x:x.split()[0].split('-')[1]).astype(int)
    day=date.apply(lambda x:x.split()[0].split('-')[2]).astype(int)
    return 365*(2015-year)+30*(9-month)+1-day

coupon_train=pd.read_csv('../input/coupon_list_train.csv').fillna(-999)
coupon_test=pd.read_csv('../input/coupon_list_test.csv').fillna(-999)

uncommon=['COUPON_ID_hash','DISPFROM','DISPEND','VALIDFROM','VALIDEND']
num_fea=['PRICE_RATE','CATALOG_PRICE','DISCOUNT_PRICE']
cat_fea=[i for i in coupon_test.columns.values if i not in uncommon+num_fea]

print cat_fea
vec=DictVectorizer()
for i in cat_fea:
    coupon_train[i]=map(str,coupon_train[i])
    coupon_test[i]=map(str,coupon_test[i])

Xt_sparse = vec.fit_transform(coupon_test[cat_fea].T.to_dict().values()).todense()
X_sparse = vec.transform(coupon_train[cat_fea].T.to_dict().values()).todense()

print X_sparse.shape, Xt_sparse.shape

for i in range(X_sparse.shape[1]):
    coupon_train['fea%d'%i]=X_sparse[:,i]*1.0
    coupon_test['fea%d'%i]=Xt_sparse[:,i]*1.0

coupon_train.drop(['DISPFROM','DISPEND','VALIDFROM','VALIDEND']+cat_fea,inplace=True, axis=1)
coupon_test.drop(['DISPFROM','DISPEND','VALIDFROM','VALIDEND']+cat_fea,inplace=True, axis=1)

coupon_train.to_csv('coupon_train.csv',index=False)
coupon_test.to_csv('coupon_test.csv',index=False)
