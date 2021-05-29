import pickle
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import regex as re
import pandas as pd


# jobs are saved as list of dictionaries eg. [{job1 details},{job2 details},...]
# SAVED JOBS data on DISK

def load_saved_jobs():
    try:
        with open('saved_jobs_disk.pickle', 'rb') as handle:
            saved_jobs_list = pickle.load(handle)        
            print(str(len(saved_jobs_list))+" saved jobs loaded!!!")
    except Exception as e:
        print("No saved jobs exists on disk...")
        saved_jobs_list=[]
    return saved_jobs_list


# To save the parsed data in format of a dict and append it into stored_jobs_list
# this function receives a single job data 
def make_dictionary(jid,gid,small_desc,big_desc,job_link,cid):
    global saved_jobs_list
    small_desc = small_desc.splitlines()

    job_dict = {} 
    job_dict["Job_id"] = jid    
    job_dict["Company_name"] = small_desc[1]
    job_dict["Job_position"] = small_desc[0]
    job_dict["Job_location"] = small_desc[2]

    # Time posted is NA by default if not mentioned
    job_dict["Time_posted"] = 'NA'
    word = 'ago'
    for items in small_desc:
        if(word in items):
            job_dict["Time_posted"] = items;

    # get description and lINK from Big desc by opening
    job_dict["job_description"] = big_desc
    job_dict["Job_apply_link"] = job_link
    job_dict["Geo_id"] = gid
    job_dict["Company_id"] = cid
    
    if(job_dict["Job_apply_link"]=="NA"):
        job_dict["Job_apply_link"]="https://www.linkedin.com/jobs/view/"+job_dict['Job_id']
    
    # NOW saving jobs will be done in experience funtion
    ###saved_jobs_list.append(job_dict)
    
    if("job_description" in job_dict):
        count_exp_mentions = 0
        desc=job_dict['job_description']

        max_year = 0
        is_experience_req = False

        # Check 1
        ####!! This method is paragraph work experience
        q = desc # "job_description 100  \n Exp: \n 0-3 years; Job Code"
        q= (re.sub(r'(\\n+)', r'#', desc))
        res = re.compile(r'#(yrs|years|year|exp|experience).*(yrs|years|year)#').search(q.lower())

        # if paragraph type experience listing is there, then extract maximum experience year 
        if res is not None:
            res=res.group(0)
            num_list=[float(num) for num in re.findall(r'\d*\.\d+|\d+', res)]

            is_experience_req =True
            max_year=max(num_list)

        # Check 2
        # This method is for detecting work experience in same line
        desc_format = desc.replace("\\n", "\n")     
        lined_desc = re.split("\n|\,|\.|\;",desc_format)

        # removing index and formating dataframe to be ready for analysis
        max_year_exp_list =[0]

        for i,line in enumerate(lined_desc):
            if('experience' in line.lower()  or 'expertise' in line.lower() ):
                count_exp_mentions+=1            

            if(('year' in line.lower() or 'yrs' in line.lower()) and ('experience' in line.lower() or 'exp' in line.lower()) ):

                # finding all the numbers in the string
                num_list=[float(num) for num in re.findall(r'\d*\.\d+|\d+', line)]
                if num_list:
                    max_year_exp_list.append(max(num_list))
                is_experience_req = True

        if(max_year<max(max_year_exp_list)):
            max_year=max(max_year_exp_list)


        # override Experience
        job_dict["Experience"] = max_year
        
        # UPDATE SAVED JOBS LIST
        saved_jobs_list.append(job_dict)
        
        # SAVE IN PICKLE
        with open('saved_jobs_disk.pickle', 'rb') as handle:
            loaded_jobs = pickle.load(handle)


        # if jobs are scrapped i.e. added in our global saved_jobs_list, then dump it in into pickle
        if(len(loaded_jobs)<=len(saved_jobs_list)):
            with open('saved_jobs_disk.pickle', 'wb') as handle:
                pickle.dump(saved_jobs_list, handle)
                print("Successfully saved : "+str(len(saved_jobs_list))+ " jobs on disk!")
        else:
            print("No jobs were scrapped!!!")
        
   
def trim_link_for_job_id(link):
    Jid = re.compile(r'/jobs/view/\d+').search(link).group(0)
    Jid = Jid.split('/jobs/view/')[1]
    return Jid


def trim_link_for_company_id(link):
    Jid = re.compile(r'/company/\d+').search(link).group(0)
    Jid = Jid.split('/company/')[1]
    return Jid

def load_opened_url_and_opened_session():
    try:
        with open('url_session_stored.pickle', 'rb') as handle:
            pickled_url_session_list = pickle.load(handle)  
            opened_url = pickled_url_session_list[0]
            opened_session_id = pickled_url_session_list[1]
            
            print(pickled_url_session_list)
            print(" url and previous session loaded!!!")
    except Exception as e:
        print("No existing url or session exisits. "+str(e))
        opened_url=''
        opened_session_id=''
        
        pickled_url_session_list=[]
        pickled_url_session_list=[opened_url,opened_session_id]
        
    return pickled_url_session_list
        


def save_opened_url_and_opened_session(pickled_url_session_list):
    try:
        with open('url_session_stored.pickle', 'wb') as handle:
            pickle.dump(pickled_url_session_list, handle)
    except Exception as e:
        print("EXCEPTION OCCURED!!## "+str(e))


def display_job(job_dict):
    print(job_dict["Company_name"]+' | Experience( Years ) : '+str(job_dict['Experience'])+ " | LinkedIn Job Id : "+job_dict['Job_id'])
        #print(b[idx]['Job_id'])
    print(job_dict["Job_position"])
        #print(b[idx]["job_description"])
    if(job_dict['Job_apply_link']!="NA"):
        print(job_dict['Job_apply_link']+"\n\n")
    else:
        print("https://www.linkedin.com/jobs/view/"+job_dict['Job_id']+"\n\n")

# jobs are saved as list of dictionaries eg. [{job1 details},{job2 details},...]
# SAVED JOBS data on DISK



def scrap_jobs(the_company_id,role='developer'):
    
    global saved_jobs_list

    options = Options()
    #options.headless = True

    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # for Turning of warnings in console selenium INFO:CONSOLE off

    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    # This will now not wait for any page to load
    # Whether to open a new session or use already exsisting session
    # it saves us from logging in everytime

    
    driver = webdriver.Chrome(options = options, desired_capabilities=capa)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    driver.get("https://www.linkedin.com/jobs")
    time.sleep(5)
    for cookie in cookies:
        driver.add_cookie(cookie)    
    driver.get("https://www.linkedin.com/jobs")


    actions = ActionChains(driver)
    start = time.time()
    print('Bot gearing up...')



    # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='jobs-search-box-keyword-id-ember36']")))
    # elem = driver.find_element_by_xpath("//*[@id='jobs-search-box-keyword-id-ember36']")
    # elem.send_keys("developer") # Software engineer, analyst, software, developer etc 

    # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='jobs-search-box-location-id-ember36']")))
    # elem = driver.find_element_by_xpath("//*[@id='jobs-search-box-location-id-ember36']")
    # elem.send_keys("Pune") # India, US, Germany, UK etc 

    # elem.send_keys(Keys.RETURN) # No need to click SUBMIT BUTTON as pressing ENTER key has same effect

    ############################

    # UNIVERSAL SEARCH based on company id
    # geoId = 92000000 means worldwide location

    # commented the code below for updatin developer pune type jobs

    # Now ultimately direct the actually job selection window will appear, no need to search in search bars 

    time.sleep(2) # very important for making wait to login

    ## TO be passed as arguments in this function
    # the_company_id='1028%2C10173544%2C5208%2C10171627%2C2722798%2C976272'
    # role='developer'

    job_page=1;
    skip_jobs_parsed_till_now = (job_page-1)*25
    
    try:

        linkedin_link_for_job_search = 'https://www.linkedin.com/jobs/search/?f_C='+str(the_company_id)+'&geoId=92000000&keywords='+role+'&start='+str(skip_jobs_parsed_till_now)
        driver.get(linkedin_link_for_job_search)
    except Exception as e:
        print("Exception occured... Couldn't connect to existing session. probably cuz session was closed... Open new window"+str(e))

        print("EXITING...")
        return

    ############################
    time.sleep(2)

    #Count total pages, by the bottom page navigation bar
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@class='artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view']")))
    bottom_page_bar = driver.find_elements_by_xpath("//*[@class='artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view']")

  

    # this gives the page number except of the current active page
    last_page = int(bottom_page_bar[len(bottom_page_bar)-1].get_attribute("data-test-pagination-page-btn"))

    # So wait till the last page is not active
    # current active page has class="artdeco-pagination__indicator artdeco-pagination__indicator--number active selected ember-view"



    i=0
    while(job_page<=last_page):
        try:
            isStale = True
            times=25 

            # Fetching jobs at one page of LinkedIn
            while(isStale==True or times>=0):
                try:
                    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@class='jobs-search-results__list-item occludable-update p0 relative ember-view']")))
                    jobs_desc_small_tabs = driver.find_elements_by_xpath("//*[@class='jobs-search-results__list-item occludable-update p0 relative ember-view']")
                    jobs_desc_small_tabs[len(jobs_desc_small_tabs)-1].location_once_scrolled_into_view
                    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@class='jobs-search-results__list-item occludable-update p0 relative ember-view']")))



                    # if max jobs fetched on one page is completed (Here max jobs 25)
                    if(len(jobs_desc_small_tabs)==25):
                        break

                    isStale = False
                    times = times-1;                

                    # For staleness of job ID in href of elements
                    # inside of job_id_parent_elements LIST find immediate child of every ElEMENT 
                    # and that child has JOB ID as HREF attribute 
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@class='mr1 artdeco-entity-lockup__image artdeco-entity-lockup__image--type-square ember-view']")))
                    job_id_25_parent_elements = driver.find_elements_by_xpath("//*[@class='mr1 artdeco-entity-lockup__image artdeco-entity-lockup__image--type-square ember-view']")
                    job_id_25_parent_elements[len(job_id_25_parent_elements)-1].location_once_scrolled_into_view
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@class='mr1 artdeco-entity-lockup__image artdeco-entity-lockup__image--type-square ember-view']")))

                    # For staleness of COMPANY ID element
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@data-control-name='job_card_company_link']")))
                    company_id_25_parent_elements = driver.find_elements_by_xpath("//*[@data-control-name='job_card_company_link']")
                    company_id_25_parent_elements[len(company_id_25_parent_elements)-1].location_once_scrolled_into_view
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@data-control-name='job_card_company_link']")))

                except StaleElementReferenceException as e:
                    print('Still Stale... Update element')
                    isStale = True
                except Exception as e:
                    print('Exception occured : '+str(e))
                    isStale = True


            # GETTING DETAILS about Job

            # After fecthing the jobs in small tabs we need to fecth the BIG description and other details by clicking on it
            # Check Job Id in the Saved_jobs

            # First Check Job Id is new OR not



            job_id_link_list_25=[]

            # Making list of job id links from elements
            for jid_ele in job_id_25_parent_elements:                    
                # jod id element is in immediate child
                actual_jid_ele = jid_ele.find_element_by_xpath("*")
                jid_href = actual_jid_ele.get_attribute("href")
                job_id_link_list_25.append(jid_href)


            company_id_link_list_25=[]

            # Making list of COMPANY id links from elements
            for company_ele in company_id_25_parent_elements:
                cid_href = company_ele.get_attribute("href")
                company_id_link_list_25.append(cid_href)

            job_tab_index=0;
            # for every job in side tab : getting JobId and CompanyId from the jobs on current page and CHECK its EXISTENCE
            for jid_link,cid_link in zip(job_id_link_list_25,company_id_link_list_25):
                
                # Checking whether job is already stored                
                is_job_already_stored = False

                trimmed_jid = trim_link_for_job_id(str(jid_link))
                trimmed_cid = trim_link_for_company_id(str(cid_link))                    
                #print(" JOB ID : "+trimmed_jid)
                #print(" COMPANY ID : "+trimmed_cid)

                # Check job if already stored
                for job_detail in saved_jobs_list:
                    if(trimmed_jid==job_detail["Job_id"]):
                        is_job_already_stored =True

                        # if job_already exists , check for it's Company ID and update if not present already
                        if("Company_id" not in job_detail):
                            # make key for dict if not present already
                            job_detail["Company_id"] = trimmed_cid
                        else:
                            if(job_detail["Company_id"]==''):
                                job_detail["Company_id"] = trimmed_cid                                
                        break
                        # ??? What about new job company id? how to update it
                        # ??? Is there any way to get NEW JOB id from ELEMENT instead of getting it from WINDOW URL. NO!


                if(is_job_already_stored==False):                
                    print('####################################################################################')
                    print('New job : '+str(i))

                    # CLICKING ADDRESS of job location in small tab desc for opening big decription  

                    # CHANGING instead of clicking on bigger element in  side tab i.e. : [@class='jobs-search-results__list-item occludable-update p0 relative ember-view']
                    # now we are clciking on, job location : [@class='job-card-container__metadata-wrapper']
                    # beacuse the problem with clicking on bigger element side tab was that it sometimes clicked on Company's name and opened a new link
                    # but we want to click on the side tab just to open the big description

                    try:
                        # if job is not on disk parse details of that job
                        safe_click_area = jobs_desc_small_tabs[job_tab_index].find_element_by_xpath(".//*[@class='job-card-container__metadata-wrapper']")
                        safe_click_area.click()


                        # Clicking on side tab gives us JobID and GeoId in the URL
                        # extract NEW JOB id using window URL. The only way till now.
                        time.sleep(0.5)
                        job_view_url = driver.current_url
                        extracted_jid = re.compile(r'currentJobId=\d+').search(job_view_url).group(0)
                        extracted_jid = extracted_jid.split('currentJobId=')[1]                



                        extracted_gid = re.compile(r'geoId=\d+').search(job_view_url).group(0)
                        extracted_gid = extracted_gid.split('geoId=')[1]

                        jid_arg = extracted_jid
                        gid_arg = extracted_gid
                        cid_arg = trimmed_cid


                        job_desc_small_arg = jobs_desc_small_tabs[job_tab_index].text

                        # Big description area
                        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//*[@class='jobs-box__html-content jobs-description-content__text t-14 t-normal']")))
                        job_description = driver.find_element_by_xpath("//*[@class='jobs-box__html-content jobs-description-content__text t-14 t-normal']")
                        job_desc_big_arg = job_description.text

                        try:
                            # Clicking on the 'APPLY' button to get the job link
                            WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//*[@class='jobs-apply-button artdeco-button artdeco-button--icon-right artdeco-button--3 artdeco-button--primary ember-view']")))
                            job_button = driver.find_element_by_xpath("//*[@class='jobs-apply-button artdeco-button artdeco-button--icon-right artdeco-button--3 artdeco-button--primary ember-view']")
                            job_button.click()

                            try:                            
                                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                                # To get the 'APPLY' link from newly opened tab
                                driver.switch_to.window(driver.window_handles[1])                            
                                time.sleep(0.5)
                                t=0
                                while(driver.current_url=='about:blank' and t<15):    
                                    time.sleep(0.25)
                                    t=t+0.25;

                                arg_job_url=driver.current_url                        

                                # Closing the job apply tab afetr getting it's URL
                                driver.execute_script("window.stop();")
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])

                            except NoSuchWindowException as e:
                                driver.switch_to.window(driver.window_handles[1])
                                driver.execute_script("window.stop();")
                                driver.close()                         
                                driver.switch_to.window(driver.window_handles[0])

                                arg_job_url='NA'

                            if(len(driver.window_handles)>=2):
                                driver.switch_to.window(driver.window_handles[1])
                                driver.execute_script("window.stop();")
                                driver.close()
                                #print("CLosed new apply window in Exception")

                            driver.switch_to.window(window_name=driver.window_handles[0])


                            # Sending everything to function to store 
                            make_dictionary(jid_arg,gid_arg,job_desc_small_arg,job_desc_big_arg,arg_job_url,cid_arg)
                            display_job(saved_jobs_list[-1])
                            i=i+1
                        except TimeoutException as ex:

                            # if Job URL not available 
                            arg_job_url = 'NA'
                            make_dictionary(jid_arg,gid_arg,job_desc_small_arg,job_desc_big_arg,arg_job_url,cid_arg)
                            display_job(saved_jobs_list[-1])

                            i=i+1
                        except Exception as e:
                            print("EXCEPTION OCCURED Clicking Area : "+str(e))

                            if(len(driver.window_handles)>=2):
                                driver.switch_to.window(driver.window_handles[1])
                                driver.execute_script("window.stop();")
                                driver.close()

                            driver.switch_to.window(window_name=driver.window_handles[0])

                            print(traceback.format_exc())


                    except TimeoutException as ex:
                        print("TIMEOUT EXCEPTION OCCURED Clicking Area : CANT FIND BIG DESCRIPTION BOX "+str(e))
                        print(traceback.format_exc())
                    except Exception as e:
                        #print("EXCEPTION OCCURED Clicking Area : "+str(e))
                        print("EXCEPTION : "+ str(e))             
                        print(traceback.format_exc())
                        print("EXCEPTION OCCURED, in looping through 25 jobs : "+str(e))
                        continue
                
                
                job_tab_index+=1


            # One page jobs scrapped!!!
            # Now GO to next page
            isStale = True
            times=25 

            # Checking for staleness of Bottom page bar element
            while(isStale==True or (times>=0 and isStale==True)):
                try:
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@class='artdeco-pagination__pages artdeco-pagination__pages--number']")))
                    bottom_page_element = driver.find_element_by_xpath("//*[@class='artdeco-pagination__pages artdeco-pagination__pages--number']")
                    bottom_page_element.location_once_scrolled_into_view
                    immediate_children = bottom_page_element.find_elements_by_xpath("*")
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@class='artdeco-pagination__pages artdeco-pagination__pages--number']")))

                    isStale = False
                    times = times-1;             

                except StaleElementReferenceException as e:
                    print('Still Stale... Update element')
                    isStale = True
                except Exception as e:
                    print('Exception occured while checking for staleness  : '+str(e))
                    isStale = True

            # no need to find next page when on last page of the job
            if(job_page!=last_page):

                time.sleep(0.5)
                pos=0;        
                for child in immediate_children:
                    if(child.get_attribute("data-test-pagination-page-btn")==str(job_page)):
                        break;
                    pos=pos+1;

                


                # visibility issue time.sleep() is hack but fix it
                immediate_children[pos+1].find_element_by_xpath("*").click()


            end = time.time()
            print(end - start)
            job_page = job_page+1
        except Exception as e:
            print("EXCEPTION OCCURED outer EXITING...!!! : "+str(e))
            print(traceback.format_exc()) 
            break
        
    return

saved_jobs_list = load_saved_jobs()
scrap_jobs(1028)