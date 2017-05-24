import numpy as np
import pandas as pd
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets

# read test labels
mnist = read_data_sets("data", one_hot=True, reshape=False, validation_size=0)
y = np.argmax(mnist.test.labels, 1)

# read prediction date
for c in range(1,8):
    dir = 'checkpoint_1-2_'+str(c)
    data = np.load(dir+'/accuracy.npz')
    indicators = np.load(dir+'/indicators.npy').item()
    a_test = data['a_test'] #[101,1]
    y_ = data['test_prediction'][np.argmax(a_test)] #[10000*n,11]
    n = len(indicators)
    cols = [ "Indicator_"+str(i) for i in range(n)]
    y_prediction = pd.DataFrame(np.zeros([10000, n]), columns=cols)
    for i in range(n):
        y_prediction['Indicator_'+str(i)] = np.argmax( y_[i*10000:(i+1)*10000,:],1)
    true_count = 0.0
    pass_logic_check_count = 0.0
    for i in range(10000):
        critirier = y_prediction.loc[i] == 10
        if sum(critirier) != n-1:
            continue
        if y_prediction.loc[i,np.argmin(critirier)] not in indicators[int(np.argmin(critirier).split('_')[1])]:
            continue
    # 99.48% pass the logic check in case #1
        pass_logic_check_count += 1
        if y_prediction.loc[i,np.argmin(critirier)] == y[i]:
            true_count += 1
    print('case #%s'%c)
    print('The accuracy without logic is %s'%(max(a_test)))
    print('The rate of passing logic check is %s'%(pass_logic_check_count/10000))
    print('The accuracy with logic check is %s'%(true_count/10000))
    print('The accuracy after passing logic check is %s'%(true_count/pass_logic_check_count))
