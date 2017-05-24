import numpy as np
import pandas as pd
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets

# setup
c = 7
dir = 'checkpoint_1-2_'+str(c)
data = np.load(dir+'/accuracy.npz')
indicators = np.load(dir+'/indicators.npy').item()

# read test labels
mnist = read_data_sets("data", one_hot=True, reshape=False, validation_size=0)
y = np.argmax(mnist.test.labels, 1)

# read prediction date
a_test = data['a_test'] #[101,1]
y_ = data['test_prediction'][np.argmax(a_test)] #[10000*n,11]
n = len(indicators)

# Mark prediction data and save it in csv file
#  'True_indicator' 1:prediction is 10th categary, 2:prediction doesn't agree with indicator, 3: prediction agrees with indicator, 4: prediction agrees with indicator and is right
# 'False_indicator' 1:prediction is 10th categary, 2:prediction doesn't agree with indicator, 3: prediction agrees with indicator
cols = pd.MultiIndex.from_tuples([("True_label", "True_label"), ("True_indicator", "True_indicator")] + [('False_indicators', str(i)) for i in range(n)])
y_mark = pd.DataFrame(np.zeros([10000, 1+n+1]), columns=cols)
y_mark.columns = y_mark.columns.droplevel()
for i in range(0,y_.shape[0]):
    ii = i%10000  # the iith image input
    j = i//10000 # the indicator=j
    pred = np.argmax(y_[i])
    True_label = y[ii]
    y_mark.loc[ii,'True_label'] = True_label
    # see if indicator is true or false
    if True_label in indicators[j]:
        if pred == 10:
            y_mark.loc[ii,'True_indicator'] = 1
            continue
        elif pred not in indicators[j]:
            y_mark.loc[ii,'True_indicator'] = 2
            continue
        elif pred in indicators[j]:
            y_mark.loc[ii,'True_indicator'] = 3
            if pred == True_label:
                y_mark.loc[ii,'True_indicator'] = 4
    else:
        if pred == 10:
            y_mark.loc[ii,str(j)] = 1
            continue
        elif pred not in indicators[j]:
            y_mark.loc[ii,str(j)] = 2
            continue
        elif pred in indicators[j]:
            y_mark.loc[ii,str(j)] = 3

y_mark.columns = cols
y_mark.to_csv('Prediction_mark_'+str(c)+'.csv', sep=',', encoding='utf-8')

# save prediction data in csv file
col_indicator = [ [("Indicator_"+str(j), str(i)) for i in range(11)] for j in range(n)]
col_ = []
for name in col_indicator:
    col_ += name
cols = pd.MultiIndex.from_tuples([('True_label','True_label')] + col_)
y_prediction = pd.DataFrame(np.zeros([10000, 1+n*11]), columns=cols)
y_prediction['True_label'] = y
for i in range(len(indicators)):
    y_prediction['Indicator_'+str(i)] = y_[i*10000:(i+1)*10000,:]

y_prediction.to_csv('Prediction_'+str(c)+'.csv', sep=',', encoding='utf-8')
