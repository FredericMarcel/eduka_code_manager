import logging
import traceback  
#perform other imports 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.chrome.options import Options 
import  time, datetime, random   
from selenium.common.exceptions import *
from bs4 import BeautifulSoup
import math 

def replace_family_codes(json_input, report_statistics):
    
    errors = []
    if json_input['DEBUG']:
       wait = 100
    else:
        wait = 10 
        
    if not  json_input["CATEGORIES"]["families"]['active']:
        logging.warning("Family code replacement turned off for all platforms.")
        return report_statistics, list()
    else:   
        for platform in json_input['PLATFORMS']:
            if (platform["cluster"] ==  'NH' and json_input["CLUSTERS"]["NH"]['active']) or (platform["cluster"] == "SH" and json_input["CLUSTERS"]["SH"]['active']):
                logging.info(f"{platform['platform']} --- Family code replacement attempt starting...")
                
                total_codes_replaced = 0 
                total_wrong_codes = 0   
                used_codes = []
                
                # prepare Options object to be passed to all drivers 
                options = Options()
                options.headless = False # to be set to True in production
                
                try:
                    driver1 = webdriver.Chrome(options=options, executable_path="chromedriver")
                    driver2 = webdriver.Chrome(options=options, executable_path="chromedriver")
                    logging.info(f"{platform['platform']} - Chrome webdrivers 1 and 2 are ready for")
                    time.sleep(1)
                except Exception as e:
                    description = f"{platform['platform']} - Initializing drivers failed"
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)
                    e.__setattr__("description", description)
                    errors.append(e)
                    continue  
                        
                try:
                    
                    ##### attempt to log in 
                    driver1.get(platform['website_url'] + "/list/manage/editlist/family")
                    element = WebDriverWait(driver1, wait).until(
                    EC.presence_of_element_located((By.ID, "txLogin")))
                    
                    driver1.find_element(By.ID,"txLogin").click()
                    driver1.find_element(By.ID,"txLogin").clear()
                    driver1.find_element(By.ID, "txLogin").send_keys(platform['login_credentials']['username'])
                    # find password input field and insert password as well
                    driver1.find_element(By.ID,"txLogin").click()
                    driver1.find_element(By.ID,"txPass").clear()
                    driver1.find_element(By.ID, "txPass").send_keys(platform['login_credentials']['password'])
                    #click login button
                    driver1.find_element(By.ID,"btConnect").click()
                    logging.info(f"{platform['platform']} --- Successful login with driver for getting wrong codes.")
                    
                except Exception as e:
                    description = f"{platform['platform']} --- Failed to log in with Selenium driver for getting wrong codes."
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)
                    e.__setattr__('description', description)
                    errors.append(e)
                    continue 
                
                try: 
                    
                    element = WebDriverWait(driver1, wait).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='CLTableCriteria']/tbody/tr/td[4]/button")))
                    #Delete family status criteria
                    driver1.find_element(By.XPATH, "//*[@id='CLTableCriteria']/tbody/tr/td[4]/button").click()
                    
                    #add a criterion on account codes 
                    driver1.find_element(By.XPATH, "//*[@id='AddCriterion']").click()
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='CriterionSearchBox']")))
                    
                    driver1.find_element(By.XPATH, "//*[@id='CriterionSearchBox']").click()
                    driver1.find_element(By.XPATH, "//*[@id='CriterionSearchBox']").clear()
                    driver1.find_element(By.XPATH, "//*[@id='CriterionSearchBox']").send_keys("account code")
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='SearchCriteriaList']/div")))
                    driver1.find_element(By.XPATH, "//*[@id='SearchCriteriaList']/div").click()
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select")))
                    driver1.find_element(By.XPATH,"//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select").click()
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select/option[5]")))
                    driver1.find_element(By.XPATH, "//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select/option[5]").click() 
                    driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').click()
                    #time.sleep(3)
                    driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').clear()
                    #adding "-00-" to the condition hereafter might be subject to adjustments 
                    driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').send_keys(platform['country_code'] + "-00-")
                    # visit the Data Columns section 
                    driver1.find_element(By.XPATH,'//*[@id="ui-id-6"]').click()
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="CLTableDataBody"]/tr[1]/td[5]/i[2]')))
                    # delete default data columns 
                    driver1.find_element(By.XPATH,'//*[@id="CLTableDataBody"]/tr[1]/td[5]/i[2]').click()
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="CLTableDataBody"]/tr[1]/td[5]/i[2]')))
                    driver1.find_element(By.XPATH,'//*[@id="CLTableDataBody"]/tr/td[5]/i[2]').click()
                    # add family data, namely account codes
                    driver1.find_element(By.XPATH,'//*[@id="Step2Standard"]/div[2]/div[2]/button[3]').click()
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="DataSearchBox"]')))
                    driver1.find_element(By.XPATH,'//*[@id="DataSearchBox"]').click()
                    driver1.find_element(By.XPATH,'//*[@id="DataSearchBox"]').clear()
                    driver1.find_element(By.XPATH,'//*[@id="DataSearchBox"]').send_keys("account code")
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="SearchDataList"]/div')))
                    driver1.find_element(By.XPATH,'//*[@id="SearchDataList"]/div').click()
                    driver1.find_element(By.XPATH,'/html/body/div[15]/div[3]/div/button').click()
                    
                    
                    #Move to List Validation Step
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ui-id-7"]'))) 
                    driver1.find_element(By.XPATH,'//*[@id="ui-id-7"]').click()
                    
                    #Give a name to the family list and save it 
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.ID,"ListName"))) 
                    driver1.find_element(By.ID,"ListName").click()
                    driver1.find_element(By.ID,"ListName").clear()
                    driver1.find_element(By.ID,"ListName").send_keys(platform["short_name"] + "__families__wrongcodes")
                    driver1.find_element(By.ID,"SaveList").click()
                    logging.info(f"{platform} - Family List Saved.")
                    
                except Exception as e:
                    description = f"{platform['short_name']} --- failed to save family list."
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)
                    e.__setattr__("description", description)
                    errors.append(e)
                    continue 
                
                try:
                    element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="OpenList"]')))
                    driver1.find_element(By.XPATH, '//*[@id="OpenList"]').click()
                    # switch driver to newly opened tab  
                    driver1.switch_to.window(driver1.window_handles[1])
                    element = WebDriverWait(driver1, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CustomListTable0_length"]/label/select')))
                    driver1.find_element(By.XPATH, '//*[@id="CustomListTable0_length"]/label/select').click()
                    driver1.find_element(By.XPATH, '//*[@id="CustomListTable0_length"]/label/select/option[8]').click()
                    time.sleep(10)
                    btfsoup = BeautifulSoup(driver1.page_source, "html.parser")
                    logging.info("Family list page source passed to html parser")
                    driver1.close()
                    
                except Exception as e:
                    description = f"{platform['short_name']} --- Failed to pass saved family list to HTML Parser"
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)
                    e.__setattr__("description", description)
                    errors.append(e)
                    continue
                
                list_of_wrong_codes = btfsoup.find_all("td", class_='Column0')
                num_of_wrong_codes = len(list_of_wrong_codes)
                total_wrong_codes = num_of_wrong_codes
                
                # report on number of wrong family codes per platform 
                report_statistics[platform['platform']]["Number of wrong family codes found"] = num_of_wrong_codes
                
                if num_of_wrong_codes == 0:
                    logging.warning(f"{platform['short_name']} --- No wrong family code was found")
                    continue
                
                logging.info(f"{platform['short_name']} --- There are {num_of_wrong_codes} wrong family codes to change")
                
                try:
                # instantiate a second driver 
                    driver2 = webdriver.Chrome(options = options, executable_path= 'chromedriver')
                    logging.info(f"{platform['short_name']} --- Chrome Webdriver #02 has been launched....")
                    
                    driver2.get(platform["website_url"] + "/configuration/manage/sync")
                    element = WebDriverWait(driver2, wait).until(
                    EC.presence_of_element_located((By.ID, "txLogin")))
                    driver2.find_element(By.ID,"txLogin").click()
                    driver2.find_element(By.ID,"txLogin").clear()
                    driver2.find_element(By.ID, "txLogin").send_keys(platform["login_credentials"]['username'])
                    
                    # find password input field and insert password as well
                    driver2.find_element(By.ID,"txLogin").click()
                    driver2.find_element(By.ID,"txPass").clear()
                    driver2.find_element(By.ID, "txPass").send_keys(platform["login_credentials"]['password'])
                    
                    # click login button
                    driver2.find_element(By.ID,"btConnect").click()
                    # wait the ready state to be complete
                    element = WebDriverWait(driver2, wait).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ui-id-11']")))
                    driver2.find_element(By.XPATH, "//*[@id='ui-id-11']").click()
                    
                except Exception as e:
                    description = f"{platform['short_name']} --- Login with Chrome webdriver #02 failed"
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)
                    e.__setattr__("description", description)
                    errors.append(e)
                    continue      
                
                filename_temp = "./bank/" + platform['short_name'] + "/" + platform['short_name'] + "__family.txt"
                wrong_code_count = 0 
                codes_replaced = 0 
                try:
                    with open(filename_temp, 'r+') as codes_file:
                            # read and store all lines into list
                            lines = codes_file.readlines()
                            #move file pointer to the beginning of a file
                            codes_file.seek(0)
                            
                            wrong_family_code = None 
                            
                            #Loop over wrong codes 
                            max_updates_per_round = json_input['CATEGORIES']['families']['max_updates_per_round']
                            for family_code_container in list_of_wrong_codes:
                                
                                if wrong_code_count >= min(num_of_wrong_codes, max_updates_per_round):
                                    break
                                
                                wrong_family_code = family_code_container.get_text().strip()
                                correct_code =  lines[wrong_code_count].strip()
                                
                                try:
                                    driver2.find_element(By.XPATH,'//*[@id="UserCodeBox"]').click()
                                    driver2.find_element(By.XPATH,'//*[@id="UserCodeBox"]').clear()
                                    if json_input['DEBUG']:
                                        driver2.find_element(By.XPATH,'//*[@id="UserCodeBox"]').send_keys("XX-XX-X-XXXXXX" + ";" + "YY-YY-Y-YYYYYY")  
                                    else:
                                        driver2.find_element(By.XPATH,'//*[@id="UserCodeBox"]').send_keys(wrong_family_code + ";" + correct_code)
                                    
                                    # Click on the Preview Button 
                                    driver2.find_element(By.XPATH,'//*[@id="tcodes"]/table/tbody/tr/td[3]/button[1]').click()
                                    element = WebDriverWait(driver2, wait).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button[1]')))
                                    
                                    #Click on the Save Button
                                    driver2.find_element(By.XPATH,'/html/body/div[8]/div[11]/div/button[1]').click()
                                    logging.warning(f"{platform['short_name']} --- Wrong family code {wrong_family_code} replaced by {correct_code}")
                                    used_codes.append(f"{correct_code};{wrong_family_code}")
                                    total_codes_replaced += 1
                                    wrong_code_count += 1
                                    
                                except Exception as e:
                                    description = f"{platform['short_name']} --- Failed to save code replacement of {wrong_family_code} with {correct_code}"
                                    origin = traceback.format_exc()
                                    e.__setattr__("origin", origin)
                                    logging.exception(description)
                                    e.__setattr__("description", description)
                                    errors.append(e)
                                    wrong_code_count += 1
                                    continue   
                                    
                except Exception as e:
                    description = f"{platform['short_name']} --- Something went wrong with handling the code bank file."
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)
                    e.__setattr__("description", description)
                    errors.append(e)
                    continue 
                
                try:
                    # delete used codes from code bank file 
                    with open(filename_temp, "r+") as bank_file:
                            lines_temp = bank_file.readlines()
                            # move file pointer to the beginning of a file
                            bank_file.seek(0)
                            # truncate the file
                            bank_file.truncate()
                            # write back only lines containing unused codes 
                            bank_file.writelines(lines_temp[total_codes_replaced:])
                    
                    # store code replacements done as tuples in a dedicated file 
                    filename_temp2 = "./bank/" + platform['short_name'] + "/" + platform['short_name'] + "__family__used.txt"
                    with open(filename_temp2, "a+") as used_codes_file:
                        used_codes_file.write("\n")
                        for tuple in used_codes:
                            used_codes_file.write(tuple)
                            used_codes_file.write("\n")
                                    
                except Exception as e:
                    description = f"{platform['short_name']} --- A problem occured when trying to delete used codes from bank and archiving them."
                    origin = traceback.format_exc()
                    e.__setattr__("origin", origin)
                    logging.exception(description)    
                    e.__setattr__("description", description)
                    errors.append(e)
                    continue
                report_statistics[platform['platform']]["Number of family codes replaced"] = total_codes_replaced                
            
            else: 
                logging.warning(f"{platform['short_name']} --- Family code replacement deactivated at cluster level.")
                
    return report_statistics, errors




