import logging, logging.config, datetime
from time import gmtime, strftime 
#### set up configurations for logging
current_GMT  = strftime("%Y-%m-%d %H:%M:%S %Z", gmtime())
current_GMT_log = strftime("%Y%m%d__%H%M%S", gmtime()) 
logging.basicConfig(level=logging.DEBUG, filename= "./logs/" + current_GMT_log + '.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y-%d-%b %H:%M:%S %Z', force=True)
logging.info(f"Script started at {current_GMT}")

# perform other imports 
import json 
import schedule 
from selenium import webdriver
from family import *
from student import * 
from reporting import *

### DEBUG to be set to False in production 
#DEBUG = True 
###


def code_update_cron():
    json_input = json.load(open("input.json"))
    report_statistics = dict()
    # build statistical report template using  .json input file 
    for platform in json_input["PLATFORMS"]:
        report_statistics[platform['platform']] = dict()
        for statistics in json_input["REPORTING"]["main_statistics"]:
            report_statistics[platform['platform']][statistics] = 0


    statistics_intermediate, errors_students = replace_student_codes(json_input, report_statistics)
    statistics, errors_families = replace_family_codes(json_input, statistics_intermediate)


    # write errors into a json file 
    errors = errors_families + errors_students
    error_dict = dict()
    error_count = 0
    for error in errors:
        error_dict[str(error_count)]  = dict()
        error_dict[str(error_count)]["description"] = error.description
        error_dict[str(error_count)]["origin"] = error.origin 
        error_count += 1
        
        
    # archive report statistics  
    statistics_filename = './reports/history/daily/statistics__' + current_GMT_log + '.json'
    with open(statistics_filename, "w") as statistics_json:
        json.dump(statistics, statistics_json)
        
    # archive report errors
    errors_filename = './reports/history/daily/errors__' + current_GMT_log + '.json'
    with open(errors_filename, "w") as errors_json:
        json.dump(error_dict, errors_json)

    date_for_email = strftime("%d/%m/%Y  %H:%M", gmtime()) 
    REPORT_SENT = send_daily_report(json_input['REPORTING']['sender_credentials'], ['frederic.tchouli@enkoeducation.com'], statistics, errors,  [], date_for_email)

    return None 

#We run the cron One time
#Before the scheduler take hand an hor later
code_update_cron()

# Task scheduling
# After every hour geeks() is called.
#schedule.every().hour.do(code_update_cron())

# Loop so that the scheduling task
# keeps on running all time.
#while True:
        #Checks whether a scheduled task
        #is pending to run or not
        #schedule.run_pending()
        #time.sleep(600)

