# val.csv is the validation result
# sub.csv is the corresponding submission

python findBadUser.py val.csv
python findPopular_val.py val.csv
#python replace.py val.csv # you can test the score by modifying the replace.py
#popular=pickle.load(open('popular_sub.p')) -> popular=pickle.load(open('popular_val.p'))
python findPopular_sub.py sub.csv
python replace.py sub.py
