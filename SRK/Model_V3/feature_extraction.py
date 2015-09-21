# -*- coding: utf-8 -*-
import csv
import random
import numpy as np
import pandas as pd
import datetime

from config import unique_genre_name, unique_capsule_text, unique_large_area_name, unique_small_area_name, unique_ken_name, unique_pref_name

def getUserDict(user_file):
	"""
	Function to get the user dict from the user_list.csv file
	It returns a user_dict dictionary where user_id is the key and the characteristics of user as values for the key in form of dict
	"""
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
	"""
	Function to get the coupon dict from the input coupon_list*.csv file
	It returns a dictionary where coupon_id is the key and all other characteristics of coupon as values for the key in form of dict
	"""
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
	"""
	Function to get the coupon dict from input coupon_list*csv file 
	It returns a dictionary where DISPFROM (coupon start date) is the key and all other characteristics of coupon as values for the key in form of list of dicts
	"""
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
	"""
	Fucntion to get the coupon purchase details from the historical data
	It returns a dict where user_id is the key and all his past purchases as values in the form of list of dicts
	"""
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
	"""
	"""
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
	"""
	Fucntion to get the dv for the given user_id and coupon_id combination, if the given user_id and coupon_id is present in the past purchase DV is returned as 1 else 0
	"""
        dv = 0
        if dv_dict.has_key(user_id):
                coupon_list = dv_dict[user_id]
                if coupon_id in coupon_list:
                        dv = 1
        return dv


def getUserFeatures(input_dict, prefecture_location_dict, assessment_date):
	"""
	Fucntion to get the features related to an user
	@input_dict : dict containing the characteristics of the user
	@assessment date : date at which the assessment is made
	It returns the feature list and the header

	Features are:
	UserGender : Whether the user is male or female (f=1, m=0)
	UserAge : Age of the user
	UserPrefName : PREF_NAME of the user as given in user_list.csv
	UserDaysSinceRegistered : Number of days since the user has registered
	UserRegisteredMonth : Month of user registry
	UserRegisteredYear : Year of user registry
	UserWithdrawn : Whether the user has withdrawn or not
	"""
        header = ['UserGender', 'UserAge', 'UserPrefName', 'UserPrefLat', 'UserPrefLon', 'UserDaysSinceRegistered', 'UserRegisteredMonth', 'UserRegisteredYear', 'UserWithdrawn']
        # getting gender variable #
        if input_dict['SEX_ID'] == 'f':
                feat_list = [1]
        else:
                feat_list = [0]

        # getting age variable #
        feat_list.append(float(input_dict['AGE']))

        # getting pref_name variable #
	pref_name = input_dict['PREF_NAME']
        feat_list.append(pref_name)
	lat = 0
	lon = 0
	if prefecture_location_dict.has_key(pref_name):
		lat = prefecture_location_dict[pref_name]['LATITUDE']
		lon = prefecture_location_dict[pref_name]['LONGITUDE']
	feat_list.extend([lat,lon])

        # getting reg month and year #
        reg_date = input_dict['REG_DATE']
        reg_date = datetime.datetime.strptime(reg_date, "%Y-%m-%d %H:%M:%S").date()
	feat_list.append((assessment_date - reg_date).days)
        feat_list.append( reg_date.month )
        feat_list.append( reg_date.year )

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

def getUserHistFeatures(transaction_list, coupon_dict, model_start_date, purchase_date):
	"""
	Fucntion to get the historical features of the user based on the available data till the given point
	@transaction_list : It has all past transactions of the customer till the point of observation in the form of list of dicts
	@coupon_dict : dict containing details about the coupons with coupon_id as key
	@model_start_date : date at which the val/test period starts
	@purchase_date : date of purchase of the coupon
	"""
        feat_header = ["NoOfPurchases", "DaysSinceLastPurchase", "NoOfPurchasesLastweek", "NoOfPurchasesLast15Days", "NoOfPurchasesLast30Days", "NoOfPurchasesLast60Days", "NoOfPurchasesLast90Days", "NoOfPurchasesLast180Days",  "DaysSincePrevPurchase", "NoOfPurchasesPrevweek", "NoOfPurchasesPrev15Days", "NoOfPurchasesPrev30Days", "NoOfPurchasesPrev60Days", "NoOfPurchasesPrev90Days", "NoOfPurchasesPrev180Days"]

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
	last_oneeightydays_purchase = 0
	days_since_prev_purchase = 9999
	prev_week_purchase = 0
        prev_fifteendays_purchase = 0
        prev_thirtydays_purchase = 0
        prev_sixtydays_purchase = 0
        prev_nintydays_purchase = 0
        prev_oneeightydays_purchase = 0
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
		if diff_days <= 180:
                        last_oneeightydays_purchase += 1
		
		diff_days = (purchase_date - datetime.datetime.strptime(transaction['I_DATE'], "%Y-%m-%d %H:%M:%S").date()).days
                if diff_days < days_since_last_purchase:
                        days_since_prev_purchase = diff_days
                if diff_days <= 7:
                        prev_week_purchase += 1
                if diff_days <= 15:
                        prev_fifteendays_purchase += 1
                if diff_days <= 30:
                        prev_thirtydays_purchase += 1
                if diff_days <= 60:
                        prev_sixtydays_purchase += 1
                if diff_days <= 90:
                        prev_nintydays_purchase += 1
                if diff_days <= 180:
                        prev_oneeightydays_purchase += 1

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
                        usable_date_mon_list[3.0] = usable_date_mon_list.get( 3.0,0 ) + 1
                        usable_date_tue_list[3.0] = usable_date_tue_list.get( 3.0,0 ) + 1
                        usable_date_wed_list[3.0] = usable_date_wed_list.get( 3.0,0 ) + 1
                        usable_date_thu_list[3.0] = usable_date_thu_list.get( 3.0,0 ) + 1
                        usable_date_fri_list[3.0] = usable_date_fri_list.get( 3.0,0 ) + 1
                        usable_date_sat_list[3.0] = usable_date_sat_list.get( 3.0,0 ) + 1
                        usable_date_sun_list[3.0] = usable_date_sun_list.get( 3.0,0 ) + 1
                        usable_date_hol_list[3.0] = usable_date_hol_list.get( 3.0,0 ) + 1
                        usable_date_before_hol_list[3.0] = usable_date_before_hol_list.get( 3.0,0 ) + 1

        feat_list.extend([days_since_last_purchase, last_week_purchase, last_fifteendays_purchase, last_thirtydays_purchase, last_sixtydays_purchase, last_nintydays_purchase, last_oneeightydays_purchase, days_since_prev_purchase, prev_week_purchase, prev_fifteendays_purchase, prev_thirtydays_purchase, prev_sixtydays_purchase, prev_nintydays_purchase, prev_oneeightydays_purchase])
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
	"""
	Function to get the min, max and mean value from a given list and also to check the presence of given input value in the list
	"""
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
	"""
	Function to get features related to usable_day_* columns present in the input file
	This functions returns the count and normalized count of coupons which has similar usable_day_* features that the customer has bought in the past
	"""
        count = 0
        normalized_count = 0
        if len(usable_date_list) > 0 :
                for value in usable_date_list:
                        if float(val) == value:
                                count += 1
                normalized_count = count / float(len(usable_date_list))
        return count, normalized_count

def getDummyVars(input_dict, feature_list, prefix="DummyVars_"):
	"""
	This function is to create dummy varibales for categorical variables
	feature_list contains all the unique features for dummy vars creation
	input_dict contains the features that are seen for the given customer's purchase
	"""
	header_list = []
	feat_list = []
	for ind,feat in enumerate(feature_list):
		header_list.append(prefix+str(ind))
		if input_dict.has_key(feat):
			feat_list.append(input_dict[feat])
		else:
			feat_list.append(0)
	return feat_list, header_list	

def getDummyVarsDays(input_dict, prefix="DummyVars_"):
	"""
	Functiont to get the dummy variables for UseableDate features
	"""
        header_list = []
        feat_list = []
        for ind,feat in enumerate([0.0, 1.0, 2.0, 3.0]):
                header_list.append(prefix+str(ind))
                if input_dict.has_key(feat):
                        feat_list.append(input_dict[feat])
                else:
                        feat_list.append(0)
        return feat_list, header_list


def getCouponFeatures(coupon_dict, master_list):
	"""
	Fucntion to get the features related to coupons
	"""
        purchase_small_area_name_dict, capsule_text_dict, genre_name_dict, coupon_large_area_name_dict, coupon_small_area_name_dict, coupon_ken_name_dict, price_rate_list, catalog_price_list, discount_price_list, dispperiod_list, valid_period_list, usable_date_mon_list, usable_date_tue_list, usable_date_wed_list, usable_date_thu_list, usable_date_fri_list, usable_date_sat_list, usable_date_sun_list, usable_date_hol_list, usable_date_before_hol_list = master_list

        feat_header = ["CouponCapsuleText", "CouponGenreName", "CouponPriceRate", "CouponCatalogPrice", "CouponDiscountPrice", "CouponDispPeriod", "CouponValidPeriod", "CouponUsableMon", "CouponUsableTue", "CouponUsableWed", "CouponUsableThu", "CouponUsableFri", "CouponUsableSat", "CouponUsableSun", "CouponUsableHol", "CouponUsableBeforeHol", "CouponLargeAreaName", "CouponKenName", "CouponSmallAreaName", "CapsuleTextCount", "CapsuleTextCountNorm", "GenreNameCount", "GenreNameCountNorm", "LargeAreaNameCount", "LargeAreaNameCountNorm", "SmallAreaNameCount", "SmallAreaNameCountNorm", "KenNameCount","KenNameCountNorm", "PriceRateMin", "PriceRateMax", "PriceRateMean", "PriceRateBetMeanMax", "PriceRateBetMinMean", "PriceRateGrtMax", "PriceRateLessMin", "CatalogPriceMin", "CatalogPriceMax", "CatalogPriceMean", "CatalogPriceBetMeanMax", "CatalogPriceBetMinMean", "CatalogPriceGrtMax", "CatalogPriceLessMin", "DiscountPriceMin", "DiscountPriceMax", "DiscountPriceMean", "DiscountPriceBetMeanMax", "DiscountPriceBetMinMean", "DiscountPriceGrtMax", "DiscountPriceLessMin", "DispPeriodMin", "DispPeriodMax", "DispPeriodMean", "DispPeriodBetMeanMax", "DispPeriodBetMinMean", "DispPeriodGrtMax", "DispPeriodLessMin", "MondayCount", "MondayCountNorm", "TuesdayCount", "TuesdayCountNorm", "WednesdayCount", "WednesdayCountNorm", "ThursdayCount", "ThursdayCountNorm", "FridayCount", "FridayCountNorm", "SaturdayCount", "SaturdayCountNorm", "SundayCount", "SundayCountNorm", "HolidayCount", "HolidayCountNorm", "BeforeHolidayCount", "BeforeHolidayCountNorm"]

        if coupon_dict['USABLE_DATE_MON'] in ('','NA'):
                coupon_dict["USABLE_DATE_MON"] = 3.0
                coupon_dict["USABLE_DATE_TUE"] = 3.0
                coupon_dict["USABLE_DATE_WED"] = 3.0
                coupon_dict["USABLE_DATE_THU"] = 3.0
                coupon_dict["USABLE_DATE_FRI"] = 3.0
                coupon_dict["USABLE_DATE_SAT"] = 3.0
                coupon_dict["USABLE_DATE_SUN"] = 3.0
                coupon_dict["USABLE_DATE_HOLIDAY"] = 3.0
                coupon_dict["USABLE_DATE_BEFORE_HOLIDAY"] = 3.0

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

	var_list, var_header = getDummyVars(capsule_text_dict, unique_capsule_text, prefix="CapsuleText_")
	feat_header.extend(var_header)
	feat_list.extend(var_list)

	var_list, var_header = getDummyVars(genre_name_dict, unique_genre_name, prefix="GenreName_")
	feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVars(coupon_large_area_name_dict, unique_large_area_name, prefix="LargeAreaName_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVars(coupon_small_area_name_dict, unique_small_area_name, prefix="SmallAreaName_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVars(coupon_ken_name_dict, unique_ken_name, prefix="KenName_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_mon_list, prefix="UsableMonday_")
	feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_tue_list, prefix="UsableTuesday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_wed_list, prefix="UsableWednesday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_thu_list, prefix="UsableThursday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_fri_list, prefix="UsableFriday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_sat_list, prefix="UsableSaturday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_sun_list, prefix="UsableSunday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_hol_list, prefix="UsableHoliday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)

	var_list, var_header = getDummyVarsDays(usable_date_before_hol_list, prefix="UsableBeforeHoliday_")
        feat_header.extend(var_header)
        feat_list.extend(var_list)
	
        return feat_list, feat_header


def getPrefectureLocationDict(prefecture_location_file):
	"""
	This function is to get the prefecture location latitude and longitude
	"""
	file_handle = open(prefecture_location_file,'rb')
        file_reader = csv.DictReader(file_handle)

        prefec_location_dict = {}
        counter = 0
        for row in file_reader:
                prefec_location_dict[row['PREF_NAME']] = row
                counter += 1
        assert len(prefec_location_dict.keys()) == counter

        file_handle.close()
        return prefec_location_dict

def getCouponAreaDict(coupon_area_file):
	"""
	This function is to get the coupon area details of the coupon ids 
	Small_area_name and Pref_name are stored in two separate lists which could be used for searching later
	"""
	file_handle = open(coupon_area_file,'rb')
        file_reader = csv.DictReader(file_handle)

        coupon_area_dict = {}
        for row in file_reader:	
                temp_dict = coupon_area_dict.get(row['COUPON_ID_hash'], {'SMALL_AREA_NAME':[],'PREF_NAME':[]})
		temp_dict['SMALL_AREA_NAME'].append(row['SMALL_AREA_NAME'])
		temp_dict['PREF_NAME'].append(row['PREF_NAME'])
		coupon_area_dict[row['COUPON_ID_hash']] = temp_dict

	# converting list to set for faster search #
	for key in coupon_area_dict:
		coupon_area_dict[key]['SMALL_AREA_NAME'] = set(coupon_area_dict[key]['SMALL_AREA_NAME'])
		coupon_area_dict[key]['PREF_NAME'] = set(coupon_area_dict[key]['PREF_NAME'])

        file_handle.close()
        return coupon_area_dict

def getCouponVisitDict(coupon_visit_file):
	file_handle = open(coupon_visit_file,'rb')
        file_reader = csv.DictReader(file_handle)

        coupon_visit_dict = {}
        for row in file_reader:
		user_id = row['USER_ID_hash']
		temp_dict = coupon_visit_dict.get(user_id, {})
		i_date = datetime.datetime.strptime(row['I_DATE'], "%Y-%m-%d %H:%M:%S").toordinal()
		temp_dict[i_date] = row
		coupon_visit_dict[user_id] = temp_dict

        file_handle.close()
        return coupon_visit_dict

def getCouponAreaFeatures(user_dict, coupon_area_dict, coupon_id):
	coupon_area_features_header = ["coupon_user_prefname_match", "coupon_smallarea_count", "coupon_prefname_count"]
	user_prefname = user_dict["PREF_NAME"]
	area_dict = coupon_area_dict.get(coupon_id, {'SMALL_AREA_NAME':[],'PREF_NAME':[]})

	if user_prefname in area_dict['PREF_NAME']:
		coupon_user_prefname_match = 1
	else:
		coupon_user_prefname_match = 0
	coupon_smallarea_count = len(area_dict['SMALL_AREA_NAME'])
	coupon_prefname_count = len(area_dict['PREF_NAME'])

	coupon_area_features = [coupon_user_prefname_match, coupon_smallarea_count, coupon_prefname_count]

	return coupon_area_features, coupon_area_features_header
		

def getUserVisitFeatures(user_id, coupon_visit_dict, date_before_purchase_date):
	user_visit_features_header = ['no_visits_7days', 'no_visits_15days', 'no_visits_30days', 'no_visits_60days', 'no_visits_older', 'no_sessions_7days', 'no_sessions_15days', 'no_sessions_30days', 'no_sessions_60days', 'no_sessions_older', 'no_referrer_7days', 'no_referrer_15days', 'no_referrer_30days', 'no_referrer_60days', 'no_referrer_older', 'no_coupons_7days', 'no_coupons_15days', 'no_coupons_30days', 'no_coupons_60days', 'no_coupons_older', 'no_pages_7days', 'no_pages_15days', 'no_pages_30days', 'no_pages_60days', 'no_pages_older']

	no_visits_7days = 0
	no_visits_15days = 0
	no_visits_30days = 0
	no_visits_60days = 0
	no_visits_older = 0
	no_sessions_7days = 0
	no_sessions_15days = 0
	no_sessions_30days = 0
	no_sessions_60days = 0
	no_sessions_older = 0
	no_referrer_7days = 0
	no_referrer_15days = 0
	no_referrer_30days = 0
        no_referrer_60days = 0
	no_referrer_older = 0
	no_coupons_7days = 0
	no_coupons_15days = 0
	no_coupons_30days = 0
        no_coupons_60days = 0
	no_coupons_older = 0
	no_pages_7days = 0
	no_pages_15days = 0
	no_pages_30days = 0
        no_pages_60days = 0
	no_pages_older = 0

	user_dict = coupon_visit_dict.get(user_id,{})
	if user_dict:
		ordinaltime_list = list(user_dict.keys())
		ordinaltime_list.sort()
		cutoff_end = date_before_purchase_date.toordinal()
		cutoff_7days = (date_before_purchase_date - datetime.timedelta(days=7)).toordinal()
		cutoff_15days = (date_before_purchase_date - datetime.timedelta(days=15)).toordinal()
		cutoff_30days = (date_before_purchase_date - datetime.timedelta(days=30)).toordinal()
		cutoff_60days = (date_before_purchase_date - datetime.timedelta(days=60)).toordinal()
		sessions_7days = []
		sessions_15days = []
		sessions_30days = []
		sessions_60days = []
		sessions_older = []
		referrer_7days = []
		referrer_15days = []
		referrer_30days = []
		referrer_60days = []
		referrer_older = []
		coupons_7days = []
		coupons_15days = []
		coupons_30days = []
		coupons_60days = []
		coupons_older = []
		pages_7days = []
		pages_15days = []
		pages_30days = []
                pages_60days = []
		pages_older = []

		for time_value in ordinaltime_list:
			if time_value > cutoff_end:
				break
			elif time_value >= cutoff_7days and time_value < cutoff_end:
				no_visits_7days += 1
				sessions_7days.append( user_dict[time_value]["SESSION_ID_hash"] )
				referrer_7days.append( user_dict[time_value]["REFERRER_hash"] )
				coupons_7days.append ( user_dict[time_value]["VIEW_COUPON_ID_hash"] ) 
				pages_7days.append( user_dict[time_value]["PAGE_SERIAL"] )
			elif time_value >= cutoff_15days and time_value < cutoff_7days:
                                no_visits_15days += 1
				sessions_15days.append( user_dict[time_value]["SESSION_ID_hash"] )
                                referrer_15days.append( user_dict[time_value]["REFERRER_hash"] )
				coupons_15days.append ( user_dict[time_value]["VIEW_COUPON_ID_hash"] )
                                pages_15days.append( user_dict[time_value]["PAGE_SERIAL"] )
			elif time_value >= cutoff_30days and time_value < cutoff_15days:
                                no_visits_30days += 1
				sessions_30days.append( user_dict[time_value]["SESSION_ID_hash"] )
                                referrer_30days.append( user_dict[time_value]["REFERRER_hash"] )
				coupons_30days.append ( user_dict[time_value]["VIEW_COUPON_ID_hash"] )
                                pages_30days.append( user_dict[time_value]["PAGE_SERIAL"] )
			elif time_value >= cutoff_60days and time_value < cutoff_30days:
                                no_visits_60days += 1
				sessions_60days.append( user_dict[time_value]["SESSION_ID_hash"] )
                                referrer_60days.append( user_dict[time_value]["REFERRER_hash"] )
				coupons_60days.append ( user_dict[time_value]["VIEW_COUPON_ID_hash"] )
                                pages_60days.append( user_dict[time_value]["PAGE_SERIAL"] )
			else:
				no_visits_older += 1
				sessions_older.append( user_dict[time_value]["SESSION_ID_hash"] )
                                referrer_older.append( user_dict[time_value]["REFERRER_hash"] )
				coupons_older.append ( user_dict[time_value]["VIEW_COUPON_ID_hash"] )
                                pages_older.append( user_dict[time_value]["PAGE_SERIAL"] )

		no_sessions_7days = len(set(sessions_7days))
		no_sessions_15days = len(set(sessions_15days))
		no_sessions_30days = len(set(sessions_30days))
		no_sessions_60days = len(set(sessions_60days))
		no_sessions_older = len(set(sessions_older))
		no_referrer_7days = len(set(referrer_7days))
		no_referrer_15days = len(set(referrer_15days))
		no_referrer_30days = len(set(referrer_30days))
		no_referrer_60days = len(set(referrer_60days))
		no_referrer_older = len(set(referrer_older))
		no_coupons_7days = len(set(coupons_7days))
		no_coupons_15days = len(set(coupons_15days))
		no_coupons_30days = len(set(coupons_30days))
                no_coupons_60days = len(set(coupons_60days))
		no_coupons_older = len(set(coupons_older))
		no_pages_7days = len(set(pages_7days))
		no_pages_15days = len(set(pages_15days))
		no_pages_30days = len(set(pages_30days))
		no_pages_60days = len(set(pages_60days))
		no_pages_older = len(set(pages_older))

	user_visit_features = [no_visits_7days, no_visits_15days, no_visits_30days, no_visits_60days, no_visits_older, no_sessions_7days, no_sessions_15days, no_sessions_30days, no_sessions_60days, no_sessions_older, no_referrer_7days, no_referrer_15days, no_referrer_30days, no_referrer_60days, no_referrer_older, no_coupons_7days, no_coupons_15days, no_coupons_30days, no_coupons_60days, no_coupons_older, no_pages_7days, no_pages_15days, no_pages_30days, no_pages_60days, no_pages_older]

	return user_visit_features, user_visit_features_header	
