import os
import sys
import time
import datetime
from influxdb import InfluxDBClient

WORK_DIR = '/var/run/results'
LOG_FILE = '/var/log/parser'

CLIENT = None
DB_NAME = "results"

# Look for results interval
POLL_INTERVAL = 5
def log_to_file(message):
    """
    Add a message to log file

    @message: Line to be logged
    """
    with open(LOG_FILE, "a") as log:
        log.write("[%s]: %s\n" % (datetime.datetime.now(), message))

def poll_results():
    """
    Search for result files and inspect them
    """
    while True:
        res_list = os.listdir(WORK_DIR)
        # Get all result files and parse warnings and errors
        for f_name in res_list:
            # Check extension
            if os.path.splitext(f_name)[1] == '.result':
                # Hashid identify an user
                hashid = os.path.splitext(f_name)[0]
                results = parse_results("%s/%s" % (WORK_DIR, f_name))
                log_to_file(results)
            else:
                # Log the error
                log_to_file("[ERROR]: Unknown type %s\n" % f_name)

            os.remove("%s/%s" %(WORK_DIR, f_name))
        # Wait untill next search (reduce overhead)
        time.sleep(POLL_INTERVAL)

def parse_results(filename):
    """
    This function will parse the compilation files generated by builders.
    At the end, results will be posted to InfluxDB

    Returns a dictionary containing the number of errors and warnings in the
    file

    @filename: File to be parsed
    """
    results = dict()
    warnings = 00
    errors = 0
    with open(filename, "r") as file:
        content = file.readlines()
        for line in content:
            if "warning" in line:
                warnings += 1
            if "error" in line:
                errors += 1

    results['warnings'] = warnings
    results['errors'] = errors
    if errors == 0:
        results['status'] = 'PASS'
    else:
        results['status'] = 'FAIL'

    return results

def start_database(host_name, port_nr, db_name):
    """
    Start InfluxDB where authentification data will be stored
    host_name:  hostname where InfluxDB will run
    port_nr :   port used by InfluxDB
    db_name :   database name to store users
    """
    global CLIENT
    CLIENT = InfluxDBClient(host=host_name, port=port_nr)

    if not CLIENT:
        log_to_file("Fail to start InfluxDB on host %s and port %d" % (host_name, port_nr))
        sys.exit()

    # Check if database is created. If not, create it
    databases_dict = CLIENT.get_list_database()
    databases = [d['name'] for d in databases_dict if 'name' in d]
    if db_name not in databases:
        log_to_file("Database %s doesn't exist. Create and switch to database" % db_name)
        CLIENT.create_database(db_name)
        CLIENT.switch_database(db_name)
    else:
        # Database already exists. Do you want to delete?
        log_to_file("Database %s already exist. Switch to database" % db_name)
        CLIENT.switch_database(db_name)

if __name__ == "__main__":
    # InfluxDB hostname should be sent as first param
    if len(sys.argv) - 1 == 0:
        log_to_file("Trying to start parser without database hostname...")
        sys.exit(-1)

    start_database(sys.argv[1], 8086, DB_NAME)
    poll_results()
