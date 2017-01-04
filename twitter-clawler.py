import requests
import sys
import time

from datetime import date, timedelta
from requests_oauthlib import OAuth1

from local_settings import api_key, api_secret, access_token, access_secret

# from
#   http://qiita.com/nasa9084/items/40f223b5b44f13ef2925
#   http://qiita.com/mima_ita/items/ba59a18440790b12d97e

url = "https://api.twitter.com/1.1/search/tweets.json"
two_weeks_ago = (date.today() - timedelta(days=7)).isoformat()
first_parameter = "?q=&geocode=35.68,139.77,2000km&lang=ja&result_type=recent&count=100&until={}".format(two_weeks_ago)

auth = OAuth1(api_key, api_secret, access_token, access_secret)

r = requests.get("https://api.twitter.com/1.1/application/rate_limit_status.json", auth=auth)
line_json = r.json()
limit_remaining = line_json["resources"]["search"]["/search/tweets"]["remaining"]
if limit_remaining <= 0:
    sys.exit(1)

request_url = url + first_parameter
print(request_url)
count = 1
while count > 0:
    r = requests.get(request_url, auth=auth)
    json = r.json()
    print(json["statuses"])
    #print(json["search_metadata"])
    if "next_results" not in json["search_metadata"]:
        break
    next_result = json["search_metadata"]["next_results"]
    request_url = url + next_result
    count = json["search_metadata"]["count"]
    time.sleep(6) # sec
