# -*- coding: utf-8 -*-
import csv
import random
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

def getDayWiseCoupons(coupon_file):
	file_handle = open(coupon_file,'rb')
        file_reader = csv.DictReader(file_handle)

        coupon_dict = {}
        for row in file_reader:
		disp_from = datetime.datetime.strptime(row["DISPFROM"], "%Y-%m-%d %H:%M:%S").date()
		temp_list = coupon_dict.get(disp_from, [])
		temp_list.append(row['COUPON_ID_hash'])
		coupon_dict[disp_from] = temp_list

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


def getDV(user_id, coupon_id, dv_dict):
        dv = 0
        if dv_dict.has_key(user_id):
                coupon_list = dv_dict[user_id]
                if coupon_id in coupon_list:
                        dv = 1
        return dv


def getUserFeatures(input_dict, assessment_date):
        header = ['UserGender', 'UserAge', 'UserPrefName', 'UserDaysSinceRegistered', 'UserWithdrawn']
        # getting gender variable #
        if input_dict['SEX_ID'] == 'f':
                feat_list = [1]
        else:
                feat_list = [0]

        # getting age variable #
        feat_list.append(float(input_dict['AGE']))

        # getting pref_name variable #
        feat_list.append(input_dict['PREF_NAME'])

        # getting reg month and year #
        reg_date = input_dict['REG_DATE']
        reg_date = datetime.datetime.strptime(reg_date, "%Y-%m-%d %H:%M:%S").date()
	feat_list.append((assessment_date - reg_date).days)
        #feat_list.append( reg_date.month )
        #feat_list.append( reg_date.year )

        # getting withdraw date #
        wd_date = input_dict['WITHDRAW_DATE']
        if wd_date == "NA":
                feat_list.append(0)
        else:
		wd_date = datetime.datetime.strptime(wd_date, "%Y-%m-%d %H:%M:%S").date()
		if wd_date < assessment_date:
                	feat_list.append(1)
		else:
			feat_list.append(0)

        return feat_list, header

def getUserHistFeatures(transaction_list, coupon_dict, model_start_date):
        feat_header = ["NoOfPurchases", "DaysSinceLastPurchase", "NoOfPurchasesLastweek", "NoOfPurchasesLast15Days", "NoOfPurchasesLast30Days", "NoOfPurchasesLast60Days", "NoOfPurchasesLast90Days"]

        # getting number of purchases #
        feat_list = [len(transaction_list)]

        # initializing variables #
        purchase_small_area_name_dict = {}
        puchase_date_list = []
        capsule_text_dict = {}
        genre_name_dict = {}
        price_rate_list = []
        catalog_price_list = []
        discount_price_list = []
        dispperiod_list = []
        valid_period_list = []
        usable_date_mon_list = {}
        usable_date_tue_list = {}
        usable_date_wed_list = {}
        usable_date_thu_list = {}
        usable_date_fri_list = {}
        usable_date_sat_list = {}
        usable_date_sun_list = {}
        usable_date_hol_list = {}
        usable_date_before_hol_list = {}
        coupon_large_area_name_dict = {}
        coupon_small_area_name_dict = {}
        coupon_ken_name_dict = {}
        days_since_last_purchase = 9999
        last_week_purchase = 0
        last_fifteendays_purchase = 0
        last_thirtydays_purchase = 0
        last_sixtydays_purchase = 0
        last_nintydays_purchase = 0
        for transaction in transaction_list:
                diff_days = (model_start_date - datetime.datetime.strptime(transaction['I_DATE'], "%Y-%m-%d %H:%M:%S").date()).days
                if diff_days < days_since_last_purchase:
                        days_since_last_purchase = diff_days
                if diff_days <= 7:
                        last_week_purchase += 1
                if diff_days <= 15:
                        last_fifteendays_purchase += 1
                if diff_days <= 30:
                        last_thirtydays_purchase += 1
                if diff_days <= 60:
                        last_sixtydays_purchase += 1
                if diff_days <= 90:
                        last_nintydays_purchase += 1

                coupon_id_dict = coupon_dict[ transaction['COUPON_ID_hash'] ]
                purchase_small_area_name_dict[transaction['SMALL_AREA_NAME']] = purchase_small_area_name_dict.get( transaction['SMALL_AREA_NAME'],0) + 1
                capsule_text_dict[ coupon_id_dict['CAPSULE_TEXT'] ]  = capsule_text_dict.get( coupon_id_dict['CAPSULE_TEXT'], 0) + 1
                genre_name_dict[ coupon_id_dict['GENRE_NAME'] ] = genre_name_dict.get( coupon_id_dict['GENRE_NAME'],0 ) + 1
                coupon_large_area_name_dict[ coupon_id_dict['large_area_name'] ] = coupon_large_area_name_dict.get( coupon_id_dict['large_area_name'],0 ) + 1
                coupon_small_area_name_dict[ coupon_id_dict['small_area_name'] ] = coupon_small_area_name_dict.get( coupon_id_dict['small_area_name'],0 ) + 1
                coupon_ken_name_dict[ coupon_id_dict['ken_name'] ] = coupon_ken_name_dict.get( coupon_id_dict['ken_name'],0 ) + 1
                price_rate_list.append( float(coupon_id_dict['PRICE_RATE']) )
                catalog_price_list.append( float(coupon_id_dict['CATALOG_PRICE']) )
                discount_price_list.append( float(coupon_id_dict['DISCOUNT_PRICE']) )
                dispperiod_list.append( float(coupon_id_dict['DISPPERIOD']) )
                if coupon_id_dict['VALIDPERIOD'] not in ('','NA'):
                        valid_period_list.append( float(coupon_id_dict['VALIDPERIOD']) )
                if coupon_id_dict['USABLE_DATE_MON'] not in ('','NA'):
                        usable_date_mon_list[ float(coupon_id_dict['USABLE_DATE_MON']) ] = usable_date_mon_list.get( float(coupon_id_dict['USABLE_DATE_MON']),0 ) + 1
                        usable_date_tue_list[ float(coupon_id_dict['USABLE_DATE_TUE']) ] = usable_date_tue_list.get( float(coupon_id_dict['USABLE_DATE_TUE']),0 ) + 1
                        usable_date_wed_list[ float(coupon_id_dict['USABLE_DATE_WED']) ] = usable_date_wed_list.get( float(coupon_id_dict['USABLE_DATE_WED']),0 ) + 1
                        usable_date_thu_list[ float(coupon_id_dict['USABLE_DATE_THU']) ] = usable_date_thu_list.get( float(coupon_id_dict['USABLE_DATE_THU']),0 ) + 1
                        usable_date_fri_list[ float(coupon_id_dict['USABLE_DATE_FRI']) ] = usable_date_fri_list.get( float(coupon_id_dict['USABLE_DATE_FRI']),0 ) + 1
                        usable_date_sat_list[ float(coupon_id_dict['USABLE_DATE_SAT']) ] = usable_date_sat_list.get( float(coupon_id_dict['USABLE_DATE_SAT']),0 ) + 1
                        usable_date_sun_list[ float(coupon_id_dict['USABLE_DATE_SUN']) ] = usable_date_sun_list.get( float(coupon_id_dict['USABLE_DATE_SUN']),0 ) + 1
                        usable_date_hol_list[ float(coupon_id_dict['USABLE_DATE_HOLIDAY']) ] = usable_date_hol_list.get( float(coupon_id_dict['USABLE_DATE_HOLIDAY']),0 ) + 1
                        usable_date_before_hol_list[ float(coupon_id_dict['USABLE_DATE_BEFORE_HOLIDAY']) ] = usable_date_before_hol_list.get( float(coupon_id_dict['USABLE_DATE_BEFORE_HOLIDAY']),0 )+1
                else:
                        usable_date_mon_list[2.0] = usable_date_mon_list.get( 2.0,0 ) + 1
                        usable_date_tue_list[2.0] = usable_date_tue_list.get( 2.0,0 ) + 1
                        usable_date_wed_list[2.0] = usable_date_wed_list.get( 2.0,0 ) + 1
                        usable_date_thu_list[2.0] = usable_date_thu_list.get( 2.0,0 ) + 1
                        usable_date_fri_list[2.0] = usable_date_fri_list.get( 2.0,0 ) + 1
                        usable_date_sat_list[2.0] = usable_date_sat_list.get( 2.0,0 ) + 1
                        usable_date_sun_list[2.0] = usable_date_sun_list.get( 2.0,0 ) + 1
                        usable_date_hol_list[2.0] = usable_date_hol_list.get( 2.0,0 ) + 1
                        usable_date_before_hol_list[2.0] = usable_date_before_hol_list.get( 2.0,0 ) + 1

        feat_list.extend([days_since_last_purchase, last_week_purchase, last_fifteendays_purchase, last_thirtydays_purchase, last_sixtydays_purchase, last_nintydays_purchase])
        return feat_list, feat_header, [purchase_small_area_name_dict, capsule_text_dict, genre_name_dict, coupon_large_area_name_dict, coupon_small_area_name_dict, coupon_ken_name_dict, price_rate_list, catalog_price_list, discount_price_list, dispperiod_list, valid_period_list, usable_date_mon_list, usable_date_tue_list, usable_date_wed_list, usable_date_thu_list, usable_date_fri_list, usable_date_sat_list, usable_date_sun_list, usable_date_hol_list, usable_date_before_hol_list]


def getCountFromDict(key, dic):
        count = 0
        count_norm = 0
        if dic.has_key(key):
                count = dic[key]
                den = np.sum( dic.values() )
                count_norm = count / float(den)
        return count, count_norm

def getMinMaxMeanFromList(val, in_list):
        min_value = -999
        max_value = -999
        mean_value = -999
        between_mean_max = 0
        between_min_mean = 0
        greater_max = 0
        lesser_min = 0
        if in_list != []:
                min_value = min(in_list)
                max_value = max(in_list)
                mean_value = np.mean(in_list)
                val = float(val)
                if val >= mean_value and val<= max_value:
                        between_mean_max = 1
                elif val >= min_value and val <= mean_value:
                        between_min_mean = 1
                elif val > max_value:
                        greater_max = 1
                elif val < min_value:
                        lesser_min = 1
        return [min_value, max_value, mean_value, between_mean_max, between_min_mean, greater_max, lesser_min]

def getUsableDayFeatures(val, usable_date_list):
        count = 0
        normalized_count = 0
        if len(usable_date_list) > 0 :
                for value in usable_date_list:
                        if float(val) == value:
                                count += 1
                normalized_count = count / float(len(usable_date_list))
        return count, normalized_count

def getCouponFeatures(coupon_dict, master_list):
        purchase_small_area_name_dict, capsule_text_dict, genre_name_dict, coupon_large_area_name_dict, coupon_small_area_name_dict, coupon_ken_name_dict, price_rate_list, catalog_price_list, discount_price_list, dispperiod_list, valid_period_list, usable_date_mon_list, usable_date_tue_list, usable_date_wed_list, usable_date_thu_list, usable_date_fri_list, usable_date_sat_list, usable_date_sun_list, usable_date_hol_list, usable_date_before_hol_list = master_list

        feat_header = ["CouponCapsuleText", "CouponGenreName", "CouponPriceRate", "CouponCatalogPrice", "CouponDiscountPrice", "CouponDispPeriod", "CouponValidPeriod", "CouponUsableMon", "CouponUsableTue", "CouponUsableWed", "CouponUsableThu", "CouponUsableFri", "CouponUsableSat", "CouponUsableSun", "CouponUsableHol", "CouponUsableBeforeHol", "CouponLargeAreaName", "CouponKenName", "CouponSmallAreaName", "CapsuleTextCount", "CapsuleTextCountNorm", "GenreNameCount", "GenreNameCountNorm", "LargeAreaNameCount", "LargeAreaNameCountNorm", "SmallAreaNameCount", "SmallAreaNameCountNorm", "KenNameCount","KenNameCountNorm", "PriceRateMin", "PriceRateMax", "PriceRateMean", "PriceRateBetMeanMax", "PriceRateBetMinMean", "PriceRateGrtMax", "PriceRateLessMin", "CatalogPriceMin", "CatalogPriceMax", "CatalogPriceMean", "CatalogPriceBetMeanMax", "CatalogPriceBetMinMean", "CatalogPriceGrtMax", "CatalogPriceLessMin", "DiscountPriceMin", "DiscountPriceMax", "DiscountPriceMean", "DiscountPriceBetMeanMax", "DiscountPriceBetMinMean", "DiscountPriceGrtMax", "DiscountPriceLessMin", "DispPeriodMin", "DispPeriodMax", "DispPeriodMean", "DispPeriodBetMeanMax", "DispPeriodBetMinMean", "DispPeriodGrtMax", "DispPeriodLessMin", "MondayCount", "MondayCountNorm", "TuesdayCount", "TuesdayCountNorm", "WednesdayCount", "WednesdayCountNorm", "ThursdayCount", "ThursdayCountNorm", "FridayCount", "FridayCountNorm", "SaturdayCount", "SaturdayCountNorm", "SundayCount", "SundayCountNorm", "HolidayCount", "HolidayCountNorm", "BeforeHolidayCount", "BeforeHolidayCountNorm"]

        if coupon_dict['USABLE_DATE_MON'] in ('','NA'):
                coupon_dict["USABLE_DATE_MON"] = 2.0
                coupon_dict["USABLE_DATE_TUE"] = 2.0
                coupon_dict["USABLE_DATE_WED"] = 2.0
                coupon_dict["USABLE_DATE_THU"] = 2.0
                coupon_dict["USABLE_DATE_FRI"] = 2.0
                coupon_dict["USABLE_DATE_SAT"] = 2.0
                coupon_dict["USABLE_DATE_SUN"] = 2.0
                coupon_dict["USABLE_DATE_HOLIDAY"] = 2.0
                coupon_dict["USABLE_DATE_BEFORE_HOLIDAY"] = 2.0

        feat_list = [coupon_dict["CAPSULE_TEXT"], coupon_dict["GENRE_NAME"], coupon_dict["PRICE_RATE"], coupon_dict["CATALOG_PRICE"], coupon_dict["DISCOUNT_PRICE"], coupon_dict["DISPPERIOD"], coupon_dict["VALIDPERIOD"], coupon_dict["USABLE_DATE_MON"], coupon_dict["USABLE_DATE_TUE"], coupon_dict["USABLE_DATE_WED"], coupon_dict["USABLE_DATE_THU"], coupon_dict["USABLE_DATE_FRI"], coupon_dict["USABLE_DATE_SAT"], coupon_dict["USABLE_DATE_SUN"], coupon_dict["USABLE_DATE_HOLIDAY"], coupon_dict["USABLE_DATE_BEFORE_HOLIDAY"], coupon_dict["large_area_name"], coupon_dict["ken_name"], coupon_dict["small_area_name"]]

        capsule_text_count, capsule_text_count_norm = getCountFromDict(coupon_dict["CAPSULE_TEXT"], capsule_text_dict)
        feat_list.extend([capsule_text_count, capsule_text_count_norm])

        genre_name_count, genre_name_count_norm = getCountFromDict(coupon_dict["GENRE_NAME"], genre_name_dict)
        feat_list.extend([genre_name_count, genre_name_count_norm])

        large_area_name_count, large_area_name_count_norm = getCountFromDict(coupon_dict["large_area_name"], coupon_large_area_name_dict)
        feat_list.extend([large_area_name_count, large_area_name_count_norm])

        small_area_name_count, small_area_name_count_norm = getCountFromDict(coupon_dict["small_area_name"], coupon_small_area_name_dict)
        feat_list.extend([small_area_name_count, small_area_name_count_norm])

        ken_name_count, ken_name_count_norm = getCountFromDict(coupon_dict["ken_name"], coupon_ken_name_dict)
        feat_list.extend([ken_name_count, ken_name_count_norm])

        price_rate_out_list = getMinMaxMeanFromList(coupon_dict["PRICE_RATE"], price_rate_list)
        feat_list.extend( price_rate_out_list )

        catalog_price_out_list = getMinMaxMeanFromList(coupon_dict["CATALOG_PRICE"], catalog_price_list)
        feat_list.extend( catalog_price_out_list )

        discount_price_out_list = getMinMaxMeanFromList(coupon_dict["DISCOUNT_PRICE"], discount_price_list)
        feat_list.extend( discount_price_out_list )

        dispperiod_out_list = getMinMaxMeanFromList(coupon_dict["DISPPERIOD"], dispperiod_list)
        feat_list.extend( dispperiod_out_list )

        monday_count, monday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_MON"], usable_date_mon_list)
        feat_list.extend([monday_count, monday_count_norm])

        tuesday_count, tuesday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_TUE"], usable_date_tue_list)
        feat_list.extend([tuesday_count, tuesday_count_norm])

        wednesday_count, wednesday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_WED"], usable_date_wed_list)
        feat_list.extend([wednesday_count, wednesday_count_norm])

        thursday_count, thursday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_THU"], usable_date_thu_list)
        feat_list.extend([thursday_count, thursday_count_norm])

        friday_count, friday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_FRI"], usable_date_fri_list)
        feat_list.extend([friday_count, friday_count_norm])

        saturday_count, saturday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_SAT"], usable_date_sat_list)
        feat_list.extend([saturday_count, saturday_count_norm])

        sunday_count, sunday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_SUN"], usable_date_sun_list)
        feat_list.extend([sunday_count, sunday_count_norm])

        holiday_count, holiday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_HOLIDAY"], usable_date_hol_list)
        feat_list.extend([holiday_count, holiday_count_norm])

        before_holiday_count, before_holiday_count_norm = getCountFromDict(coupon_dict["USABLE_DATE_BEFORE_HOLIDAY"], usable_date_before_hol_list)
        feat_list.extend([before_holiday_count, before_holiday_count_norm])

        return feat_list, feat_header

if __name__ == "__main__":
        model_data_path = "../../Data/Model1/"
        full_data_path = "../../Data/"

        # file_names #
        user_file = full_data_path + "user_list.csv"
        coupon_list_train_file = model_data_path + "coupon_list_train.csv"
        coupon_list_feature_file = model_data_path + "coupon_list_feature.csv"
        coupon_detail_train_file = model_data_path + "coupon_detail_train.csv"
        coupon_detail_feature_file = model_data_path + "coupon_detail_feature.csv"
        model_start_date = datetime.date(2012, 06, 17)  # (year, month, day)
        model_end_date = datetime.date(2012, 06, 23)

        # getting User Dict from user file #
        print "Getting User Dict.."
        user_dict = getUserDict(user_file)

        # getting the coupons used for train and features #
        print "Getting Coupon Dict.."
        coupon_list_train_dict = getCouponDict(coupon_list_train_file)
        coupon_list_feature_dict = getCouponDict(coupon_list_feature_file)

	# getting coupons daywise #
	daywise_coupon_list_dict = getDayWiseCoupons(coupon_list_feature_file)

	# getting the DV Dict of that has purchase combination of userid and coupon id #
        print "Getting DV Dict..."
        dv_dict = getDVDict(coupon_detail_train_file, coupon_list_train_dict.keys())

        # getting the dict of past coupon purcahse details of user from coupon_detail #
        print "Getting Coupon purchase details.."
        coupon_purchase_detail_dict = getCouponPurchaseDict(coupon_detail_feature_file)

	# preparing IDVs #
	print "Preparing IDVs..."
	out_file = csv.writer(open("train_idvs.csv","w"))
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
			user_features, user_features_header = getUserFeatures(user_dict[user_id], date_before_purchase_date)

			# getting the new history list and getting user_hist features based on it #
			new_coupon_purchase_detail_userid_list = []
			for coupon_purchase_detail in coupon_purchase_detail_userid_list[:ind]:
				if  datetime.datetime.strptime(coupon_purchase_detail['I_DATE'], "%Y-%m-%d %H:%M:%S").date() < date_before_purchase_date:
					new_coupon_purchase_detail_userid_list.append(coupon_purchase_detail)
			#print new_coupon_purchase_detail_userid_list
			user_hist_features, user_hist_features_header, master_list = getUserHistFeatures(new_coupon_purchase_detail_userid_list, coupon_list_feature_dict, model_start_date)
		
			# getting coupon for dv = 1 #
			coupon_features, coupon_features_header = getCouponFeatures(coupon_list_feature_dict[purchase_coupon], master_list)
			dv_value = 1
			if out_row_count == 0:
                                out_header = ["USER_ID_hash", "COUPON_ID_hash"]+ user_features_header + user_hist_features_header + coupon_features_header + ["DV"]
                                out_header_len = len(out_header)
                                out_file.writerow( out_header )
			out_row = [user_id, purchase_coupon] + user_features + user_hist_features + coupon_features + [dv_value]
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
					coupon_features, coupon_features_header = getCouponFeatures(coupon_list_feature_dict[non_purchased_coupon], master_list)	
					dv_value = 0
					out_row = [user_id, non_purchased_coupon] + user_features + user_hist_features + coupon_features + [dv_value]
		                        assert len(out_row) == out_header_len
                		        out_file.writerow( out_row )
		                        out_row_count += 1
			
		user_count += 1
		if user_count % 200 == 0:
			print "Processed Users : ", user_count
