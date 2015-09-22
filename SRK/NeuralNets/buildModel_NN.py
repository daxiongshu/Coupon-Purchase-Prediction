import sys
import numpy as np
import pandas as pd
from sklearn import preprocessing, cross_validation, metrics
from sklearn import ensemble
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb

from config import *

np.random.seed(2015)
from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers.core import Dense, Activation, Dropout
from keras.constraints import maxnorm
from keras.utils import np_utils

def runNN(train_X, train_y, test_X, test_y=None):
	#sc = preprocessing.StandardScaler()
        #train_X = sc.fit_transform(train_X)
        #test_X = sc.transform(test_X)

	train_y = np_utils.to_categorical(train_y, 2)

        model = Sequential()
        model.add(Dense(train_X.shape[1], 100, init='he_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.2))
        model.add(Dense(100, 50, init='he_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.4))
        model.add(Dense(50, 25, init='he_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.4))
        model.add(Dense(25, 2, init='he_uniform'))
        model.add(Activation('softmax'))

        #sgd_opt = SGD(lr=0.01)
        model.compile(loss='binary_crossentropy', optimizer='adam')

        model.fit(train_X, train_y, batch_size=64, nb_epoch=30, validation_split=0.05, verbose=2)
        preds = model.predict(test_X, verbose=0)[:,1]
	print preds[:10]
	print "Test preds shape : ",preds.shape
	print "ROC AUC score : ", metrics.roc_auc_score(test_y, preds)
        #print "Val sample : ", RMSLE(test_y, preds)



if __name__ == "__main__":
	"""
	train_file = "dev_idvs.csv"

	train = pd.read_csv(train_file)
	print train.shape

	#col_names = ["UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName"]
        #train = train.drop(col_names, axis=1)

	#le_UserIDHash = preprocessing.LabelEncoder()
	#train["USER_ID_hash"] = le_UserIDHash.fit_transform(train["USER_ID_hash"].astype("str"))

	le_UserPrefName = preprocessing.LabelEncoder()
        temp = le_UserPrefName.fit_transform(unique_pref_name)
        train["UserPrefName"] = le_UserPrefName.transform(train["UserPrefName"])
	ohe_UserPrefName = preprocessing.OneHotEncoder(sparse=False)
	ohe_UserPrefName.fit(temp.reshape(-1,1))
	train_UserPrefName = ohe_UserPrefName.transform(train["UserPrefName"].reshape(-1,1))

        le_CouponCapsuleText = preprocessing.LabelEncoder()
        temp = le_CouponCapsuleText.fit_transform(unique_capsule_text)
        train["CouponCapsuleText"] = le_CouponCapsuleText.transform(train["CouponCapsuleText"])
	ohe_CouponCapsuleText = preprocessing.OneHotEncoder(sparse=False)
	ohe_CouponCapsuleText.fit(temp.reshape(-1,1))
	train_CouponCapsuleText = ohe_CouponCapsuleText.transform(train["CouponCapsuleText"].reshape(-1,1))

        le_CouponGenreName = preprocessing.LabelEncoder()
        temp = le_CouponGenreName.fit_transform(unique_genre_name)
        train["CouponGenreName"] = le_CouponGenreName.transform(train["CouponGenreName"])
	ohe_CouponGenreName = preprocessing.OneHotEncoder(sparse=False)
	ohe_CouponGenreName.fit(temp.reshape(-1,1))
	train_CouponGenreName = ohe_CouponGenreName.transform(train["CouponGenreName"].reshape(-1,1))

        le_CouponLargeAreaName = preprocessing.LabelEncoder()
        temp = le_CouponLargeAreaName.fit_transform(unique_large_area_name)
        train["CouponLargeAreaName"] = le_CouponLargeAreaName.transform(train["CouponLargeAreaName"])
	ohe_CouponLargeAreaName = preprocessing.OneHotEncoder(sparse=False)
	ohe_CouponLargeAreaName.fit(temp.reshape(-1,1))
	train_CouponLargeAreaName = ohe_CouponLargeAreaName.transform(train["CouponLargeAreaName"].reshape(-1,1))

        le_CouponSmallAreaName = preprocessing.LabelEncoder()
        temp = le_CouponSmallAreaName.fit_transform(unique_small_area_name)
        train["CouponSmallAreaName"] = le_CouponSmallAreaName.transform(train["CouponSmallAreaName"])
	ohe_CouponSmallAreaName = preprocessing.OneHotEncoder(sparse=False)
        ohe_CouponSmallAreaName.fit(temp.reshape(-1,1))
	train_CouponSmallAreaName = ohe_CouponSmallAreaName.transform(train["CouponSmallAreaName"].reshape(-1,1))

        le_CouponKenName = preprocessing.LabelEncoder()
        temp = le_CouponKenName.fit_transform(unique_ken_name)
        train["CouponKenName"] = le_CouponKenName.transform(train["CouponKenName"])
	ohe_CouponKenName = preprocessing.OneHotEncoder(sparse=False)
	ohe_CouponKenName.fit(temp.reshape(-1,1))
	train_CouponKenName = ohe_CouponKenName.transform(train["CouponKenName"].reshape(-1,1))

	print "Filling NAs.."
	train['CouponValidPeriod'].fillna(-999, inplace=True)

	train_y = np.array( train["DV"] )
	train_X = np.array( train.drop(["COUPON_ID_hash", "USER_ID_hash", "UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName", "DV"],axis=1))
	print train_X.shape, train_y.shape
	del train
	import gc
	gc.collect()

	train_X = np.hstack([train_X, train_UserPrefName, train_CouponCapsuleText, train_CouponGenreName, train_CouponLargeAreaName, train_CouponSmallAreaName, train_CouponKenName])
	del train_CouponCapsuleText
	del train_CouponGenreName
	del train_CouponLargeAreaName
	del train_UserPrefName
	del train_CouponSmallAreaName
	del train_CouponKenName
	gc.collect()

	print train_X.shape, train_y.shape

	#for i in xrange(train_X.shape[1]):
	#	print train.columns.values[i+2], sum(np.isnan(train_X[:,i]))

	print "Saving inputs.."
	np.save("train_X.npy", train_X)
	np.save("train_y.npy", train_y)
	print "Done"

	"""

	print "loading.."
	train_X = np.load("train_X.npy")
	train_y = np.load("train_y.npy")
	print train_X.shape, train_y.shape

	################## XGBoost ###############
	################## XGBoost ###############
        print "Building models.."
        cv_scores = []
        kf = cross_validation.KFold(train_X.shape[0], n_folds=8, shuffle=True, random_state=2015)
        for dev_index, val_index in kf:
                dev_X, val_X = train_X[dev_index,:], train_X[val_index,:]
                dev_y, val_y = train_y[dev_index], train_y[val_index]

                sc = preprocessing.StandardScaler()
                dev_X = sc.fit_transform(dev_X)
                val_X = sc.transform(val_X)

		runNN(dev_X, dev_y, val_X, test_y=val_y)

                break
