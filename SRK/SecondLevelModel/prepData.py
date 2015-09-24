import numpy as np
import pandas as pd

if __name__ == "__main__":
        data_path = "./InputFiles/"
        test_file_names = ["test_predictions_rf_est200_dep25_leaf7_feat3_seed0_trainseed1234.csv","test_predictions_rf_est200_dep25_leaf7_feat3_seed0_trainseed1234_d3.csv","test_predictions_xgb_dep14_child18_eta05_round450_seed0_trainseed1234.csv","test_predictions_xgb_dep14_child18_eta05_round450_seed1_trainseed4567.csv","test_predictions_xgb_dep14_child18_eta05_round450_seed2_trainseed1234_d3.csv","test_predictions_xgb_dep14_child18_eta05_round450_seed4_trainseed4567_d3.csv","test_predictions_xgb_dep18_child50_eta05_round450_seed3_trainseed1234_d3.csv","test_predictions_xgb_dep18_child50_eta05_round450_seed3_trainseed4567_d3.csv"]
        val_file_names = ["val_predictions_rf_est200_dep25_leaf7_feat3_seed0_devseed1234.csv","val_predictions_rf_est200_dep25_leaf7_feat3_seed0_devseed1234_d3.csv","val_predictions_xgb_dep14_child18_eta05_round450_seed0_devseed1234.csv","val_predictions_xgb_dep14_child18_eta05_round450_seed1_devseed4567.csv","val_predictions_xgb_dep14_child18_eta05_round450_seed2_devseed1234_d3.csv","val_predictions_xgb_dep14_child18_eta05_round450_seed4_devseed4567_d3.csv","val_predictions_xgb_dep18_child50_eta05_round450_seed3_devseed1234_d3.csv","val_predictions_xgb_dep18_child50_eta05_round450_seed3_devseed4567_d3.csv"]

        val_file = "../PurchaseModel_v3/val_idvs.csv"
        test_file = "../PurchaseModel_v3/test_idvs.csv"
        cols_to_read = ["USER_ID_hash", "COUPON_ID_hash", "DV"]

        #val_df = pd.read_csv(val_file, usecols=cols_to_read)
        #print val_df.shape

        #for index, file_name in enumerate(val_file_names):
        #       print "Raeading file : ", file_name
        #       val_df["Preds"+str(index)] = np.array( (pd.read_csv(data_path+file_name))["Prediction"].apply(lambda x : str(np.round(x,6))) )
        #val_df.to_csv("valdata_secondlevel.csv", index=False)

        test_df = pd.read_csv(test_file, usecols=cols_to_read)
        print test_df.shape

        for index, file_name in enumerate(test_file_names):
                print "Raeading file : ", file_name
                test_df["Preds"+str(index)] = np.array( (pd.read_csv(data_path+file_name))["Prediction"].apply(lambda x : str(np.round(x,6))) )
        test_df.to_csv("testdata_secondlevel.csv", index=False)
