#!/usr/bin/env python
import sys
import json
import traceback
import datetime
from datetime import timedelta
from datetime import datetime
from flask import Flask
from flask import request
from flask import jsonify
import sqldb


app = Flask(__name__)

calculation = []
valid_values = [0,1,2,3,4,5,6,7,8,9, '-' ,'+']

golfers = {}
active_rounds = {}
course_info = {}
stock_tee_times = [700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500]

@app.route("/helloworld", methods=['GET'])
def hello_world():
    return "Hello World! \n"

# Golfer Specific Endpoints

# Endpoint to add a new golfer
# example call: requests.post(url + '/golfer/evanf/add')
@app.route("/user/<user_id>/add", methods=['POST'])
def add_golfer(user_id):
    '''POST endpoint taking no data, uses user_id in API call to register a golfer. If already registered, verfied'''
    r = sqldb.add_golfer(user_id)
    return "Added golfer {}".format(user_id)


# Endpoint to add a new golfer
# example call: requests.post(url + '/golfer/evanf/add')
@app.route("/user/<user_id>/get", methods=['get'])
def get_golfer(user_id):
    '''POST endpoint taking no data, uses user_id in API call to register a golfer. If already registered, verfied'''
    r = sqldb.get_golfer(user_id)
    return "got golfer {}".format(r)


# Endpoint to see all past rounds
@app.route("/user/<user_id>/history", methods=['GET'])
def golfer_history(user_id):
    '''GET endpoint using user_id in API call to return history of rounds'''
    if user_id not in golfers:
        print('golfer not reigstered')
        return 'golfer not registered'
    elif not golfers.get(user_id).get('past_rounds', ''):
        print('golfer has not golfed before')
        return 'No rounds to show'
    else:
        # There are past rounds we want to return
        print("golfers past rounds: {}".format(golfers[user_id].get('past_rounds', '')))
        return "Printed golfing history \n"


def validate_golfer(id):
    if not sqldb.get_golfer(id):
        print('Please register before golfing')
        return False
    return True



# Endpoint to start a new round from the golfer POV
# example call: requests.post(url + '/golfer/evanf/round/start', json=json.dumps({"course": "mycourse", "tee_time": "0800"}))
@app.route("/user/<user_id>/round/start", methods=['POST'])
def add_round(user_id):
    '''POST Endpoint to start a new round. JSON input should include course and tee time'''
    try:
        data = json.loads(request.get_json())
    except:
        print("Error getting round info: {}".format(traceback.print_exc()))
        return "Error getting round info \n"

    if not validate_golfer(user_id):
        return 'golfer not registered'
    elif sqldb.get_active_rounds('golfer', user_id):
        print('Golfer already active in a round. Please end before starting a new round')
        return 'golfer already active'
    else:
        # golfer is registered, not currently playing
        # Check course is valid
        if not sqldb.get_course(data['course']):
            return "Course {} is not valid. Can not start round".format(data['course'])
        # Check tee time is valid
        if not _check_tee_time(data['course'], data['tee_time']):
            return "Tee time {} is not available.".format(data['tee_time'])
        #Start the round
        r = sqldb.reserve_tee_time(user_id, data['course'], data['tee_time'])
        return "Started new round \n"


# Endpoint to end a round from golfer. Takes no data, since only 1 round can be active at a time
@app.route("/user/<user_id>/round/end", methods=['POST'])
def end_round(user_id):
    try:
        if not validate_golfer(user_id):
            return 'golfer not registered'
        rounds = sqldb.get_active_rounds('golfer', user_id)
        if not rounds:
            print('No round currently active')
            return 'No active round to end'
        else:
            #Had an active round to end
            #total_time = timedelta.total_seconds(end_time - start_time)
            r = sqldb.end_tee_time(user_id)
            print("Ending round for {}!".format(user_id))
            return "Ended round \n"
    except:
        print("Error starting new round: {}".format(traceback.print_exc()))
        return "Error starting new round \n"


# Course Specific Endpoints

# example call: requests.post(url + '/course/mycourse/init')
@app.route("/course/<course_name>/init", methods = ['POST'])
def init_course(course_name):
    try:
        data = json.loads(request.get_json())
    except:
        print("No tee times specified. Init with stock times. error:{}".format(traceback.print_exc()))
        data = None

    # Only info tied to a course will be available tee times
    c = {'name': course_name, 'description': 'golf_course', 'tee_times': stock_tee_times}
    if data and data.get('tee_times', ''):
        c['tee_times'] = data['tee_times']
    print(c['tee_times'])
    sqldb.add_course(c)
    return 'Course {} initalized and ready to book!'.format(course_name)


# example call: requests.get(url + '/course/mycourse/rounds/available')
@app.route("/course/<course_name>/rounds/available", methods=['GET'])
def open_tee_times(course_name):
    open_times = sqldb.get_available_tee_times(course_name)
    print("Open times: {}".format(open_times))
    return jsonify(open_times)


# example call: requests.get(url + '/course/mycourse/rounds/available')
@app.route("/course/<course_name>/rounds/add", methods=['POST'])
def add_tee_times(course_name):
    try:
        data = json.loads(request.get_json())
    except:
        print("No tee times specified. Init with stock times. error:{}".format(traceback.print_exc()))
        data = None

    open_times = sqldb.add_tee_time(data['tee_times'], course_name)
    print("Added tee times to {}: {}".format(open_times, course_name))
    return "Added tee times"


@app.route("/course/<course_name>/rounds/avg_time", methods=['GET'])
def get_course_avg_round(course_name):
    # get all completed rounds for the course
    #sqldb.
    return "hold"

def _check_tee_time(course_name, tee_time):
    '''Internal method to handle open_tee_times flask response obj'''
    times = open_tee_times(course_name).get_data()
    times = times.replace(',', '').split()
    if str(tee_time) in times:
        print("Found the tee time")
        return True
    else:
        print("No time found")
        return False

# The following are endpoints for caluclations on the data
@app.route("/result", methods=['GET'])
def get_result():
    status = {'result': calculation}
    # do the calculation

    return jsonify(status)


if __name__ == "__main__":
    sqldb.setup_db()
    print("sql set up")
    app.run(
        host="0.0.0.0",
        port=int("7000")
)


'''INIT PERSON AND COURSE FOR TESTING
r =requests.post(url + '/user/evanf/add')
r = requests.post(url + '/course/mycourse/init')
r=requests.post(url + '/course/mycourse2/init', json=json.dumps({'tee_times': [800,900,1000]}))
r = requests.get(url + '/course/mycourse/rounds/available')
r =requests.post(url + '/user/evanf/round/start', json=json.dumps({"course": "mycourse", "tee_times": "0800"}))

'''