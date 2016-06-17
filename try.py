
'''
#################################################
# 						#
#	Thanks to Franck Dernoncourt (MIT)	#										
#						#
#################################################
'''

import subprocess
import platform
import copy

from sklearn.datasets import load_digits
import sklearn.metrics 
import numpy as np
from sklearn.cross_validation import StratifiedShuffleSplit
import matplotlib.pyplot as plt

import sys 
sys.path.append("/home/vision/caffe-master/python")
import caffe
import caffe.draw
import h5py


def load_data():

	DATA = load_digits()
	data = DATA.data
	labels = DATA.target

	targets = np.zeros((len(labels),10))
	for count, labels in enumerate(labels):
		targets[count][labels] = 1

	new_data = {}

	new_data['input'] = np.reshape(data, (1797,1,1,64))
	new_data['output'] = targets

	return new_data

def save_data_as_hdf5(hdf5_data_filename, data):
    
    with h5py.File(hdf5_data_filename, 'w') as f:
        f['data'] = data['input'].astype(np.float32)
        f['label'] = data['output'].astype(np.float32)

def train(solver_prototxt_filename):
    caffe.set_mode_cpu()
    solver = caffe.get_solver(solver_prototxt_filename)
    solver.solve()



def get_predicted_output(deploy_prototxt_filename, caffemodel_filename, input, net = None):
    
    if net is None:
        net = caffe.Net(deploy_prototxt_filename,caffemodel_filename, caffe.TEST)
        
    out = net.forward(data=input)
    return out[net.outputs[0]]

def get_predicted_outputs(deploy_prototxt_filename, caffemodel_filename, inputs):
    
    outputs = []
    net = caffe.Net(deploy_prototxt_filename,caffemodel_filename, caffe.TEST)
    for input in inputs:
        outputs.append(copy.deepcopy(get_predicted_output(deploy_prototxt_filename, caffemodel_filename, input, net)))
    return outputs    

    
def get_accuracy(true_outputs, predicted_outputs):
    
    number_of_samples = true_outputs.shape[0]
    number_of_outputs = true_outputs.shape[1]
    threshold = 0.0 # 0 if SigmoidCrossEntropyLoss ; 0.5 if EuclideanLoss
    for output_number in range(number_of_outputs):
        predicted_output_binary = []
        for sample_number in range(number_of_samples):
            #print(predicted_outputs)
            #print(predicted_outputs[sample_number][output_number])            
            if predicted_outputs[sample_number][0][output_number] < threshold:
                predicted_output = 0
            else:
                predicted_output = 1
            predicted_output_binary.append(predicted_output)
            
        print('accuracy: {0}'.format(sklearn.metrics.accuracy_score(true_outputs[:, output_number], predicted_output_binary)))
        print(sklearn.metrics.confusion_matrix(true_outputs[:, output_number], predicted_output_binary))
    
    
def main():
    
    solver_prototxt_filename = 'solver.prototxt'
    train_test_prototxt_filename = 'train_test.prototxt'
    deploy_prototxt_filename  = 'deploy.prototxt'
    hdf5_train_data_filename = 'train_data.hdf5' 
    hdf5_test_data_filename = 'test_data.hdf5' 
    caffemodel_filename = 'digit_iter_1000000.caffemodel' # generated by train()
    
    # Prepare data
    data = load_data()
    train_data = data
    test_data = data
    save_data_as_hdf5(hdf5_train_data_filename, data)
    save_data_as_hdf5(hdf5_test_data_filename, data)
    
    # Train network
    train(solver_prototxt_filename)
        
    # Get predicted outputs
    #input = np.array([[0,0,5,13,9,1,0,0,0,0,13,15,10,15,5,0,0,3,
#			15,2,0,11,8,0,0,4,12,0,0,8,8,0,0,5,8,0,0,9,8,0,0,4,11,0,1,12,7,0,0,2,14,5,10,12,0,0,0,0,6,13,10,0,0,0]])
 #   print(get_predicted_output(deploy_prototxt_filename, caffemodel_filename, input))
    #input = np.array([[[[ 5.1,  3.5,  1.4,  0.2]]],[[[ 5.9,  3. ,  5.1,  1.8]]]])
    #print(get_predicted_output(deploy_prototxt_batch2_filename, caffemodel_filename, input))
    
    # Print network
    #print_network(deploy_prototxt_filename, caffemodel_filename)
    #print_network(train_test_prototxt_filename, caffemodel_filename)
   # print_network_weights(train_test_prototxt_filename, caffemodel_filename)
    
    inputs = data['input']
    outputs = get_predicted_outputs(deploy_prototxt_filename, caffemodel_filename, inputs)
    get_accuracy(data['output'], outputs)
    #'''
    
if __name__ == "__main__":
    main()









