# -*- coding: utf-8 -*-
import csv
import random
import numpy as np
import pandas as pd
import datetime

from feature_extraction import getUserDict, getCouponDict, getDayWiseCoupons, getCouponPurchaseDict, getDVDict, getDV, getUserFeatures, getUserHistFeatures, getCountFromDict, getMinMaxMeanFromList, getUsableDayFeatures, getDummyVars, getDummyVarsDays, getCouponFeatures, getPrefectureLocationDict, getCouponAreaDict, getCouponVisitDict, getUserVisitFeatures, getCouponAreaFeatures

if __name__ == "__main__":
        model_data_path = "../../Data/Model2/"
        full_data_path = "../../Data/"

        # file_names #
        user_file = full_data_path + "user_list.csv"
        ##coupon_list_train_file = model_data_path + "coupon_list_val.csv"
        coupon_list_feature_file = model_data_path + "coupon_list_dev.csv"
        ##coupon_detail_train_file = model_data_path + "coupon_detail_val.csv"
        coupon_detail_feature_file = model_data_path + "coupon_detail_dev.csv"
	coupon_visit_feature_file = model_data_path + "coupon_visit_dev.csv"
	prefecture_location_file = full_data_path + "prefecture_locations.csv"
	coupon_area_file = full_data_path + "coupon_area_train.csv"
	model_start_date = datetime.date(2012, 06, 17)  # (year, month, day)
        ##model_end_date = datetime.date(2012, 06, 23)

        # getting User Dict from user file #
        print "Getting User Dict.."
        user_dict = getUserDict(user_file)

        # getting the coupons used for train and features #
        print "Getting Coupon Dict.."
        ##coupon_list_train_dict = getCouponDict(coupon_list_train_file)
        coupon_list_feature_dict = getCouponDict(coupon_list_feature_file)

	# getting coupons daywise #
	daywise_coupon_list_dict = getDayWiseCoupons(coupon_list_feature_file)

	## getting the DV Dict of that has purchase combination of userid and coupon id #
        ##print "Getting DV Dict..."
        ##dv_dict = getDVDict(coupon_detail_train_file, coupon_list_train_dict.keys())

        # getting the dict of past coupon purcahse details of user from coupon_detail #
        print "Getting Coupon purchase details.."
        coupon_purchase_detail_dict = getCouponPurchaseDict(coupon_detail_feature_file)

	# Getting prefecture location details #
	print "Getting Prefecture location details.. "
	prefecture_location_dict = getPrefectureLocationDict(prefecture_location_file)

	# getting coupon area details in form of dict #
	print "Getting coupon area dict.."
	coupon_area_dict = getCouponAreaDict(coupon_area_file)

	# getting coupon visit history of users in form of dict#
	print "Getting the visit history of users.."
	coupon_visit_dict = getCouponVisitDict(coupon_visit_feature_file)

	# preparing IDVs #
	print "Preparing IDVs..."
	out_file = csv.writer(open("dev_idvs.csv","w"))
	random.seed(1234)
	user_count = 0
	out_row_count = 0
	for user_id in coupon_purchase_detail_dict:
		coupon_purchase_detail_userid_list = coupon_purchase_detail_dict[user_id]
		for ind, coupon_dict in enumerate(coupon_purchase_detail_userid_list):
			purchase_coupon = coupon_dict['COUPON_ID_hash']
			puchase_date = datetime.datetime.strptime(coupon_dict['I_DATE'], "%Y-%m-%d %H:%M:%S").date()

			# getting coupons on the given day which is x days before purchase day #
			days_before = random.randint(1,7)
			date_before_purchase_date = puchase_date - datetime.timedelta(days=days_before)
			try:
				daywise_coupon_list = daywise_coupon_list_dict[date_before_purchase_date]
			except:
				date_before_purchase_date = puchase_date
				daywise_coupon_list = daywise_coupon_list_dict[date_before_purchase_date]

			# getting user features #
			user_features, user_features_header = getUserFeatures(user_dict[user_id], prefecture_location_dict, date_before_purchase_date)

			# getting the new history list and getting user_hist features based on it #
			new_coupon_purchase_detail_userid_list = []
			for coupon_purchase_detail in coupon_purchase_detail_userid_list[:ind]:
				if  datetime.datetime.strptime(coupon_purchase_detail['I_DATE'], "%Y-%m-%d %H:%M:%S").date() < date_before_purchase_date:
					new_coupon_purchase_detail_userid_list.append(coupon_purchase_detail)
			#print new_coupon_purchase_detail_userid_list
			user_hist_features, user_hist_features_header, master_list = getUserHistFeatures(new_coupon_purchase_detail_userid_list, coupon_list_feature_dict, model_start_date, date_before_purchase_date)
			user_visit_features, user_visit_features_header = getUserVisitFeatures(user_id, coupon_visit_dict, date_before_purchase_date)
			coupon_area_features, coupon_area_features_header = getCouponAreaFeatures(user_dict[user_id], coupon_area_dict, purchase_coupon)
		
			# getting coupon for dv = 1 #
			coupon_features, coupon_features_header = getCouponFeatures(coupon_list_feature_dict[purchase_coupon], master_list)
			dv_value = 1
			if out_row_count == 0:
                                out_header = ["USER_ID_hash", "COUPON_ID_hash"]+ user_features_header + user_hist_features_header + user_visit_features_header + coupon_area_features_header + coupon_features_header + ["DV"]
                                out_header_len = len(out_header)
                                out_file.writerow( out_header )
			out_row = [user_id, purchase_coupon] + user_features + user_hist_features + user_visit_features + coupon_area_features + coupon_features + [dv_value]
                        assert len(out_row) == out_header_len
                        out_file.writerow( out_row )
                        out_row_count += 1
	
			# getting some coupons for dv=0 #
			no_of_non_purchased_coupons = 4
			if len(daywise_coupon_list) > no_of_non_purchased_coupons :
				non_purchased_coupons = random.sample(daywise_coupon_list, no_of_non_purchased_coupons)
				for non_purchased_coupon in non_purchased_coupons:
					if non_purchased_coupon == purchase_coupon:
						continue
					coupon_area_features, coupon_area_features_header = getCouponAreaFeatures(user_dict[user_id], coupon_area_dict, non_purchased_coupon)
					coupon_features, coupon_features_header = getCouponFeatures(coupon_list_feature_dict[non_purchased_coupon], master_list)	
					dv_value = 0
					out_row = [user_id, non_purchased_coupon] + user_features + user_hist_features + user_visit_features + coupon_area_features + coupon_features + [dv_value]
		                        assert len(out_row) == out_header_len
                		        out_file.writerow( out_row )
		                        out_row_count += 1	
		user_count += 1

		if user_count % 200 == 0:
			print "Processed Users : ", user_count
					
				 


