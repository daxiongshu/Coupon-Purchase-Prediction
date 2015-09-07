Thie folder has code that reproduces sub3.csv, 0.010933 LB

no overall cv has done for this model but most customers have 0.8+ per customer auc

The idea is that, for the customers who buy "many" coupons, the per customer model works better

A possible reason is that their personal behavior/habit dominates. 

to run the model:

mkdir sub2

python rebuild_coupon_feature.py

python per-customer.py

python gensub.py


