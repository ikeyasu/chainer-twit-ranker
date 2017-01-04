chainer-twit-ranker
==================

Twitter の retweet 数を予測する人工知能を作ってみたかったけど無理だった話。

Twitterの文字数は、140文字なので、人工知能の入力としてしては簡単そう、というのが発端。
簡単な教師あり学習にしたかったので、retweet数を正解データにしてやってみました。

が、できそうに無いという話。

まずデータ集め。twitter-clawler.py で行います。
東京を中心に、2000km の範囲で、日本語を使っているTweetを集めます。
このスクリプトで、46698のTweetが 数時間で集まりました。
集まったものは、original_dataset に入れておきます。
ただ、このスクリプトだと、100個ずつ、jsonファイルが分割されている野江、
以下のような、Shell scriptでファイルを統合してから使います。

```
cd original_dataset
LAST=`ls | sed 's/twit_\([0-9][0-9]*\).json/\1/' | sort -n|tail -n 1`
LAST_1=`expr ${LAST} - 1`
echo [ > ../dataset/twit.json
for i in `seq 0 ${LAST_1}`; do cat twit_${i}.json| sed 's/^\[//' | sed 's/\]$/,/'>> ../dataset/twit.json; done
cat twit_${LAST}.json| sed 's/^\[//' | sed 's/\]$//' >> ../dataset/twit.json
echo ] >> ../dataset/twit.json
```

また、現状のままだと、他人のTweetをRetweetしただけのTweetと、手書きでRTしたTweetが多く含まれ
データとしては、不十分です。
そのため、それらを省いたものを作ります。

```
cd dataset
python filter_twit_data.py twit.json --no-rt > twit_no_rt.json
```

これで中身を見てみると、retweet 数にだいぶ偏りがある事が分かります。（当然ですが）
これではまともに学習でき無さそうです。（ほとんど、0 と予測するようになるだけ）

```
$ python test_dataset.py twit_no_rt.json | sort -n | uniq -c
30313 0
 935 1
 257 2
 120 3
  76 4
  47 5
  35 6
  23 7
  20 8
  19 9
  19 10
  15 11
   9 12
   9 13
  10 14
  10 15
   4 16
   3 17
   2 18
   5 19
   6 20
   3 21
   5 22
   2 23
   2 24
   2 26
   2 27
   5 28
   2 30
   4 31
   3 32
   5 33
   5 34
   2 38
   1 41
   2 44
   1 46
   1 47
   1 48
   1 51
   1 53
   1 54
   1 60
   1 64
   1 67
   2 68
   1 69
   2 71
   1 75
   1 80
   1 90
   1 94
   1 95
   1 96
   1 113
   1 115
   1 123
   1 154
   2 222
   1 235
   1 254
   1 344
   1 360
   1 3522
```

なので、gen_data.py で適等に分散するようにしてみました。
出力は10個にしたいので、適等に0〜100を0〜8にわりふり、それ以上を9に割り振っています。

```
$ python gen_data.py twit_no_rt.json > twit_standard.json
$ python test_dataset.py twit_standard.json | sort -n | uniq -c
 100 0
 100 1
 100 2
 100 3
  97 4
  86 5
  27 6
  30 7
  14 8
  11 9
```

多いものは少ないですが、まぁ、それなりに均等になりました。
これで学習してみましたが、、

```
$ python3 --train-data dataset/twit_standard.json -e 10000
$ python3 predict.py model/MLP_twit_standard_2.model 今日はクリスマス
4: 1.0000
0: 0.0000
1: 0.0000
2: 0.0000
3: 0.0000
5: 0.0000
6: 0.0000
7: 0.0000
8: 0.0000
9: 0.0000
```

ということで、あまり旨く学習できませんでした。。
なにか間違っているのか、データが悪いのか、そもそも無理なのか。
そもそも、人間にも予測困難なものは、人工知能にも無理という話泣きはします。。

（一応、非常にシンプルなデータで、予測ができることは確認済みです）)