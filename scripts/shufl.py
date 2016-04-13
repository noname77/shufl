#!/usr/bin python

from __future__ import print_function

import sys
import os
import time

import numpy as np
import theano
import theano.tensor as T

import lasagne

import pickle

# ################## Download and prepare the MNIST dataset ##################
# This is just some way of getting the MNIST dataset from an online location
# and loading it into numpy arrays. It doesn't involve Lasagne at all.

def load_dataset():

    #from http://stackoverflow.com/questions/18675863/load-data-from-python-pickle-file-in-a-loop
    def pickleLoader(f):
        try:
            while True:
                yield pickle.load(f)
        except EOFError:
            pass

    def load_mel_specs(filename):
        data = np.ndarray(21642 * 128 * 911, np.float64)
        data = data.reshape(-1, 1, 128, 911)

        with open(filename) as f:
            i = 0
            for mel in pickleLoader(f):
                data[i][0] = mel
                i += 1

        return data

    def load_tag_vectors(filename):
        data = np.ndarray((21642, 40), np.float32)
        with open(filename) as f:
            i = 0
            for tag_vector in pickleLoader(f):
                data[i] = tag_vector
                i += 1
        return data

    # We can now download and read the training and test set images and labels.
    X_train = load_mel_specs('data/mels.pickle')
    y_train = load_tag_vectors('data/tags.pickle')

     # not ready for testing yet
#    X_test = load_mnist_images('t10k-images-idx3-ubyte.gz')
#    y_test = load_mnist_labels('t10k-labels-idx1-ubyte.gz')
#
    # We reserve the last 1000 training examples for validation.
    X_train, X_val = X_train[:-1000], X_train[-1000:]
    y_train, y_val = y_train[:-1000], y_train[-1000:]

    # We just return all the arrays in order, as expected in main().
    # (It doesn't matter how we do this as long as we can read them again.)
    return X_train, y_train, X_val, y_val

def build_cnn(input_var=None):
    # As a third model, we'll create a CNN of two convolution + pooling stages
    # and a fully-connected hidden layer in front of the output layer.

    # Input layer, as usual:
    network = lasagne.layers.InputLayer(shape=(None, 1, 128, 911),
                                        input_var=input_var)
    # This time we do not apply input dropout, as it tends to work less well
    # for convolutional layers.

    # Convolutional layer with 32 kernels of size 5x5. Strided and padded
    # convolutions are supported as well; see the docstring.
    network = lasagne.layers.Conv2DLayer(
            network, num_filters=256, filter_size=(4, 128),
            nonlinearity=lasagne.nonlinearities.rectify,
            W=lasagne.init.GlorotUniform())
    # Expert note: Lasagne provides alternative convolutional layers that
    # override Theano's choice of which implementation to use; for details
    # please see http://lasagne.readthedocs.org/en/latest/user/tutorial.html.

    # Max-pooling layer of factor 2 in both dimensions:
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(4, 4))

    # Another convolution with 32 5x5 kernels, and another 2x2 pooling:
    network = lasagne.layers.Conv2DLayer(
            network, num_filters=256, filter_size=(4, 128),
            nonlinearity=lasagne.nonlinearities.rectify)
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(2, 2))

    # Another convolution with 32 5x5 kernels, and another 2x2 pooling:
    network = lasagne.layers.Conv2DLayer(
            network, num_filters=256, filter_size=(4, 128),
            nonlinearity=lasagne.nonlinearities.rectify)
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(2, 2))

    # Another convolution with 32 5x5 kernels, and another 2x2 pooling:
    network = lasagne.layers.Conv2DLayer(
            network, num_filters=512, filter_size=(4, 128),
            nonlinearity=lasagne.nonlinearities.rectify)

    # A fully-connected layer of 256 units with 50% dropout on its inputs:
    network = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(network, p=.5),
            num_units=256,
            nonlinearity=lasagne.nonlinearities.rectify)

    network = lasagne.layers.GlobalPoolLayer(network)

    # And, finally, the 10-unit output layer with 50% dropout on its inputs:
    network = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(network, p=.5),
            num_units=1024,
            nonlinearity=lasagne.nonlinearities.softmax)

    # And, finally, the 10-unit output layer with 50% dropout on its inputs:
    network = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(network, p=.5),
            num_units=1024,
            nonlinearity=lasagne.nonlinearities.softmax)

    # And, finally, the 10-unit output layer with 50% dropout on its inputs:
    network = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(network, p=.5),
            num_units=188,
            nonlinearity=lasagne.nonlinearities.softmax)

    return network

# ############################## Main program ################################
# Everything else will be handled in our main program now. We could pull out
# more functions to better separate the code, but it wouldn't make it any
# easier to read.

def main(model='mlp', num_epochs=500):
    # Load the dataset
    print("Loading data...")
    X_train, y_train, X_val, y_val = load_dataset()

    # Prepare Theano variables for inputs and targets
    input_var = T.tensor4('inputs')
    target_var = T.ivector('targets')
#
#    print("Building model and compiling functions...")
#    network = build_cnn(input_var)


if __name__ == '__main__':
    if ('--help' in sys.argv) or ('-h' in sys.argv):
        print("Trains a neural network on MNIST using Lasagne.")
        print("Usage: %s [EPOCHS]" % sys.argv[0])
        print()
        print("EPOCHS: number of training epochs to perform (default: 500)")
    else:
        kwargs = {}
        if len(sys.argv) > 1:
            kwargs['num_epochs'] = int(sys.argv[1])
        main(**kwargs)
