import csv
import pandas as pd
import numpy as np
import cPickle as pickle

	
import sys
if __name__ == "__main__":
	
	pred_dv_file = sys.argv[1]

	
	pred_dv_handle = open(pred_dv_file)

	
	pred_reader = csv.DictReader(pred_dv_handle)

	user_count = 0
	summation = 0
        baduser=[]
        couponcount={}
	for pred_row in pred_reader:
	
		pred_coupons = pred_row["PURCHASED_COUPONS"].split(" ")
                for pc in pred_coupons:
                    if pc not in couponcount:
                        couponcount[pc]=0
                    couponcount[pc]+=1
	
        kc=[i for i in couponcount]
        vc=[couponcount[i] for i in couponcount]
        couponcount=pd.DataFrame({'coupon':kc,'count':vc})
        result=couponcount.sort_index(by='count',ascending=False)
        print result[:10]
        result=result[:10]
        pickle.dump(np.array(result['coupon']),open('popular.p','w'))
        
