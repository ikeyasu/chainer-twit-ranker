import argparse
import json

def main(args):
    with open(args.twitjson) as f:
        data = json.loads(f.read())
        if args.no_rt:
            data = list(filter(lambda d: "RT" not in d["text"], data))
        if args.no_zero_retweet:
            data = list(filter(lambda d: d["retweet_count"] != 0, data))
        if args.retweet_count >= 0:
            data = list(filter(lambda d: d["retweet_count"] == args.retweet_count, data))
        if args.max_count >= 0:
            data = data[0:args.max_count - 1]
        print(json.dumps(data))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='filter twit data')
    parser.add_argument('twitjson', type=str, help='twit.json file')
    parser.add_argument('--no-rt', action='store_true', help='No RT tweet')
    parser.add_argument('--no-zero-retweet', action='store_true', help='No zero retweet')
    parser.add_argument('--retweet-count', type=int, default=-1, help='retweet count')
    parser.add_argument('--max-count', type=int, default=-1, help='max count')
    args = parser.parse_args()
    main(args)
