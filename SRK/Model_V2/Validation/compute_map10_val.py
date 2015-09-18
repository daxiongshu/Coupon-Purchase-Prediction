import csv
import pandas as pd
import numpy as np
from average_precision import apk

def computeMAP(actual_coupons, pred_coupons, m=10, n=10):
	len_actual_coupons = len(actual_coupons)
	len_pred_coupons = len(pred_coupons)

	# return 0 if there are no actual coupon purchase #
	if len_actual_coupons == 0:
		return 0

	# truncating the list if the number of coupons are greater than allowed limit #
	if len_actual_coupons > m:
		actual_coupons = actual_coupons[:m]
		len_actual_coupons = m
	if len_pred_coupons > n:
		pred_coupons = pred_coupons[:n]
		len_pred_coupons = n
	#if len_pred_coupons > len_actual_coupons:
        #        pred_coupons = pred_coupons[:len_actual_coupons]
        #        len_pred_coupons = len_actual_coupons


	prefix = 1.0 / len_actual_coupons
	summation = 0
	num_present = 0
	for k in xrange(len_pred_coupons):
		if pred_coupons[k] in actual_coupons:
			num_present += 1
			summation += num_present / float(k+1)

	return prefix * summation
	

if __name__ == "__main__":
	actual_dv_file = "val_dv.csv"
	pred_dv_file = "val_sub.csv"

	actual_dv_handle = open(actual_dv_file)
	pred_dv_handle = open(pred_dv_file)

	actual_reader = csv.DictReader(actual_dv_handle)
	pred_reader = csv.DictReader(pred_dv_handle)

	user_count = 0
	summation = 0
	for act_row in actual_reader:
		pred_row = pred_reader.next()
		assert act_row["USER_ID_hash"] == pred_row["USER_ID_hash"]
		if act_row["PURCHASED_COUPONS"]:
			actual_coupons = act_row["PURCHASED_COUPONS"].split(" ")
		else:
			actual_coupons = []
		pred_coupons = pred_row["PURCHASED_COUPONS"].split(" ")
		#map_at_10 = computeMAP(actual_coupons, pred_coupons, m=10, n=10)
		map_at_10 = apk(actual_coupons, pred_coupons)
		summation += map_at_10
		user_count += 1

	#print user_count
	#print summation
	overall_map_at_10 = summation / float(user_count)
	print "Eval metric value : ", overall_map_at_10

	actual_dv_handle.close()
	pred_dv_handle.close() 
