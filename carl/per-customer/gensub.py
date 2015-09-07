import os
import pandas as pd
import numpy as np
import csv
files=os.listdir('sub2')
pred={}
name='../peruser/ave3sub.csv'
for row in csv.DictReader(open(name)):
    pred[row['USER_ID_hash']]=row['PURCHASED_COUPONS']
for sub in files:
    s=pd.read_csv('sub/%s'%sub)
    result = s.sort_index(by='label', ascending=False)
#    print ' '.join([str(i) for i in np.array(result[:10]['COUPON_ID_hash'])])#.head()
    pred[sub]=' '.join([str(i) for i in np.array(result[:10]['COUPON_ID_hash'])])
print len(files)
f=open('sub3.csv','w')
f.write('USER_ID_hash,PURCHASED_COUPONS\n')
for sub in pred:
    line='%s,%s\n'%(sub,pred[sub])
    f.write(line)
f.close()
