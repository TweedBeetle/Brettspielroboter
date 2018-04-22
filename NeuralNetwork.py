from __future__ import print_function
import numpy as np
import difflib
from scipy.special import expit
import ffnet as fn

def sigmoid(x):
    # return 1.0/(1.0 + np.exp(-x))
    return expit(x)
    # return 0.5 * (x / (1 + abs(x)) + 0.5)
    # return x / (1 + abs(x))

def sigmoid_prime(x):
    return sigmoid(x)*(1.0-sigmoid(x))

def tanh(x):
    return np.tanh(x)

def tanh_prime(x):
    return 1.0 - x**2

def theta2ai(theta):
    a = [item for sublist in theta for item in sublist]
    b = [item for sublist in a for item in sublist]
    return np.matrix(b).T

def theta2ai2(theta):
    return np.reshape(theta, (len(theta), 1))

def ai2thetaold(ai, s):
    t1 = np.array(ai[0:(s[0]+1) * (s[1]+1)].reshape(s[0]+1, s[1]+1))
    # print((s[0]+1) * (s[1]+1))
    # print(ai[(s[0]+1) * (s[1]+1):len(ai)])
    t2 = np.array(ai[(s[0]+1) * (s[1]+1):len(ai)].reshape(s[1]+1, s[2]))
    return [t1, t2]

def ai2theta(ai, s):
    theta = []
    indexcounter = 0
    for i in xrange(len(s)-2):
        theta.append(np.array(ai[indexcounter:indexcounter + (s[i]+1) * (s[i+1]+1)].reshape((s[i]+1), (s[i+1]+1))))
        indexcounter += (s[i]+1) * (s[i+1]+1)
    #t1 = np.array(ai[0:(s[0]+1) * (s[1]+1)].reshape(s[0]+1, s[1]+1))
    # print((s[0]+1) * (s[1]+1))
    # print(ai[(s[0]+1) * (s[1]+1):len(ai)])
    #t2 = np.array(ai[(s[0]+1) * (s[1]+1):len(ai)].reshape(s[1]+1, s[2]))
    theta.append(np.array(ai[indexcounter:len(ai)].reshape(s[-2]+1, s[-1])))
    return theta

def ai2theta2(ai, s):
    return np.reshape(ai, (1, len(ai)))[0]

class NeuralNetwork:

    def __init__(self, layers, activation='sigmoid'):
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.activation_prime = sigmoid_prime
        elif activation == 'tanh':
            self.activation = tanh
            self.activation_prime = tanh_prime

        # Set weights
        self.weights = []
        # range of weight values (-1,1)
        # input and hidden layers - random((2+1, 2+1)) : 3 x 3
        for i in xrange(1, len(layers) - 1):
            r = 2*np.random.random((layers[i-1] + 1, layers[i] + 1)) -1
            self.weights.append(r)
        # output layer - random((2+1, 1)) : 3 x 1
        r = 2*np.random.random( (layers[i] + 1, layers[i+1])) - 1
        self.weights.append(r)
        print(self.weights[0].shape)
        print(self.weights[1].shape)
        #a = [item for sublist in self.weights for item in sublist]
        #print([item for sublist in a for item in sublist])

    def fit(self, X, y, learning_rate=0.2, epochs=100000):
        # Add column of ones to X
        # This is to add the bias unit to the input layer
        ones = np.atleast_2d(np.ones(X.shape[0]))
        X = np.concatenate((ones.T, X), axis=1)

        for k in xrange(epochs):
            # if k % 10000 == 0: print 'epochs:', k # doesnt work with futre print function

            i = np.random.randint(X.shape[0])
            a = [X[i]]

            for l in xrange(len(self.weights)):
                    dot_value = np.dot(a[l], self.weights[l])
                    activation = self.activation(dot_value)
                    a.append(activation)
            # output layer
            error = y[i] - a[-1]
            deltas = [error * self.activation_prime(a[-1])]

            # we need to begin at the second to last layer
            # (a layer before the output layer)
            for l in xrange(len(a) - 2, 0, -1):
                deltas.append(deltas[-1].dot(self.weights[l].T)*self.activation_prime(a[l]))

            # reverse
            # [level3(output)->level2(hidden)]  => [level2(hidden)->level3(output)]
            deltas.reverse()

            # backpropagation
            # 1. Multiply its output delta and input activation
            #    to get the gradient of the weight.
            # 2. Subtract a ratio (percentage) of the gradient from the weight.
            for i in xrange(len(self.weights)):
                layer = np.atleast_2d(a[i])
                delta = np.atleast_2d(deltas[i])
                self.weights[i] += learning_rate * layer.T.dot(delta)

    def predict(self, x):
        a = np.concatenate((np.ones(1).T, np.array(x)), axis=1)
        for l in xrange(0, len(self.weights)):
            a = self.activation(np.dot(a, self.weights[l]))
        return a

def predict2(theta, x):
    # a = np.concatenate((np.ones(1).T, np.array(x)), axis=1)
    a = np.concatenate((np.ones(1).T, x), axis=1)
    for l in xrange(0, len(theta)-1):
        a = sigmoid(np.dot(a, theta[l]))
        # print sum(a[a == 1])
        # if sum(a[a == 1]) > 0: raise ValueError('predict warning 1')
    a = np.dot(a, theta[l+1])
    # if a[0] == 1.0: raise ValueError('predict warning 2')
    # print a[0]
    # if a[0] > 10**11 or a[0] < -10**11:
    #     print('warning!')
    return a[0]

conec = fn.mlgraph( (64, 40, 20, 1) )
net = fn.ffnet(conec)
def predict3(weights, x):
    net.weights = weights
    s = net.call(x)
    # print(s)
    # assert s != 1
    return s

if __name__ == '__main__':

    # a = list(np.matrix('[1,2;3,4]').T)
    # b = list(np.matrix('[1,3;4,5]').T)

    # s = [64, 160, 80, 1]
    # s = [640, 400, 400, 1]
    # s = [640, 700, 500, 300, 200, 1]
    # s = [64, 64, 64, 64, 64, 64, 1]
    # s = [64, 64, 64, 1]
    # s = [64, 64, 64, 64, 1]
    # s = [64, 128, 64, 1]
    # s = [64, 64, 128, 1]
    # s = [64, 32, 32, 1]
    # s = [64, 40, 20, 1]
    s = [64, 40, 20, 1]
    # s = [91, 40, 10, 1]
    # s = [74, 128, 64, 1]
    # s = [64, 64, 1]
    conec = fn.mlgraph( (64, 40, 20, 1) )
    net = fn.ffnet(conec)
    print(len(net.weights))

        # nn = NeuralNetwork(s)
        # print(len(theta2ai(nn.weights)))

        # print(predict2(nn.weights, np.random.random((64,64))[0]))
        # print(theta2ai(nn.weights))
        #
        # X = np.array([[0, 0],
        #               [0, 1],
        #               [1, 0],
        #               [1, 1]])
        #
        # y = np.array([0, 1, 1, 0])
        #
        # nn.fit(X, y)
        #
        # for e in X:
        #     print(e,nn.predict(e))
