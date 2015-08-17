import sys
import numpy as np
import pandas as pd
from sklearn import preprocessing, cross_validation, metrics
from sklearn import ensemble
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb

from config import *

if __name__ == "__main__":
	train_file = "train_idvs.csv"

	train = pd.read_csv(train_file)
	print train.shape

	#col_names = ["UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName"]
        #train = train.drop(col_names, axis=1)

	le_UserPrefName = preprocessing.LabelEncoder()
        le_UserPrefName.fit(unique_pref_name)
        train["UserPrefName"] = le_UserPrefName.transform(train["UserPrefName"])

        le_CouponCapsuleText = preprocessing.LabelEncoder()
        le_CouponCapsuleText.fit(unique_capsule_text)
        train["CouponCapsuleText"] = le_CouponCapsuleText.transform(train["CouponCapsuleText"])

        le_CouponGenreName = preprocessing.LabelEncoder()
        le_CouponGenreName.fit(unique_genre_name)
        train["CouponGenreName"] = le_CouponGenreName.transform(train["CouponGenreName"])

        le_CouponLargeAreaName = preprocessing.LabelEncoder()
        le_CouponLargeAreaName.fit(unique_large_area_name)
        train["CouponLargeAreaName"] = le_CouponLargeAreaName.transform(train["CouponLargeAreaName"])

        le_CouponSmallAreaName = preprocessing.LabelEncoder()
        le_CouponSmallAreaName.fit(unique_small_area_name)
        train["CouponSmallAreaName"] = le_CouponSmallAreaName.transform(train["CouponSmallAreaName"])

        le_CouponKenName = preprocessing.LabelEncoder()
        le_CouponKenName.fit(unique_ken_name)
        train["CouponKenName"] = le_CouponKenName.transform(train["CouponKenName"])

	print "Filling NAs.."
	train['CouponValidPeriod'].fillna(-999, inplace=True)

	train_X = np.array( train.iloc[:, 2:-1])
	train_y = np.array( train["DV"] )
	print train_X.shape, train_y.shape

	#for i in xrange(train_X.shape[1]):
	#	print train.columns.values[i+2], sum(np.isnan(train_X[:,i]))


	################## XGBoost ###############
        print "Preparing data for XGB.."
        params = {}
        params["objective"] = "binary:logistic"
        params["eta"] = 0.2
        params["min_child_weight"] = 5
        params["subsample"] = 0.7
        params["colsample_bytree"] = 0.6
        params["scale_pos_weight"] = 0.8
        params["silent"] = 1
        params["max_depth"] = 6
        params["max_delta_step"]=2
        params["seed"] = 0
        params['eval_metric'] = "auc"

        plst = list(params.items())

	print "Building models.."
	cv_scores = []
	kf = cross_validation.KFold(train_X.shape[0], n_folds=8, shuffle=True, random_state=2015)
	for dev_index, val_index in kf:
		dev_X, val_X = train_X[dev_index,:], train_X[val_index,:]
		dev_y, val_y = train_y[dev_index], train_y[val_index]

		xgtrain = xgb.DMatrix(dev_X, label=dev_y)
        	xgtest = xgb.DMatrix(val_X, label=val_y)
        	watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]

        	print "Running model.."
        	num_rounds = 800
        	model = xgb.train(plst, xgtrain, num_rounds, watchlist)
        	pred_dev_y = model.predict(xgtrain)
        	pred_val_y = model.predict(xgtest)

		cv_scores.append( metrics.roc_auc_score(val_y, pred_val_y) )
		print cv_scores[-1]
	print cv_scores
	print np.mean(cv_scores)
