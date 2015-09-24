import numpy as np
import pandas as pd
from sklearn.cross_validation import KFold
from sklearn import ensemble, metrics

if __name__ == "__main__":
	data_path = "./"
	train_file_name = data_path + "valdata_secondlevel.csv"

	train_df = pd.read_csv(train_file_name)
	print train_df.shape

	print "Getting rank.."
	train_df["Preds0_Rank"] = train_df.groupby('USER_ID_hash')['Preds0'].rank(ascending=False)
	print "Getting rank2"
	train_df["Preds1_Rank"] = train_df.groupby('USER_ID_hash')['Preds1'].rank(ascending=False)
	train_df["Preds2_Rank"] = train_df.groupby('USER_ID_hash')['Preds2'].rank(ascending=False)
	train_df["Preds3_Rank"] = train_df.groupby('USER_ID_hash')['Preds3'].rank(ascending=False)
	train_df["Preds4_Rank"] = train_df.groupby('USER_ID_hash')['Preds4'].rank(ascending=False)
	train_df["Preds5_Rank"] = train_df.groupby('USER_ID_hash')['Preds5'].rank(ascending=False)
	train_df["Preds6_Rank"] = train_df.groupby('USER_ID_hash')['Preds6'].rank(ascending=False)
	train_df["Preds7_Rank"] = train_df.groupby('USER_ID_hash')['Preds7'].rank(ascending=False)

	print "Get other data.."
	cols_to_use = ['Preds0', 'Preds1', 'Preds2', 'Preds3', 'Preds4', 'Preds5', 'Preds6', 'Preds7', 'Preds0_Rank', 'Preds1_Rank', 'Preds2_Rank', 'Preds3_Rank', 'Preds4_Rank', 'Preds5_Rank', 'Preds6_Rank', 'Preds7_Rank']
	#cols_to_use = ['Preds1', 'Preds4', 'Preds6', 'Preds1_Rank', 'Preds4_Rank', 'Preds6_Rank']
	train_X = np.array( train_df[cols_to_use] )
	train_y = np.array( train_df['DV'] )
	train_coupon_id = np.array( train_df['COUPON_ID_hash'] )
	train_user_id = np.array( train_df['USER_ID_hash'] )
	train_unique_users = np.unique(train_user_id)
	del train_df
	import gc
	gc.collect()

	print "Cross validating.."
	pred_train = np.zeros(train_X.shape[0])
        kf = KFold(len(train_unique_users), n_folds=5, shuffle=True, random_state=0)
        #print len(unique_train_tube_ids)
        cv_scores = []
        for dev_unique_index, val_unique_index in kf:
                dev_index, val_index = [], []
                dev_user_ids, val_user_ids = set(train_unique_users[dev_unique_index]), set(train_unique_users[val_unique_index])

                for index, value in enumerate(train_user_id):
                        if value in dev_user_ids:
                                dev_index.append(index)
                        elif value in val_user_ids:
                                val_index.append(index)
                        else:
                                raise
                print len(dev_index), len(val_index)

                dev_X, val_X = train_X[dev_index,:], train_X[val_index,:]
                dev_y, val_y = train_y[dev_index], train_y[val_index]

		print "Running model.."
		clf = ensemble.RandomForestClassifier(n_estimators=30, max_depth=5, min_samples_leaf=3, max_features=0.6, n_jobs=4, random_state=0)
		clf.fit(dev_X, dev_y)
		pred_val_y = clf.predict_proba(val_X)[:,1]
		pred_train[val_index] = pred_val_y

		print metrics.roc_auc_score(val_y, pred_val_y)

	del train_X
	gc.collect()

	out_df = pd.DataFrame({"USER_ID_hash":train_user_id, "COUPON_ID_hash":train_coupon_id, "Prediction":pred_train})
        out_df.to_csv("val_preds.csv", index=False)

