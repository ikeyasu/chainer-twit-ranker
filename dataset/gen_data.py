import argparse
import json
import numpy as np

TABLE = {
    0:0, 1:1, 2:2, 3:3, 4:3, 5:3, 6:4, 7:4, 8:4, 9:4,
    10:5, 11:5, 12:5, 13:5, 14:5, 15:5, 16:5, 17:5, 18:5, 19:5,
    20:6, 21:6, 22:6, 23:6, 24:6, 25:6, 26:6, 27:6, 28:6, 29:6,
    30:7, 31:7, 32:7, 33:7, 34:7, 35:7, 36:7, 37:7, 38:7, 39:7,
    40:7, 41:7, 42:7, 43:7, 44:7, 45:7, 46:7, 47:7, 48:7, 49:7,
    50:7, 51:7, 52:7, 53:7, 54:7, 55:7, 56:7, 57:7, 58:7, 59:7,
    60:8, 61:8, 62:8, 63:8, 64:8, 65:8, 66:8, 67:8, 68:8, 69:8,
    70:8, 71:8, 72:8, 73:8, 74:8, 75:8, 76:8, 77:8, 78:8, 79:8,
    80:8, 81:8, 82:8, 83:8, 84:8, 85:8, 86:8, 87:8, 88:8, 89:8,
    90:8, 91:8, 92:8, 93:8, 94:8, 95:8, 96:8, 97:8, 98:8, 99:8,
}
TABLE_MAX = 99
DISTRIBUTION_MAX = 100

def main(args):
    with open(args.twitjson) as f:
        data = json.loads(f.read())
        distribution = [[], [], [], [], [], [], [], [], [], []]
        for m in data:
            if m["retweet_count"] > TABLE_MAX:
                m["retweet_count"] = 9
            else:
                m["retweet_count"] = TABLE[m["retweet_count"]]
            distribution[m["retweet_count"]].append(m)

        result = []
        for d in distribution:
            np.random.shuffle(d)
            result.extend(d[0:DISTRIBUTION_MAX])
        print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='filter twit data')
    parser.add_argument('twitjson', type=str, help='twit.json file')
    args = parser.parse_args()
    main(args)
