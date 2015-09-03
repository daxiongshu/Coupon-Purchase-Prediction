import datetime
import numpy as np
import pandas as pd

if __name__ == "__main__":
	# specification of input files #
	data_path = "../../Data/"
	coupon_list_file = data_path + "coupon_visit_train.csv"
	model_start_date = datetime.date(2012, 06, 17)  # (year, month, day)
	model_end_date = datetime.date(2012, 06, 23)

	# specification of output files #
	out_data_path = "../../Data/Model2/"
	feature_coupon_file = out_data_path + "coupon_visit_dev.csv"
	train_coupon_file = out_data_path + "coupon_visit_val.csv" 
	
	# converting to data frame #
	coupon_df = pd.read_csv(coupon_list_file, parse_dates=[1])
	print coupon_df.shape

	# getitng the data frame for features and train #
	train_indices = np.where(coupon_df['I_DATE']>=model_start_date)[0]
	feature_indices = np.where(coupon_df['I_DATE']<model_start_date)[0]
	train_coupon_df = coupon_df.iloc[train_indices,:]
	feature_coupon_df = coupon_df.iloc[feature_indices,:]
	print train_coupon_df.shape
	print feature_coupon_df.shape
	assert train_coupon_df.shape[0] + feature_coupon_df.shape[0] == coupon_df.shape[0]

	# writing it to csv file #
	train_coupon_df.to_csv(train_coupon_file, index=False)
	feature_coupon_df.to_csv(feature_coupon_file, index=False)
