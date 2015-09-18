# -*- coding: utf-8 -*-
"""
    0     1     2     3     4     5     6     7     8     9    10    11    13 
20731  1493   401   134    64    24    10     5     5     2     1     2     1 
"""
import csv
import numpy as np
import pandas as pd
import datetime

def getUserDict(user_file):
	file_handle = open(user_file,'rb')
	file_reader = csv.DictReader(file_handle)
	
	user_dict = {}
	counter = 0
	for row in file_reader:
		user_dict[row['USER_ID_hash']] = row
		counter += 1
	assert len(user_dict.keys()) == counter

	file_handle.close()
	return user_dict

def getCouponDict(coupon_file):
	file_handle = open(coupon_file,'rb')
        file_reader = csv.DictReader(file_handle)

	counter = 0
	coupon_dict = {}
	for row in file_reader:
		coupon_dict[row['COUPON_ID_hash']] = row
		counter += 1
	assert len(coupon_dict.keys()) == counter

	file_handle.close()
        return coupon_dict


def getCouponPurchaseDict(coupon_file):
	file_handle = open(coupon_file,'rb')
        file_reader = csv.DictReader(file_handle)
	coupon_purchase_dict = {}
	for row in file_reader:
		temp_list = coupon_purchase_dict.get(row['USER_ID_hash'], [])
		temp_list.append(row)
		coupon_purchase_dict[row['USER_ID_hash']] = temp_list
	file_handle.close()
	return coupon_purchase_dict

def getDVDict(coupon_file, coupon_list):
	file_handle = open(coupon_file,'rb')
        file_reader = csv.DictReader(file_handle)
	dv_dict = {}
        for row in file_reader:
		if row['COUPON_ID_hash'] in coupon_list:
			temp_list = dv_dict.get(row['USER_ID_hash'],[])
			temp_list.append(row['COUPON_ID_hash'])
			dv_dict[row['USER_ID_hash']] = temp_list
	file_handle.close()
	return dv_dict

def writeDV(dv_dict, user_file, out_file):
	user_file_handle = open(user_file)
	out_file_handle = open(out_file, "wb")

	reader = csv.DictReader(user_file_handle)
	writer = csv.writer(out_file_handle)
	writer.writerow(["USER_ID_hash","PURCHASED_COUPONS"]) # writing header

	for row in reader:
		user_id = row["USER_ID_hash"]
		coupon_str = ""
		if dv_dict.has_key(user_id):
			coupon_list = list(set(dv_dict[user_id]))
			coupon_str = " ".join(coupon_list)
		writer.writerow([user_id, coupon_str])

	user_file_handle.close()
	out_file_handle.close()

if __name__ == "__main__":
	model_data_path = "../../Data/Model2/"
	full_data_path = "../../Data/"

	# file_names #
	coupon_list_train_file = model_data_path + "coupon_list_val.csv"
	coupon_detail_train_file = model_data_path + "coupon_detail_val.csv"
	sample_sub_file = full_data_path + "sample_submission.csv"
	out_file = "val_dv.csv"
	model_start_date = datetime.date(2012, 06, 17)  # (year, month, day)
        model_end_date = datetime.date(2012, 06, 23)

	# getting the coupons used for train and features #
	print "Getting Coupon Dict.."
	coupon_list_train_dict = getCouponDict(coupon_list_train_file)

	# getting the DV Dict of that has purchase combination of userid and coupon id #
	print "Getting DV Dict..."
	dv_dict = getDVDict(coupon_detail_train_file, coupon_list_train_dict.keys())	

	# writing out the dv to out file #
	print "Writing out DV..."
	writeDV(dv_dict, sample_sub_file, out_file)
