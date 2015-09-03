# -*- coding: utf-8 -*-
import csv
import numpy as np
import pandas as pd
import datetime

from feature_extraction import getUserDict, getCouponDict, getDayWiseCoupons, getCouponPurchaseDict, getDVDict, getDV, getUserFeatures, getUserHistFeatures, getCountFromDict, getMinMaxMeanFromList, getUsableDayFeatures, getDummyVars, getDummyVarsDays, getCouponFeatures

if __name__ == "__main__":
	model_data_path = "../../Data/Model2/"
	full_data_path = "../../Data/"

	# file_names #
	user_file = full_data_path + "user_list.csv"
	coupon_list_train_file = model_data_path + "coupon_list_val.csv"
	coupon_list_feature_file = model_data_path + "coupon_list_dev.csv"
	coupon_detail_train_file = model_data_path + "coupon_detail_val.csv"
	coupon_detail_feature_file = model_data_path + "coupon_detail_dev.csv"
	out_file = csv.writer(open("val_idvs.csv","w"))
	model_start_date = datetime.date(2012, 06, 17)  # (year, month, day)
        model_end_date = datetime.date(2012, 06, 23)

	# getting User Dict from user file #
	print "Getting User Dict.."
	user_dict = getUserDict(user_file)

	# getting the coupons used for train and features #
	print "Getting Coupon Dict.."
	coupon_list_train_dict = getCouponDict(coupon_list_train_file)
	coupon_list_feature_dict = getCouponDict(coupon_list_feature_file)

	# getting the DV Dict of that has purchase combination of userid and coupon id #
	print "Getting DV Dict..."
	dv_dict = getDVDict(coupon_detail_train_file, coupon_list_train_dict.keys())	
	#dv_dict = {}

	# getting the dict of past coupon purcahse details of user from coupon_detail #
	print "Getting Coupon purchase details.."
	coupon_purchase_detail_dict = getCouponPurchaseDict(coupon_detail_feature_file)

	print "Preparing the data.."
	user_count = 0
	out_row_count = 0
	for user_id in user_dict.keys():
		user_features, user_features_header = getUserFeatures(user_dict[user_id], model_start_date)
		try:
			userid_coupon_purchase_detail_list = coupon_purchase_detail_dict[user_id]
		except:
			userid_coupon_purchase_detail_list = []
		user_hist_features, user_hist_features_header, master_list = getUserHistFeatures(userid_coupon_purchase_detail_list, coupon_list_feature_dict, model_start_date, model_start_date)
		for coupon_id in coupon_list_train_dict.keys():
			coupon_features, coupon_features_header = getCouponFeatures(coupon_list_train_dict[coupon_id], master_list)
			dv_value = getDV(user_id, coupon_id, dv_dict)
			if out_row_count == 0:
				out_header = ["USER_ID_hash", "COUPON_ID_hash"]+ user_features_header + user_hist_features_header + coupon_features_header + ["DV"]
				out_header_len = len(out_header)
				out_file.writerow( out_header )
			out_row = [user_id, coupon_id] + user_features + user_hist_features + coupon_features + [dv_value]
			assert len(out_row) == out_header_len
			out_file.writerow( out_row )
			out_row_count += 1
			#break
		user_count +=1
		#break
		if user_count % 200 == 0:
				print "Processed Users : ", user_count
