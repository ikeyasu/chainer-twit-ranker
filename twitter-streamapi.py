import requests
import json
from requests_oauthlib import OAuth1

from local_settings import api_key, api_secret, access_token, access_secret

# from http://qiita.com/nasa9084/items/40f223b5b44f13ef2925

url = "https://stream.twitter.com/1.1/statuses/filter.json"

auth = OAuth1(api_key, api_secret, access_token, access_secret)

r = requests.post(url, auth=auth, stream=True, data={"locations":"134.18,33.64,144.11,41.70"}) # East-Japan (Except Hokkai-do)
#r = requests.post(url, auth=auth, stream=True, data={"locations":"-122.75,36.8,-121.75,37.8"}) # SF
r = requests.post(url, auth=auth, stream=True, data={"language":"ja", "locations":"134.18,33.64,144.11,41.70"}) # East-Japan (Except Hokkai-do)

for line in r.iter_lines():
  #print(line)
  line_json = json.loads(line.decode("utf-8"))
  #print(line_json["text"])
  print(line_json["retweet_count"])
  #print(json.dumps(line_json))
