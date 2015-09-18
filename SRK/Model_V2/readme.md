#### New folder with validation codes ####

Given train data is first split into two samples (dev and val sample based on timeline) for internal validation purpose
 1. dev sample - coupons that are released till 16th June, 2012
 2. val sample - coupons that are released from 17th June, 2012 to 23rd June, 2012

Files which help to do the splitting the train data are as follows. Create a new folder 'Model2' inside the data folder and the new files will be written inside the 'Model2' folder.
 1. splitCoupon.py
 2. splitCouponDetail.py
 3. splitCouponVisit.py

Also we need to get the DV for the validation sample. We will use the output file when we need to compute the MAP@10 value of validation sample. File to produce the val DV is
 getDV_val.py
 
