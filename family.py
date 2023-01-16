import logging
import traceback  
#perform other imports 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.chrome.options import Options 
import  time, datetime, random   
from selenium.common.exceptions import *
from bs4 import BeautifulSoup
import math 

def replace_family_codes(json_input, report_statistics):
    
    
    try: 
        errors = []
        options = Options()
        options.add_argument("--headless")
        options.headless = True
        #optional
        options.add_argument('--no-sandbox')
        #optional
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        #driver = webdriver.Chrome(options = options)  Uncomment this line in PRODUCTION 
        
        
        if json_input['DEBUG']:
            wait = 100
        else:
            wait = 100
            
        if not  json_input["CATEGORIES"]["families"]['active']:
            logging.warning("Family code replacement turned off for all platforms.")
            return report_statistics, list()
        else:   
            for platform in json_input['PLATFORMS']:
                if (platform["cluster"] ==  'NH' and json_input["CLUSTERS"]["NH"]['active']) or (platform["cluster"] == "SH" and json_input["CLUSTERS"]["SH"]['active']):
                    logging.info(f"{platform['platform']} --- Family code replacement attempt starting...")
                    
                    total_wrong_codes = 0   
                    used_codes = []                  
                    logging.info(f"{platform['platform']} - Chrome webdrivers 1 and 2 are ready for")
                    time.sleep(1)
                    
                            
                    try:
                        
                        ##### attempt to log in 
                        driver.get(platform['website_url'] + "/list/manage/editlist/family")
                        element = WebDriverWait(driver, wait).until(
                        EC.presence_of_element_located((By.ID, "txLogin")))
                        
                        driver.find_element(By.ID,"txLogin").click()
                        driver.find_element(By.ID,"txLogin").clear()
                        driver.find_element(By.ID, "txLogin").send_keys(platform['login_credentials']['username'])
                        # find password input field and insert password as well
                        driver.find_element(By.ID,"txLogin").click()
                        driver.find_element(By.ID,"txPass").clear()
                        driver.find_element(By.ID, "txPass").send_keys(platform['login_credentials']['password'])
                        #click login button
                        driver.find_element(By.ID,"btConnect").click()
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
                        
                        element = WebDriverWait(driver, wait).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='CLTableCriteria']/tbody/tr/td[4]/button")))
                        #Delete family status criteria
                        driver.find_element(By.XPATH, "//*[@id='CLTableCriteria']/tbody/tr/td[4]/button").click()
                        
                        #add a criterion on account codes 
                        driver.find_element(By.XPATH, "//*[@id='AddCriterion']").click()
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='CriterionSearchBox']")))
                        
                        driver.find_element(By.XPATH, "//*[@id='CriterionSearchBox']").click()
                        driver.find_element(By.XPATH, "//*[@id='CriterionSearchBox']").clear()
                        driver.find_element(By.XPATH, "//*[@id='CriterionSearchBox']").send_keys("account code")
                        time.sleep(15)
                        element = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH, "//*[@id='SearchCriteriaList']/div")))
                        driver.find_element(By.XPATH, "//*[@id='SearchCriteriaList']/div").click()
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select")))
                        driver.find_element(By.XPATH,"//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select").click()
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select/option[5]")))
                        driver.find_element(By.XPATH, "//*[@id='CLTableCriteria']/tbody/tr/td[2]/span/select/option[5]").click() 
                        driver.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').click()
                        #time.sleep(3)
                        driver.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').clear()
                        #adding "-00-" to the condition hereafter might be subject to adjustments 
                        driver.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').send_keys(platform['country_code'] + "-00-")
                        # visit the Data Columns section 
                        driver.find_element(By.XPATH,'//*[@id="ui-id-6"]').click()
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="CLTableDataBody"]/tr[1]/td[5]/i[2]')))
                        # delete default data columns 
                        driver.find_element(By.XPATH,'//*[@id="CLTableDataBody"]/tr[1]/td[5]/i[2]').click()
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="CLTableDataBody"]/tr[1]/td[5]/i[2]')))
                        driver.find_element(By.XPATH,'//*[@id="CLTableDataBody"]/tr/td[5]/i[2]').click()
                        # add family data, namely account codes
                        driver.find_element(By.XPATH,'//*[@id="Step2Standard"]/div[2]/div[2]/button[3]').click()
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="DataSearchBox"]')))
                        driver.find_element(By.XPATH,'//*[@id="DataSearchBox"]').click()
                        driver.find_element(By.XPATH,'//*[@id="DataSearchBox"]').clear()
                        driver.find_element(By.XPATH,'//*[@id="DataSearchBox"]').send_keys("account code")
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="SearchDataList"]/div')))
                        driver.find_element(By.XPATH,'//*[@id="SearchDataList"]/div').click()
                        driver.find_element(By.XPATH,'/html/body/div[15]/div[3]/div/button').click()
                        
                        
                        #Move to List Validation Step
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ui-id-7"]'))) 
                        driver.find_element(By.XPATH,'//*[@id="ui-id-7"]').click()
                        
                        #Give a name to the family list and save it 
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.ID,"ListName"))) 
                        driver.find_element(By.ID,"ListName").click()
                        driver.find_element(By.ID,"ListName").clear()
                        driver.find_element(By.ID,"ListName").send_keys(platform["short_name"] + "__families__wrongcodes")
                        driver.find_element(By.ID,"SaveList").click()
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
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="OpenList"]')))
                        driver.find_element(By.XPATH, '//*[@id="OpenList"]').click()
                        # switch driver to newly opened tab  
                        driver.switch_to.window(driver.window_handles[1])
                        element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CustomListTable0_length"]/label/select')))
                        driver.find_element(By.XPATH, '//*[@id="CustomListTable0_length"]/label/select').click()
                        driver.find_element(By.XPATH, '//*[@id="CustomListTable0_length"]/label/select/option[8]').click()
                        time.sleep(10)
                        btfsoup = BeautifulSoup(driver.page_source, "html.parser")
                        logging.info("Family list page source passed to html parser")
                        driver.close()
                        
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
                    total_wrong_codes += num_of_wrong_codes
                    
                    # report on number of wrong family codes per platform 
                    report_statistics[platform['platform']]["Number of wrong family codes found"] = num_of_wrong_codes
                    
                    if num_of_wrong_codes == 0:
                        logging.warning(f"{platform['short_name']} --- No wrong family code was found")
                        continue
                    
                    logging.info(f"{platform['short_name']} --- There are {num_of_wrong_codes} wrong family codes to change")
                    
                    try:
                    # instantiate a second driver 
                        logging.info(f"{platform['short_name']} --- Chrome Webdriver #02 has been launched....")
                        driver.switch_to.window(driver.window_handles[0])
                        driver.get(platform["website_url"] + "/configuration/manage/sync")
                        # wait the ready state to be complete
                        element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ui-id-10']")))
                        driver.find_element(By.XPATH, "//*[@id='ui-id-10']").click()
                        
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
                                    correct_code =  lines[codes_replaced].strip()
                                    
                                    try:
                                        driver.find_element(By.XPATH,'//*[@id="UserCodeBox"]').click()
                                        driver.find_element(By.XPATH,'//*[@id="UserCodeBox"]').clear()
                                        if json_input['DEBUG']:
                                            driver.find_element(By.XPATH,'//*[@id="UserCodeBox"]').send_keys("XX-XX-X-XXXXXX" + ";" + "YY-YY-Y-YYYYYY")  
                                        else:
                                            driver.find_element(By.XPATH,'//*[@id="UserCodeBox"]').send_keys(wrong_family_code + ";" + correct_code)
                                        
                                        # Click on the Preview Button 
                                        driver.find_element(By.XPATH,'//*[@id="tcodes"]/table/tbody/tr/td[3]/button[1]').click()
                                        element = WebDriverWait(driver, wait, ignored_exceptions=(StaleElementReferenceException)).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button[1]')))
                                        
                                        #Click on the Save Button
                                        driver.find_element(By.XPATH,'/html/body/div[8]/div[11]/div/button[1]').click()
                                        logging.warning(f"{platform['short_name']} --- Wrong family code {wrong_family_code} replaced by {correct_code}")
                                        used_codes.append(f"{correct_code};{wrong_family_code}")
                                        codes_replaced += 1
                                        wrong_code_count += 1
                                        time.sleep(3)
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
                    
                    
                    if not json_input['DEBUG']:
                        try:
                            # delete used codes from code bank file 
                            with open(filename_temp, "r+") as bank_file:
                                    lines_temp = bank_file.readlines()
                                    # move file pointer to the beginning of a file
                                    bank_file.seek(0)
                                    # truncate the file
                                    bank_file.truncate()
                                    # write back only lines containing unused codes 
                                    bank_file.writelines(lines_temp[codes_replaced:])
                            
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
                    
                    report_statistics[platform['platform']]["Number of family codes replaced"] =  codes_replaced                
                
                else: 
                    logging.warning(f"{platform['short_name']} --- Family code replacement turned off at cluster level.")
    except Exception as e:
        description = "A problem occured with family code replacements."
        origin = traceback.format_exc()
        e.__setattr__("origin", origin)
        logging.exception(description)    
        e.__setattr__("description", description)
        errors.append(e)
    
    finally:
        driver.quit()
                
    return report_statistics, errors




