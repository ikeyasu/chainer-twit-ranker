#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

import numpy as np
import six
import time

import chainer
from chainer import cuda
from chainer import functions as F
from chainer import optimizers
from chainer import serializers

from net import CNN, MLP


def update(net, x, t, loss_func):
    y = net(x)
    loss = loss_func(y, t)

def concat_examples(batch, batch_size, device=None):
    x = np.zeros((batch_size, 140), dtype=np.float32)
    for i in six.moves.range(batch_size):
        ary = np.asarray(bytearray(batch[i]["text"], 'utf-8')[0:139])
        x[i] = blit(x[i], ary, (0, ))
    t = xp.asarray([d["retweet_count"] if d["retweet_count"] < 10 else 9 for d in batch], np.int32)
    return x, t

def evaluate(net, dataset, batch_size, device=None):
    # データを1回ずつ使用する場合はrepeat=Falseにする
    # そうしないと`for batch in iterator`が終了しない
    iterator = chainer.iterators.SerialIterator(dataset, batch_size, repeat=False, shuffle=False)
    loss_sum = 0
    acc_sum = 0
    num = 0
    for batch in iterator:
        raw_x, raw_t = concat_examples(batch, batch_size, device)
        # backpropagationは必要ないのでvolatileをTrueにする
        x = chainer.Variable(raw_x, volatile=True)
        t = chainer.Variable(raw_t, volatile=True)
        y = net(x)
        probs = F.softmax(y).data[0]
        results = sorted(zip(six.moves.range(10), probs), key=lambda x: -x[1])
        print(raw_t)
        for n, p in results:
            print('{0:d}: {1:.4f}'.format(n, p))
        loss = F.softmax_cross_entropy(y, t)
        acc = F.accuracy(y, t)
        n = len(raw_x)
        loss_sum += float(loss.data) * n
        acc_sum += float(acc.data) * n
        num += n
    return loss_sum / num, acc_sum / num

# http://stackoverflow.com/a/28676904
def blit(dest, src, loc):
    pos = [i if i >= 0 else None for i in loc]
    neg = [-i if i < 0 else None for i in loc]
    target = dest[[slice(i,None) for i in pos]]
    src = src[[slice(i, j) for i,j in zip(neg, target.shape)]]
    target[[slice(None, i) for i in src.shape]] = src
    return dest

def predict(net, text_for_predict):
    # 予測時にはtrain=Falseを指定する
    text = xp.zeros(140, dtype=xp.float32)
    ary = xp.asarray(bytearray(text_for_predict, 'utf-8')[0:139])
    text = blit(text, ary, (0, ))
    text = text.reshape((1, -1))
    y = net(chainer.Variable(text, volatile=True), train=False)
    probs = F.softmax(y).data[0]
    results = sorted(zip(six.moves.range(10), probs), key=lambda x: -x[1])
    for n, p in results:
        print('{0:d}: {1:.4f}'.format(n, p))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='MNIST training')
    parser.add_argument('--gpu', '-g', type=int, default=-1, help='GPU device index, -1 indicates CPU')
    parser.add_argument('--epoch', '-e', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch-size', '-b', type=int, default=100, help='Mini batch size')
    parser.add_argument('--prefix', '-p', type=str, default=None, help='prefix of saved file name')
    parser.add_argument('--model', '-m', type=str, default='mlp', choices=['mlp', 'cnn'], help='Neural network model')
    parser.add_argument('--train-data', type=str, required=True, help='filename of twit_XX.json')
    args = parser.parse_args()

    n_epoch = args.epoch
    batch_size = args.batch_size
    if args.prefix is None:
        prefix = 'model'
    else:
        prefix = args.prefix
    net = MLP(140, 10, 100) if args.model == 'mlp' else CNN()
    gpu_device = args.gpu
    if gpu_device >= 0:
        chainer.cuda.get_device(gpu_device).use()
        net.to_gpu(gpu_device)
        xp = cuda.cupy
    else:
        xp = np
    optimizer = optimizers.Adam()
    optimizer.setup(net)

    train_data = json.loads(open(args.train_data).read())
    # train dataとvalidation dataに分離する
    train_data, valid_data = chainer.datasets.split_dataset_random(train_data, len(train_data) - batch_size)
    print(len(train_data))
    train_iterator = chainer.iterators.SerialIterator(train_data, batch_size)
    train_loss_sum = 0
    train_acc_sum = 0
    train_num = 0
    best_valid_acc = 0
    best_test_acc = 0
    last_clock = time.clock()

    while train_iterator.epoch < n_epoch:
        # 入力値と正解ラベルを取得
        # x: 入力値
        # t: 正解ラベル
        batch = train_iterator.next()
        x, t = concat_examples(batch, batch_size)
        # ネットワークの実行
        y = net(x)
        # 損失の計算
        loss = F.softmax_cross_entropy(y, t)
        # 精度の計算(学習時に必須ではない)
        acc = F.accuracy(y, t)
        # ネットワークの勾配初期化
        net.cleargrads()
        # バックプロパゲーションを行い勾配を計算する
        loss.backward()
        # パラメータを更新する
        optimizer.update()
        # 損失、精度の累積
        train_loss_sum += float(loss.data) * len(x)
        train_acc_sum += float(acc.data) * len(x)
        train_num += len(x)
        if train_iterator.is_new_epoch:
            train_loss = train_loss_sum / train_num
            train_acc = train_acc_sum / train_num
            valid_loss, valid_acc = evaluate(net, valid_data, batch_size, gpu_device)
            #test_loss, test_acc = evaluate(net, test_data, batch_size, gpu_device)
            current_clock = time.clock()
            print('epoch {} done {}s elapsed'.format(train_iterator.epoch, current_clock - last_clock))
            last_clock = current_clock
            print('train loss: {} accuracy: {}'.format(train_loss, train_acc))
            print('valid loss: {} accuracy: {}'.format(valid_loss, valid_acc))
            #print('test  loss: {} accuracy: {}'.format(test_loss, test_acc))
            #predict(net, '9')
            train_loss_sum = 0
            train_acc_sum = 0
            train_num = 0
            #if valid_acc > best_valid_acc:
            #    best_valid_acc = valid_acc
            #    best_test_acc = test_acc
            serializers.save_npz('{}.model'.format(prefix), net)
    train_iterator.finalize()

    print('best test accuracy: {}'.format(best_test_acc))

