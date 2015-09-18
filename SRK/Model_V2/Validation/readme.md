#### Codes used for validating the model ####

Once we get the best params for model building, we can get the probability values for the validation week and code for this is
 * finalModel_xgb_val.py

We can get the top 10 coupons for all users based on the probability score and the code for this is
 * postProcess_val.py

New postProcess code with weightage based on the release date is 
 * postProcess_val_v2.py

Code to compute the evaluation metric in the validation sample is
 * compute_map10_val.py
