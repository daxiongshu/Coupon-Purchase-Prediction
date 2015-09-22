import csv
import sys
import cPickle as pickle
name=sys.argv[1]
bad=pickle.load(open('baduser.p'))
popular=pickle.load(open('popular_sub.p'))
pc=[str(i) for i in popular]
pc=' '.join(pc)
f=open('popular_%s'%name,'w')
f.write('USER_ID_hash,PURCHASED_COUPONS\n')
f1=open(name)
f1.readline()
for row in csv.DictReader(open(name)):
    line=f1.readline()
    if row['USER_ID_hash'] in bad:
        line='%s,%s\n'%(row['USER_ID_hash'],pc)
    #else:
    #    line='%s,%s\n'%(row['USER_ID_hash'],row['PURCHASED_COUPONS'])

    f.write(line)
f.close()    
