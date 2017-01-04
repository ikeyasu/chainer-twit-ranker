chainer-twit-ranker
==================

Work in progress...

クローラで集めたjsonを一つにするshell script
=======================================

```
cd original_dataset
LAST=`ls | sed 's/twit_\([0-9][0-9]*\).json/\1/' | sort -n|tail -n 1`
LAST_1=`expr ${LAST} - 1`
echo [ > ../dataset/twit.json
for i in `seq 0 ${LAST_1}`; do cat twit_${i}.json| sed 's/^\[//' | sed 's/\]$/,/'>> ../dataset/twit.json; done
cat twit_${LAST}.json| sed 's/^\[//' | sed 's/\]$//' >> ../dataset/twit.json
echo ] >> ../dataset/twit.json
```

