import csv
import datetime
import numpy as np
import pandas as pd

if __name__ == "__main__":
	file_name = "val_predictions_xgb_dep14_child18_eta05_round450_seed0_devseed1234.csv"
	sample_sub_file = "val_dv.csv"
	sub_file_name = "val_sub.csv"
	coupon_file_name = "../../Data/Model2/coupon_list_val.csv"

	file_handle = open(file_name,"rb")
	sub_file_handle = open(sub_file_name, "wb")
	coupon_file_handle = open(coupon_file_name, "rb")
	user_ids_list = np.array( pd.read_csv(sample_sub_file)["USER_ID_hash"] )

	reader = csv.DictReader(file_handle)
	writer = csv.writer(sub_file_handle)
	coupon_reader = csv.DictReader(coupon_file_handle)
	writer.writerow(["USER_ID_hash","PURCHASED_COUPONS"])

	day_weight_dict = {17:1.0, 18:0.98, 19:0.96, 20:0.94, 21:0.91, 22:0.87, 23:0.82}

	print "Getting coupon dict.."
	coupon_dict = {}
	for row in coupon_reader:
		disp_date = datetime.datetime.strptime(row['DISPFROM'], "%Y-%m-%d %H:%M:%S").day
		coupon_dict[row["COUPON_ID_hash"]] = disp_date

	print "Getting user dict.."
	user_dict = {}
	for row in reader:
		user_id = row["USER_ID_hash"]
		temp_dict = user_dict.get(user_id, {})
		weight = day_weight_dict[ coupon_dict[row["COUPON_ID_hash"]] ]
		temp_dict[float(row["Prediction"])*weight] = row["COUPON_ID_hash"]
		user_dict[user_id] = temp_dict

	print "Writing to out file.."
	for user_id in user_ids_list:
		temp_dict = user_dict[user_id]
		pred_values_list = list(temp_dict.keys())
		pred_values_list.sort()
		pred_values_list.reverse()
		#print pred_values_list[:10]
		purchased_coupons = []
		for i in xrange(10):
			#if pred_values_list[i]>0.2:
				purchased_coupons.append( temp_dict[pred_values_list[i]] )
		purchased_coupons = " ".join(purchased_coupons)
		writer.writerow([user_id, purchased_coupons])
			 

	file_handle.close()
	sub_file_handle.close()	
	coupon_file_handle.close()
