import logging
import traceback 
# perform other imports 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.chrome.options import Options 
import  time, datetime, random   
from selenium.common.exceptions import *
from bs4 import BeautifulSoup

gender_dict = {"G": "male", "F": "female"}

def replace_student_codes(json_input, report_statistics):
    DEBUG_STUDENT = True 
    errors = []
    if DEBUG_STUDENT:
       wait = 100
    else:
        wait = 10 
        
    if not json_input["CATEGORIES"]["students"]['active']:
        logging.warning("Student code replacement turned off for all platforms.")
        return report_statistics, list()
    else:   
        for platform in json_input['PLATFORMS']:
            if (platform["cluster"] ==  'NH' and json_input["CLUSTERS"]["NH"]['active']) or (platform["cluster"] == "SH" and json_input["CLUSTERS"]["SH"]['active']):
                logging.info(f"{platform['platform']} --- Student code replacement attempt starting...")
                
                total_codes_replaced = 0 
                total_wrong_codes = 0   
                
                
                # prepare Options object to be passed to all drivers 
                options = Options()
                options.headless = False # to be set to True in production
                for gender, gender_eng in gender_dict.items():
                    logging.info(f"{platform['platform']} --- {gender_eng} students currently dealt with...")
                    driver1 = webdriver.Chrome(options = options, executable_path= 'chromedriver')
                    used_codes = []
                    try:
                        driver1.get(platform["website_url"] + "/list/manage/editlist/student")
                        element = WebDriverWait(driver1, wait).until(EC.presence_of_element_located((By.ID, "txLogin")))
                        driver1.find_element(By.ID,"txLogin").click()
                        driver1.find_element(By.ID,"txLogin").clear()
                        driver1.find_element(By.ID, "txLogin").send_keys(platform["login_credentials"]["username"])
                        # find password input field and insert password as well
                        driver1.find_element(By.ID,"txLogin").click()
                        driver1.find_element(By.ID,"txPass").clear()
                        driver1.find_element(By.ID, "txPass").send_keys(platform["login_credentials"]["password"])
                        # click login button
                        driver1.find_element(By.ID,"btConnect").click()
                        #random wait for ready state to be complete
                        
                        
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Failed to log in with Selenium driver for getting wrong student codes."
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__('description', description)
                        errors.append(e)
                        continue 
                    
                    logging.info(f"{platform['platform']} - {gender_eng} students --- sucessfully logged in with Chrome webdriver 01")   
                    
                    try:
                        
                        element = WebDriverWait(driver1, wait).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[4]/button')))
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[4]/button').click()            
                        #Click on the Add Criterion Button
                       
                        driver1.find_element(By.XPATH, '//*[@id="AddCriterion"]').click()
                        #Search for Identification code property in the Criterion Search Box (top right of modal)
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CriterionSearchBox"]')))
                        driver1.find_element(By.XPATH, '//*[@id="CriterionSearchBox"]').click()
                        driver1.find_element(By.XPATH, '//*[@id="CriterionSearchBox"]').clear()
                        driver1.find_element(By.XPATH, '//*[@id="CriterionSearchBox"]').send_keys("identification") 
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="SearchCriteriaList"]/div'))) 
                        driver1.find_element(By.XPATH, '//*[@id="SearchCriteriaList"]/div').click()
                        # Define criterion : does not contain country code + "-ST-"
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/select'))) 
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/select').click()
                        # choose "does not contain" option 
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/select/option[5]'))) 
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/select/option[5]').click()
                        
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').click()
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').clear()
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr/td[2]/span/span/input').send_keys(platform["country_code"] + "-ST-")
                        
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Adding Identification Code Criterion failed"
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__('description', description)
                        errors.append(e)
                        continue 
                    
                    
                    try:
                        # Click on the Add Criterion Button again 
                        driver1.find_element(By.XPATH, '//*[@id="AddCriterion"]').click()
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CriterionSearchBox"]')))
                        #Search for the student gender property in the Criterion Search Box (top right of modal)
                        
                        driver1.find_element(By.XPATH, '//*[@id="CriterionSearchBox"]').click()
                        driver1.find_element(By.XPATH, '//*[@id="CriterionSearchBox"]').clear()
                        driver1.find_element(By.XPATH, '//*[@id="CriterionSearchBox"]').send_keys("gender")
                        # select the student gender property that shows up upon search 
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="SearchCriteriaList"]/div'))) 
                        driver1.find_element(By.XPATH, '//*[@id="SearchCriteriaList"]/div').click()
                        
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr[2]/td[2]/span/span'))) 
                        # Click on the Add button 
                        driver1.find_element(By.XPATH, '//*[@id="CLTableCriteria"]/tbody/tr[2]/td[2]/span/span').click()
                        # select the gender of interest for this round 
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="RTLstValues"]/div[1]'))) 
                        driver1.find_element(By.XPATH, f"//div[@id='RTLstValues']/div[@data-key='{gender}']").click()
                                
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Failed to add Gender Criterion to student list."
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__('description', description)
                        errors.append(e)
                        continue 
                        
                    
                    try:
                        #Move to the List Validation Step 
                        driver1.find_element(By.XPATH, '//*[@id="ui-id-7"]').click()
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.ID, "ListName"))) 

                        #Give a List Name to the Generated List 
                        driver1.find_element(By.ID,"ListName").click()
                        driver1.find_element(By.ID,"ListName").clear()
                        driver1.find_element(By.ID,"ListName").send_keys(platform['country_code'] + "__" + gender_eng + "students__wrongcodes")
                        time.sleep(0.1)
                        #Save the list generated 
                        driver1.find_element(By.ID,"SaveList").click()
                        logging.info(f"{platform['platform']} - {gender_eng} students --- Student List Saved.")
                    
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Failed to save student list."
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__('description', description)
                        errors.append(e)
                        continue 
                    
                    try: 
                        
                        driver1.find_element(By.ID, "OpenList").click() 
                        # switch driver to newly opened tab 
                        driver1.switch_to.window(driver1.window_handles[1])
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/div/table/tbody/tr[1]/td[1]'))) 
                        driver1.find_element(By.XPATH,  '//*[@id="CustomListTable0_length"]/label/select').click()
                        
                        element = WebDriverWait(driver1, wait).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CustomListTable0_length"]/label/select/option[8]'))) 
                        driver1.find_element(By.XPATH, '//*[@id="CustomListTable0_length"]/label/select/option[8]').click()
                        
                         # use the BeautifulSoup library to parse page source 
                        btfsoup = BeautifulSoup(driver1.page_source, "html.parser")
                        logging.info(f"{platform['platform']} - {gender_eng} students --- Student list page source passed to HTML parser....") 
                        
                        #### get all wrong codes found
                        list_of_wrong_codes = btfsoup.find_all("td", class_='Column0')
                        num_of_wrong_codes = len(list_of_wrong_codes)
                        
                        #update number of wrong student codes found on platform  
                        total_wrong_codes += num_of_wrong_codes 
                        
                        if num_of_wrong_codes == 0:
                            logging.warning(f"{platform['platform']} - {gender_eng} students --- No wrong code was found.")
                            continue
                        
                        logging.info(f"{platform['platform']} - {gender_eng} students --- There are {num_of_wrong_codes} wrong codes to change.")
             
                            
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Failed to get wrong codes from saved student list"
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__('description', description)
                        errors.append(e)
                        continue 
                    
                    
                    try:
                    # instantiate a second driver 
                        driver2 = webdriver.Chrome(options = options, executable_path= 'chromedriver')
                        logging.info(f"{platform['platform']} - {gender_eng} students ---Chrome Webdriver #02 has been launched....")
                        
                        driver2.get(platform["website_url"] + "/configuration/manage/sync")
                        
                        element = WebDriverWait(driver1, wait).until(EC.presence_of_element_located((By.ID, "txLogin")))
                        driver2.find_element(By.ID,"txLogin").click()
                        driver2.find_element(By.ID,"txLogin").clear()
                        driver2.find_element(By.ID, "txLogin").send_keys(platform["login_credentials"]["username"])
                        # find password input field and insert password as well
                        driver2.find_element(By.ID,"txLogin").click()
                        driver2.find_element(By.ID,"txPass").clear()
                        driver2.find_element(By.ID, "txPass").send_keys(platform["login_credentials"]["password"])
                        # click login button
                        driver2.find_element(By.ID,"btConnect").click()
                        #random wait for ready state to be complete
                        element = WebDriverWait(driver2, wait).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ui-id-11"]')))
                        driver2.find_element(By.XPATH, '//*[@id="ui-id-11"]').click()
                        
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Failed to get to code replacement page."
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__('description', description)
                        errors.append(e)
                        continue  
                
                    # relative path to file where available student codes are kept for the currently dealt platform 
                    
                    filename_temp = "./bank/" + platform['short_name'] + "/" + platform['short_name'] + "__" + gender_eng + "__" + "student.txt"
                    wrong_code_count = 0 
                    codes_replaced = 0 
                    
                    try:
                        with open(filename_temp, 'r+') as codes_file:
                            # read and store all lines into list
                            lines = codes_file.readlines()
                            #move file pointer to the beginning of a file
                            codes_file.seek(0)
                            
                            wrong_student_code = None 
                            
                            #Loop over wrong codes 
                            for student_code_container in list_of_wrong_codes:
                                if wrong_code_count >= num_of_wrong_codes:
                                    break 
                                
                                wrong_student_code = student_code_container.get_text().strip()
                                correct_code =  lines[wrong_code_count].strip()
                                
                                try:
                                   
                                    driver2.find_element(By.XPATH,  '//*[@id="PersonCodeBox"]').click()
                                    driver2.find_element(By.XPATH,  '//*[@id="PersonCodeBox"]').clear()
                                    
                                    # Don't change actual codes in DEBUG mode !! 
                                    if DEBUG_STUDENT:
                                        driver2.find_element(By.XPATH,  '//*[@id="PersonCodeBox"]').send_keys("XX-XX-X-XXXXXX" + ";" + "YY-YY-Y-YYYYYY")
                                    else:   
                                        driver2.find_element(By.XPATH,  '//*[@id="PersonCodeBox"]').send_keys(wrong_student_code + ";" + correct_code)
                                    
                                    #click on the Preview Button 
                                    driver2.find_element(By.XPATH, '//*[@id="tcodes"]/table/tbody/tr/td[1]/button[1]').click()
                                    element = WebDriverWait(driver2, wait).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button[1]')))
                                    # click on the Save Button 
                                    driver2.find_element(By.XPATH, '/html/body/div[8]/div[11]/div/button[1]').click()
                                    logging.warning(f"{platform['platform']} - {gender_eng} students ---  {wrong_student_code} replaced by {correct_code}.")
                                    wrong_code_count += 1
                                    codes_replaced += 1
                                    #add a line containing used code and replaced code to used codes text file 
                                    used_codes.append(f"{correct_code};{wrong_student_code}")
                                except Exception as e:
                                    description = f"{platform['platform']} - {gender_eng} students --- Failed to replace wrong code {wrong_student_code} by {correct_code}"
                                    logging.exception(description)
                                    e.__setattr__("description", description)
                                    errors.append(e)
                                    wrong_code_count += 1
                                    continue   
                            
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Problem occured when handling code bank file."
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)  
                        e.__setattr__("description", description)
                        errors.append(e)        
                        continue 
                    
                    # update number of wrong codes replaced 
                    total_codes_replaced += codes_replaced 
                    
                    
                    # update code bank and replacement history files 
                    try:
                        # delete used codes from corresponding code bank 
                        with open(filename_temp, "r+") as bank_file:
                            lines_temp = bank_file.readlines()
                            # move file pointer to the beginning of a file
                            bank_file.seek(0)
                            # truncate the file
                            bank_file.truncate()
                            # write back only lines containing unused codes 
                            bank_file.writelines(lines_temp[codes_replaced:])
                            
                        #store code replacements done as tuples in a dedicated file 
                        filename_temp2 = "./bank/" + platform['short_name'] + "/" + platform['short_name'] + "__" + gender_eng + "__" + "student__used.txt"
                        with open(filename_temp2, "a+") as used_codes_file:
                            used_codes_file.write("\n")
                            for tuple in used_codes:
                                used_codes_file.write(tuple)
                                used_codes_file.write("\n")
                                
                    except Exception as e:
                        description = f"{platform['platform']} - {gender_eng} students --- Problem occured when attempting to delete and archive used codes."
                        origin = traceback.format_exc()
                        e.__setattr__("origin", origin)
                        logging.exception(description)
                        e.__setattr__("description", description)
                        errors.append(e)
                        continue
            
                report_statistics[platform['platform']]['Number of wrong student codes found'] = total_wrong_codes
                report_statistics[platform['platform']]['Number of student codes replaced'] = total_codes_replaced 
                 
            else:
                logging.warning(f"{platform['platform']} --- Student code replacement turned off at cluster level.")
                continue 
            
    return report_statistics, errors 


