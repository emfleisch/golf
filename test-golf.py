import requests
import json
import time

url = "http://localhost:7000"
r = requests.post(url + '/user/evanf/add')
print(r.text)

r = requests.post(url + '/course/mycourse/init', json=json.dumps({'tee_times': [800,900,1000]}))
print(r.text)

r = requests.get(url + '/course/mycourse/rounds/available')
print(r.text)

r =requests.post(url + '/user/evanf/round/start', json=json.dumps({"course": "mycourse", "tee_time": 800}))
print(r.text)

print("***********Next request should throw an error, round already started")
print(r.text)

r =requests.post(url + '/user/evanf/round/start', json=json.dumps({"course": "mycourse", "tee_time": 1000}))
print(r.text)

r = requests.get(url + '/course/mycourse/rounds/available')
print(r.text)

# sleep for 5 seconds
time.sleep(15)
r =requests.post(url + '/user/evanf/round/end')
print(r.text)

r = requests.post(url + '/course/mycourse/rounds/add', json=json.dumps({'tee_times': [800,900,1000,1100,1200]}))
print(r.text)

r = requests.get(url + '/course/mycourse/rounds/available')
print(r.text)

