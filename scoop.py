#!/usr/bin/env python
import sys
from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

calculation = []
valid_values = [0,1,2,3,4,5,6,7,8,9, '-' ,'+']


@app.route("/helloworld", methods=['GET'])
def hello_world():
    return "Hello World! \n"


@app.route("/digits", methods=['POST'])
def add_digit():

    success = {}
    # Error handle first
    # Ordering
    data = request.get_json()

    if not calculation and isinstance(data['digit'],int):
        #Add to cacluation
        calculation.append(data['digit'])
        status = {'result': 'Added digit'}

    elif not calculation and isinstance(data['digit'],str):
        status = {'result': 'int expected'}

    elif isinstance(calculation[-1], str) and not isinstance(data['digit'],int):
        status = {'result': 'int expected'}

    elif isinstance(calculation[-1], int) and not isinstance(data['digit'],str):
        status = {'result': 'operator expected'}


    #E2 input validation:
    elif data['digit'] not in valid_values:
        status = {'result': 'invalid input digit'}

    else:
        #Add to cacluation
        calculation.append(data['digit'])
        status = {'result': 'Added digit'}

    return jsonify(status)


@app.route("/result", methods=['GET'])
def get_result():
    status = {'result': calculation}
    # do the calculation

    return jsonify(status)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int("7000")
)
