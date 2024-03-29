# image + one-dimensional indicator -> nine categories + conflict category
# By Fang Wan

import tensorflow as tf
import math
import os
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
tf.set_random_seed(0)
import numpy as np
import pandas as pd

# Download images and labels into mnist.test (10K images+labels) and mnist.train (60K images+labels)
mnist = read_data_sets("data", one_hot=True, reshape=False, validation_size=0)

# input X: 28x28 grayscale images, the first dimension (None) will index the images in the mini-batch
X = tf.placeholder(tf.float32, [None, 28, 28, 1])
X2 = tf.placeholder(tf.float32, [None, 1])
# correct answers will go here
Y_ = tf.placeholder(tf.float32, [None, 11])
# variable learning rate
lr = tf.placeholder(tf.float32)

# three convolutional layers with their channel counts, and a
# fully connected layer (tha last layer has 10 softmax neurons)
K = 4  # first convolutional layer output depth
L = 8  # second convolutional layer output depth
M = 12  # third convolutional layer
N = 200  # fully connected layer

W1 = tf.Variable(tf.truncated_normal([5, 5, 1, K], stddev=0.1))  # 5x5 patch, 1 input channel, K output channels
B1 = tf.Variable(tf.ones([K])/10)
W2 = tf.Variable(tf.truncated_normal([5, 5, K, L], stddev=0.1))
B2 = tf.Variable(tf.ones([L])/10)
W3 = tf.Variable(tf.truncated_normal([4, 4, L, M], stddev=0.1))
B3 = tf.Variable(tf.ones([M])/10)

W21 = tf.Variable(tf.truncated_normal([1, 12], stddev=0.1))
B21 = tf.Variable(tf.ones([12])/10)

W4 = tf.Variable(tf.truncated_normal([7 * 7 * M, N], stddev=0.1))
B4 = tf.Variable(tf.ones([N])/10)
W5 = tf.Variable(tf.truncated_normal([N, 11], stddev=0.1))
B5 = tf.Variable(tf.ones([11])/10)

# The model
stride = 1  # output is 28x28
Y1 = tf.nn.relu(tf.nn.conv2d(X, W1, strides=[1, stride, stride, 1], padding='SAME') + B1)
stride = 2  # output is 14x14
Y2 = tf.nn.relu(tf.nn.conv2d(Y1, W2, strides=[1, stride, stride, 1], padding='SAME') + B2)
stride = 2  # output is 7x7
Y3 = tf.nn.relu(tf.nn.conv2d(Y2, W3, strides=[1, stride, stride, 1], padding='SAME') + B3)

Y21 = tf.nn.relu(tf.matmul(X2, W21) + B21)
Y21 = tf.reshape(Y21,[-1, 1, 1, 12])
Y21 = tf.tile(Y21, [1, 7, 7, 1])
Y3 = Y3 + Y21

# reshape the output from the third convolution for the fully connected layer
YY = tf.reshape(Y3, shape=[-1, 7 * 7 * M])

Y4 = tf.nn.relu(tf.matmul(YY, W4) + B4)
Ylogits = tf.matmul(Y4, W5) + B5
Y = tf.nn.softmax(Ylogits)

# cross-entropy loss function (= -sum(Y_i * log(Yi)) ), normalised for batches of 100  images
# TensorFlow provides the softmax_cross_entropy_with_logits function to avoid numerical stability
# problems with log(0) which is NaN
cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=Ylogits, labels=Y_)
cross_entropy = tf.reduce_mean(cross_entropy)*100

# accuracy of the trained model, between 0 (worst) and 1 (best)
correct_prediction = tf.equal(tf.argmax(Y, 1), tf.argmax(Y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# training step, the learning rate is a placeholder
train_step = tf.train.AdamOptimizer(lr).minimize(cross_entropy)

# init
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)
saver = tf.train.Saver()

# Setting up the indicators
checkpoint_path = './checkpoint_smaller'
if not os.path.isdir(checkpoint_path):
    os.mkdir(checkpoint_path)

id = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
np.random.shuffle(id)
n = 2 #n=2, 5, 10
#indicators = {i:id[round(10/n*i):round(10/n*(i+1))] for i in range(n)} #4:n=2 #6:n=5 #7:n=10
#indicators = {0:id[0:3], 1:id[3:10]}        #3
indicators = {0:[0,1,2,3,4], 1:[5,6,7,8,9]} #1
#indicators = {0:[0,2,4,6,8], 1:[1,3,5,7,9]} #2
#indicators = {0:[0], 1:[1,2,3,4,5,6,7,8,9]} #5
#indicators = {0:[1,3,5,7], 1:[0,2,4,6,8,9]} #8
np.save(checkpoint_path+'/indicators', indicators)

# traverse all indicators and generate new labels
def generate_data(batch_X, batch_Y):
    l = len(batch_X)
    batch_X_rep = np.tile(batch_X, [n,1,1,1])
    batch_X2_rep = np.tile( np.arange(0,n).reshape([1,n]), [l,1] ).flatten('F').reshape([l*n,1])
    batch_id = np.argmax( batch_Y, axis=1 ).reshape([l,1])
    batch_id_rep = np.tile(batch_id, [n,1])
    # find the true indicator of each image
    batch_X2_rep_true = np.tile(
        np.array(list(map(lambda x: [k for k, v in indicators.items() if x in v], batch_id))) ,
        [n,1])
    # generate the new labels including the conflict class
    batch_Y_rep = np.zeros((l*n,10+1))
    for i, match in zip(np.arange(l*n), batch_X2_rep_true==batch_X2_rep):
        if match:
            batch_Y_rep[i][batch_id_rep[i]] = 1
        else:
            batch_Y_rep[i][10] = 1
    return batch_X_rep, batch_X2_rep, batch_Y_rep

# You can call this function in a loop to train the model, 100 images at a time
a_train = []
a_test = []
test_prediction = []
for i in range(201,301):
    # training on batches of 100 images with 100 labels
    batch_X = mnist.train.images[:600,:]
    batch_Y = mnist.train.labels[:600,:]
    batch_X_rep, batch_X2_rep, batch_Y_rep = generate_data(batch_X, batch_Y)
    # learning rate decay
    max_learning_rate = 0.003
    min_learning_rate = 0.0001
    decay_speed = 2000.0
    learning_rate = min_learning_rate + (max_learning_rate - min_learning_rate) * math.exp(-i/decay_speed)
    sess.run(train_step, {X: batch_X_rep, X2: batch_X2_rep, Y_: batch_Y_rep, lr: learning_rate})
    # compute training values for visualisation
    if i%1==0:
        a = sess.run(accuracy, {X: batch_X_rep, X2: batch_X2_rep, Y_: batch_Y_rep})
        print(str(i) + ": accuracy:" + str(a) + " (lr:" + str(learning_rate) + ")")
        a_train.append(a)
    # compute test values for visualisation
    if i%10==0:
        test_X_rep, test_X2_rep, test_Y_rep = generate_data(mnist.test.images, mnist.test.labels)
        a = sess.run(accuracy, {X: test_X_rep, X2: test_X2_rep, Y_: test_Y_rep})
        a_test.append(a)
        y = sess.run(Y, {X: test_X_rep, X2: test_X2_rep})
        test_prediction.append(y)
        print(": ********* epoch " + str(i) + " ********* test accuracy:" + str(a))

saver.save(sess, checkpoint_path + '/Network')

print("max test accuracy: " + str(max(a_test)))
np.savez(checkpoint_path+'/accuracy', a_test=a_test, a_train=a_train, test_prediction=test_prediction)

# n=2, best 0.96 after 10000 iterations
# n=3, 0.8993
# n=4, 0.838
# n=5, 0.999

# layers 4 8 12 200, patches 5x5str1 5x5str2 4x4str2 best 0.989 after 10000 iterations

#calculate prediction accuracy
y = np.argmax(mnist.test.labels, 1)
y_ = test_prediction[np.argmax(a_test)] #[10000*n,11]

cols = [ "Indicator_"+str(i) for i in range(n)]
y_prediction = pd.DataFrame(np.zeros([10000, n]), columns=cols)
for i in range(n):
    y_prediction['Indicator_'+str(i)] = np.argmax( y_[i*10000:(i+1)*10000,:],1)

true_count = 0.0
pass_logic_check_count = 0.0
for i in range(10000):
    critirier = y_prediction.loc[i] == 10
    # see if there are exactly n-1 conflict prediction
    if sum(critirier) != n-1:
        continue
    # see if the left prediction agrees with its indicator
    if y_prediction.loc[i,np.argmin(critirier)] not in indicators[int(np.argmin(critirier).split('_')[1])]:
        continue
    pass_logic_check_count += 1
    if y_prediction.loc[i,np.argmin(critirier)] == y[i]:
        true_count += 1

print('The accuracy without logic is %s'%(max(a_test)))
print('The rate of passing logic check is %s'%(pass_logic_check_count/10000))
print('The conditional accuracy after passing logic check is %s'%(true_count/pass_logic_check_count))
print('The total accuracy with logic check is %s'%(true_count/10000))

# 300 epoch, train_size = 3000
#The accuracy without logic is 0.95695
#The rate of passing logic check is 0.9646
#The conditional accuracy after passing logic check is 0.9654
#The total accuracy with logic check is 0.9312

# 300 epoches, train_size =  600
# train accuracy becomes 1 after 110 epoches
#The accuracy without logic is 0.8927
#The rate of passing logic check is 0.9128
#The conditional accuracy after passing logic check is 0.904250657318142
#The total accuracy with logic check is 0.8254
