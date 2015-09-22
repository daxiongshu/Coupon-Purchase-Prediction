I have a trick that improves cv a lot but not lb.
#I improve our best cv from 0.0267 to 0.0274, but LB from 0.0112 to 0.0104

step1: find bad users in validation result. Badusers are defined as: the ones who bought coupons and none of our predictions for this user is correct

step2: count coupons in validation prediction result. Simply count each coupon in the validation result

step3: find the most popular coupons. Sort the coupons by count and save the top 10 coupons with most count

step4: replace the bad users' predictions with the top 10 popular coupons



For lb, we don't know the real bad users, so I assume the bad users in validation are the bad users in test

then I found popular coupons in our best sub, the other procedures are the same

Is it because my assumption is not valid?
