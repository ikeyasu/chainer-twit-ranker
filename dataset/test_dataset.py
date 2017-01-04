import json
import sys

import chainer
import numpy as np
import six

with open(sys.argv[1]) as f:
    train_data = json.loads(f.read())
    #print(len(train_data))
    for d in train_data:
        #print(d["retweet_count"], d["text"].replace("\n", ""))
        print(d["retweet_count"])
        #print(len(d["text"]), d["text"])
