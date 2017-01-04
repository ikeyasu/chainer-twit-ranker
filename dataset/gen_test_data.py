import argparse
import json

import numpy as np

import six


def main(args):
    step = args.number // 10
    array = []
    for i in six.moves.range(args.number):
        text = str(i // step)
        retweet_count = i // step * 100
        array.append({"text": text, "retweet_count": retweet_count})
    np.random.shuffle(array)
    print(json.dumps(array))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gen simple test data')
    parser.add_argument('number', type=int, help='number of dataset')
    args = parser.parse_args()
    main(args)
