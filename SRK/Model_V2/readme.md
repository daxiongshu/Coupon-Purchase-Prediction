#### New folder with validation codes ####

Given train data is first split into two samples (dev and val sample based on timeline) for internal validation purpose
 1. dev sample - coupons that are released till 16th June, 2012
 2. val sample - coupons that are released from 17th June, 2012 to 23rd June, 2012

Files which help to do the splitting the train data are as follows. Create a new folder 'Model2' inside the data folder and the new files will be written inside the 'Model2' folder.
 1. splitCoupon.py
 2. splitCouponDetail.py
 3. splitCouponVisit.py

Also we need to get the DV for the validation sample. We will use the output file when we need to compute the MAP@10 value of validation sample. File to produce the val DV is
 * getDV_val.py

Next part is the feature creation. We will build IDVs on four samples - dev, val, train and test. 
Models are built on the dev sample and validated on the val sample. Models with best params are finally built again on the train sample and predicted on the test sample.
 1. buildIDV_dev.py - to build IDVs on the dev sample based on the past purchases present in dev
 2. buildIDV_val.py - to build IDVs on val sample for all the coupon-user combination of val week
 3. buildIDV_train.py - to build IDVs on the train sample based on past purchases
 4. buildIDV_test.py - to build IDVs on test sample 

Then comes the model building part. We need to find the best params for the model through cross validation (xgboost in this case - we could change the type of modeling algorithm). AUC is used as the measure for param tuning. The code for this is
 * buildModel_xgb.py

Once we get the good params from cross validation, we could use those params to build the final model. This code outputs the predicted probabilities for all coupon-user combinations of test week. The model code for final model is 
 * finalModel_xgb.py

Next step is to post process the output probability file to get the top 10 coupons for a given user. Code for getting this is
 * postProcess.py

A new postProcess code where some weightage is given based on the release date of the coupons is present in
 * postProcess_v2.py

* Validation codes are present in the validation folder with a readme file inside *
