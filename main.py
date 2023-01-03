import logging, logging.config, datetime
from time import gmtime, strftime 
#### set up configurations for logging
current_GMT  = strftime("%Y-%m-%d %H:%M:%S %Z", gmtime())
current_GMT_log = strftime("%Y%m%d__%H%M%S", gmtime()) 
logging.basicConfig(level=logging.DEBUG, filename= "./logs/" + current_GMT_log + '.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%y-%d-%b %H:%M:%S %Z', force=True)
logging.info(f"Script started at {current_GMT}")

# perform other imports 
import json 
from selenium import webdriver
from family import *
from student import * 
from reporting import *

### DEBUG to be set to False in production 
DEBUG = True 
###

json_input = json.load(open("input.json"))
report_statistics = dict()
# build statistical report template using  .json input file 
for platform in json_input["PLATFORMS"]:
    report_statistics[platform['platform']] = dict()
    for statistics in json_input["REPORTING"]["main_statistics"]:
        report_statistics[platform['platform']][statistics] = 0

print(report_statistics.__str__())
statistics, errors = replace_student_codes(json_input, report_statistics)
#statistics_updated01, errors = replace_family_codes(json_input, statistics)

REPORT_SENT = send_daily_report({ 'email' : 'frederic.tchouli@enkoeducation.com', 'password': 'Se19neurJes06'}, ['frederic.tchouli@enkoeducation.com'], statistics, errors,  [])
