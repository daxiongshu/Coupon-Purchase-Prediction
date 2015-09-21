import sys
import csv
import numpy as np
import pandas as pd
from sklearn import preprocessing, cross_validation, metrics
from sklearn import ensemble
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb

from config import *

if __name__ == "__main__":
	train_file = "train_idvs_seed1234.csv"
	test_file = "test_idvs.csv"
	user_file = "../../Data/user_list.csv"
	test_pred_file = "test_predictions_xgb_dep18_child50_eta05_round450_seed3_trainseed1234_d3.csv"

	train = pd.read_csv(train_file)
	users_list = np.array(pd.read_csv(user_file)["USER_ID_hash"]).astype('str')
	print train.shape

	print "Label encomding.."
	#col_names = ["UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName"]
	#train = train.drop(col_names, axis=1)

	#le_UserIDHash = preprocessing.LabelEncoder()
	#le_UserIDHash.fit(users_list)
        #train["USER_ID_hash"] = le_UserIDHash.transform(train["USER_ID_hash"].astype("str"))

	le_UserPrefName = preprocessing.LabelEncoder()
        le_UserPrefName.fit(unique_pref_name)
        train["UserPrefName"] = le_UserPrefName.transform(train["UserPrefName"].astype('str'))

        le_CouponCapsuleText = preprocessing.LabelEncoder()
        le_CouponCapsuleText.fit(unique_capsule_text)
        train["CouponCapsuleText"] = le_CouponCapsuleText.transform(train["CouponCapsuleText"].astype('str'))

        le_CouponGenreName = preprocessing.LabelEncoder()
        le_CouponGenreName.fit(unique_genre_name)
        train["CouponGenreName"] = le_CouponGenreName.transform(train["CouponGenreName"].astype('str'))

        le_CouponLargeAreaName = preprocessing.LabelEncoder()
        le_CouponLargeAreaName.fit(unique_large_area_name)
        train["CouponLargeAreaName"] = le_CouponLargeAreaName.transform(train["CouponLargeAreaName"].astype('str'))

        le_CouponSmallAreaName = preprocessing.LabelEncoder()
        le_CouponSmallAreaName.fit(unique_small_area_name)
        train["CouponSmallAreaName"] = le_CouponSmallAreaName.transform(train["CouponSmallAreaName"].astype('str'))

        le_CouponKenName = preprocessing.LabelEncoder()
        le_CouponKenName.fit(unique_ken_name)
        train["CouponKenName"] = le_CouponKenName.transform(train["CouponKenName"].astype('str'))

	print "Filling NAs.."
	train['CouponValidPeriod'].fillna(-999, inplace=True)

	
	train_y = np.array( train["DV"] )
	#train = np.array( train.iloc[:, 2:-1])
	train = np.array( train.drop(["COUPON_ID_hash","USER_ID_hash","DV"],axis=1))
	print train.shape, train_y.shape

	#for i in xrange(train_X.shape[1]):
	#	print train.columns.values[i+2], sum(np.isnan(train_X[:,i]))

	################## XGBoost ###############
        print "Preparing data for XGB.."
        params = {}
        params["objective"] = "binary:logistic"
        params["eta"] = 0.05
        params["min_child_weight"] = 18
        params["subsample"] = 0.7
        params["colsample_bytree"] = 0.6
        params["scale_pos_weight"] = 0.8
        params["silent"] = 1
        params["max_depth"] = 14
        params["max_delta_step"]=2
        params["seed"] = 2
        params['eval_metric'] = "auc"

        plst = list(params.items())


	xgtrain = xgb.DMatrix(train, label=train_y)
	del train
	del train_y
	import gc
	gc.collect()

	print "Running model.."
	num_rounds = 450
	model = xgb.train(plst, xgtrain, num_rounds)

	del xgtrain
	gc.collect()

	print "Preparing test.."
	test_writer = csv.writer(open(test_pred_file, "w"))
	test_writer.writerow(["USER_ID_hash", "COUPON_ID_hash", "Prediction"])
	full_test = pd.read_csv(test_file, chunksize=354532)
	for test in full_test:
		print "Reading new chunk..."
		#col_names = ["UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName"]
		#test = test.drop(col_names, axis=1)
		test_userid = test["USER_ID_hash"].copy()
		#test["USER_ID_hash"] = le_UserIDHash.transform(test["USER_ID_hash"].astype("str"))
		test["UserPrefName"] = le_UserPrefName.transform(test["UserPrefName"].astype('str'))
                test["CouponCapsuleText"] = le_CouponCapsuleText.transform(test["CouponCapsuleText"].astype('str'))
                test["CouponGenreName"] = le_CouponGenreName.transform(test["CouponGenreName"].astype('str'))
                test["CouponLargeAreaName"] = le_CouponLargeAreaName.transform(test["CouponLargeAreaName"].astype('str'))
                test["CouponSmallAreaName"] = le_CouponSmallAreaName.transform(test["CouponSmallAreaName"].astype('str'))
                test["CouponKenName"] = le_CouponKenName.transform(test["CouponKenName"].astype('str'))

		test['CouponValidPeriod'].fillna(-999, inplace=True)
		#test_X = np.array(test.iloc[:,2:-1])
		test_X = np.array( test.drop(["COUPON_ID_hash","USER_ID_hash","DV"],axis=1))
		xgtest = xgb.DMatrix(test_X)
		preds = model.predict(xgtest)

		for row_no in xrange(test.shape[0]):
			test_writer.writerow([test_userid[row_no], test["COUPON_ID_hash"][row_no], preds[row_no]])
			
