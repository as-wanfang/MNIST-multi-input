# MNIST-multi-input

image_number means the true digit on the image.

1: -mnist with two inputs, image + indicator, where indicator is a single number 10*image_number. -Label is one of 10 classes. -Trained model has a higher testing accuracy and is entirely controlled by the indicator input since the model will learn strong pattern first. -1_test: applied the trained model above.

1-1: -mnist with two inputs, image + indicator, where indicator is a single number 1/0 (1 when the image_number is >=5). -Label is one of 10 classes. -Trained model has a higher testing accuracy at 0.9964 compared to the original mnist testing accuracy at 0.989. The model output is determined by two inputs together while mainly by the image input.

2: -mnist with one input. -Label is one of 2 classes: <5, >=5.

2-1: -mnist with two inputs, image + indicator, where indicator is the image_number. -Label is one of 2 classes: <5, >=5.

With conflict class:

normal: -mnist with two inputs, image + indicator, where indicator is a single number. -Label is one of 11 classes: 0~9, and confict.

3-1: -mnist with two inputs, image + indicator, where indicator is multi-dimensional. -Label is one of 11 classes: 0~9, and confict.

3-2: -mnist with two inputs, image + indicator, where indicator is the image_number. -Label is one of 3 classes: <5, >=5, and conflict (indicator conflict with image).

3-3: -mnist with two inputs, image + indicator, where indicator is a even or odd. -Label is one of 3 classes: <5, >=5, and conflict. -Difference: In application, logic check is only checking whether there is one conflict class and one other class. For example with an image and the prediction is conflict and >5 when traverse indicators. But the prediction and its indicator can be right anyway. The rate of passing logic check is 0.9958 The accuracy after passing logic check is 0.9933 The total accuracy is 0.9891
