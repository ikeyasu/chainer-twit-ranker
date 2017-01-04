#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import six

import chainer
from chainer import cuda
from chainer import functions as F
from chainer import serializers
from net import CNN, MLP


def predict(net, image):
    # 予測時にはtrain=Falseを指定する
    y = net(chainer.Variable(image, volatile=True), train=False)
    return F.softmax(y).data

# http://stackoverflow.com/a/28676904
def blit(dest, src, loc):
    pos = [i if i >= 0 else None for i in loc]
    neg = [-i if i < 0 else None for i in loc]
    target = dest[[slice(i,None) for i in pos]]
    src = src[[slice(i, j) for i,j in zip(neg, target.shape)]]
    target[[slice(None, i) for i in src.shape]] = src
    return dest


def main(args):
    net = MLP(140, 10, 100) if args.model == 'mlp' else CNN()
    gpu_device = args.gpu
    if gpu_device >= 0:
        chainer.cuda.get_device(gpu_device).use()
        net.to_gpu(gpu_device)
        xp = cuda.cupy
    else:
        xp = np
    serializers.load_npz(args.model_file, net)
    text = xp.zeros(140, dtype=xp.float32)
    ary = xp.asarray(bytearray(args.tweet, 'utf-8')[0:139])
    text = blit(text, ary, (0, ))
    text = text.reshape((1, -1))
    probs = cuda.to_cpu(predict(net, text))[0]
    results = sorted(zip(six.moves.range(10), probs), key=lambda x: -x[1])
    for n, p in results:
        print('{0:d}: {1:.4f}'.format(n, p))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MNIST prediction')
    parser.add_argument('model_file', type=str, help='Model file path')
    parser.add_argument('tweet', type=str, help='tweet text')
    parser.add_argument('--model', '-m', type=str, default='mlp', choices=['mlp', 'cnn'], help='Neural network model')
    parser.add_argument('--gpu', '-g', type=int, default=-1, help='GPU device index, -1 indicates CPU')
    args = parser.parse_args()

    main(args)
