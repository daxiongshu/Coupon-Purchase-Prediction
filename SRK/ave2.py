import pandas as pd
name='Prediction'
s1=pd.read_csv('test_predictions_xgb.csv',index_col=0)
s2=pd.read_csv('ftrl1sub_prob.csv',index_col=0)

s1[name]=(s1[name]*0.95+s2[name]*0.05)
s1.to_csv('ave2_prob.csv')
