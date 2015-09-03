#### Order of files to run ####
* splitCoupon.py
* splitCouponDetail.py
* splitCouponVisit.py

These three files will split the given train set coupons into dev-val sample. Last week in the training set will be 
taken as validation and the other weeks are included in dev sample

* buildIDV_dev.py
* buildIDV_val.py
* buildIDV_train.py
* buildIDV_test.py

These four files will create the IDVs for dev, val, train and test sample respectively. 
For model tuning, we can develop the model on dev idvs and validate them on val idvs.
For final model build, we can use train idvs to build the model and test idvs to get the test set predictions

* buildModel_xgb.py

Code to build an xgb model in the dev sample alone with cross validation. 
In next version, this should be modified so that model is built on dev sample and validated on val sample

* finalModel_xgb.py
* postProcess.py

finalModel_xgb code will build the model in train idvs and make predictions for test idvs.
postProcess code will then post process the test predictions to get the top 10 coupons for each user_id.

In this version, I have pushed the feature creation part into a separate file *feature_extraction.py* 
so that all buildIDVs code can call the same function unlike the earlier versions. 
Also added comments in the feature_extraction.py code for easy understanding.  

