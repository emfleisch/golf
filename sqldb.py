import os
import traceback
import sqlite3
from datetime import datetime

db_filename="golf.db"
time_pattern = "%Y-%m-%d %H:%M:%S"


def setup_db():
    db_is_new = not os.path.exists(db_filename)

    conn = sqlite3.connect(db_filename)

    if db_is_new:
        print("Creating schema for {} using \'create_schema.sh\'".format(db_filename))
        with open('create_schema', 'rt') as f:
            schema = f.read()
        conn.executescript(schema)
    else:
        print("Database {} exists".format(db_filename))

    conn.close()

def get_time():
    return(datetime.now().strftime(time_pattern))

def add_course(course_info):
    # init the course
    if not get_course(course_info['name'], 'name'):
        cmd = "insert into courses (name, description) values ('{}','{}')".format(course_info['name'], course_info['description'])
        write_to_db(cmd)

        # init the tee times
        add_tee_time(course_info['tee_times'], course_info['name'])
    return True

def get_course(course_name, col='*'):
    cmd = "select {} from courses WHERE name = \"{}\"".format(col, course_name)
    return(read_from_db(cmd))


def get_available_tee_times(course_name):
    cmd = "select time from tee_times left outer join courses on course_name = courses.name where courses.name = \"{}\" and available = 1".format(course_name)
    return(read_from_db(cmd))

def get_completed_tee_times(course_name):
    cmd = 'select tee_time_id from tee_times where course_name = "{} and end_time != ""'.format(course_name)
    return(read_from_db(cmd))


def get_all_tee_times(course_name):
    cmd = 'select time from tee_times left outer join courses on course_name = courses.name where courses.name = "{}"'.format(course_name)
    return(read_from_db(cmd))


def get_active_rounds(user, id):
    # Get active rounds for a user
    cmd = 'select time from tee_times where golfer = "{}" and start_time != "" and end_time = ""'.format(id)
    return(read_from_db(cmd))


def reserve_tee_time(golfer, course_name, time):
    cmd = 'UPDATE tee_times SET available=0, golfer="{}", start_time="{}" WHERE course_name="{}" and time = {}'.format(golfer, get_time(), course_name, time)
    return(write_to_db(cmd))


def end_tee_time(golfer):
    cmd = 'select tee_time_id from tee_times where golfer="{}" and start_time != "" and end_time = ""'.format(golfer)
    tee_time_id = read_from_db(cmd)[0]
    print(tee_time_id)
    cmd = 'UPDATE tee_times SET end_time="{}" WHERE tee_time_id = {}'.format(get_time(),tee_time_id)
    write_to_db(cmd)
    update_avg_round_times(tee_time_id)

def update_avg_round_times(tee_time_id):
    # update avg round time for course
    cmd = 'select start_time from tee_times where tee_time_id = {} UNION select end_time from tee_times where tee_time_id = {}'.format(tee_time_id, tee_time_id)
    times = read_from_db(cmd)
    delta = (datetime.strptime(times[1], time_pattern) - datetime.strptime(times[0], time_pattern)).seconds
    print("Round time: {}".format(delta))

    # get current avg time for course
    cmd = 'select avg_round_time from courses left outer join tee_times on name = tee_times.course_name where tee_times.tee_time_id = {}'.format(
        tee_time_id)
    curr_course_avg = read_from_db(cmd)
    new_course_avg = _get_avg(curr_course_avg, delta)
    cmd = 'UPDATE courses SET avg_round_time = {} where name = (select course_name from tee_times where tee_time_id = {})'.format(new_course_avg, tee_time_id)
    write_to_db(cmd)

    # update avg round time for the golfer
    cmd = 'select avg_round_time from golfers left outer join tee_times on name = tee_times.golfer where tee_times.tee_time_id={}'.format(tee_time_id)
    curr_golfer_avg = read_from_db(cmd)
    new_golfer_avg = _get_avg(curr_golfer_avg, delta)
    cmd = 'UPDATE golfers SET avg_round_time = {} where name = (select golfer from tee_times where tee_time_id = {})'.format(new_golfer_avg, tee_time_id)
    write_to_db(cmd)


def _get_avg(curr_avg, round_delta):
    print("Current avg: {}".format(curr_avg))
    if curr_avg[0] is 0:
        new_avg = round_delta
    else:
        new_avg = (curr_avg[0] + round_delta) / 2
    print("New avg time: {}".format(new_avg))
    return new_avg


def add_tee_time(times, course_name):
    # Takes 1 or list of tee times to add to a course
    # Checks if tee time already exists, active or not
    curr_times = get_all_tee_times(course_name)
    print("Current times for course: {}".format(curr_times))
    new_times = [t for t in times if t not in curr_times]
    print("New times for course: {}".format(new_times))
    for time in new_times:
        cmd = 'insert into tee_times (time, course_name) values ({},"{}")'.format(time,course_name)
        write_to_db(cmd)


def add_golfer(golfer_id):
    if not get_golfer(golfer_id):
        cmd = "insert into golfers (name) values ('{}')".format(golfer_id)
        write_to_db(cmd)
    else:
        print("Golfer {} has already been added".format(golfer_id))
    return True


def get_golfer(golfer_id, col='name'):
    cmd = "select {} from golfers WHERE name=\"{}\"".format(col, golfer_id)
    if read_from_db(cmd):
        return True
    else:
        return False


def write_to_db(cmd):
    print("cmd: {}".format(cmd))
    try:
        with sqlite3.connect(db_filename) as conn:
            conn.execute(cmd)
    except:
        print("Error writing to db. cmd {},  error :{}".format(cmd, traceback.print_exc()))


def read_from_db(cmd):
    print("cmd: {}".format(cmd))
    try:
        data = []
        with sqlite3.connect(db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute(cmd)
            for row in cursor.fetchall():
                data.append(row[0])
        return data
    except:
        print("Error reading from db. cmd {},  error :{}".format(cmd, traceback.print_exc()))