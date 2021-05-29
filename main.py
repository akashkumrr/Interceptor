#imports
from flask import Flask, request, render_template, redirect, url_for, session,jsonify
from flask_bootstrap import Bootstrap
import json
import datetime
from datetime import date
import pickle
import lzma
import multiprocessing
from itertools import islice
import time


# loading saved jobs from disk( pickle )
def load_saved_jobs():
    try:
        with open('saved_jobs_disk.pickle', 'rb') as handle:
            saved_jobs_list = pickle.load(handle)        
            #print(str(len(saved_jobs_list))+" saved jobs loaded!!!")
    except Exception as e:
        print("No saved jobs exists on disk..."+str(e))
        saved_jobs_list=[]
    return saved_jobs_list

# saving shorted jobs on disk( pickle )
def saving_shortlisted_jobs(shortlisted_jobs_list):
    try:
        with open('shortlisted_jobs_disk.pickle', 'wb') as handle:
            pickle.dump(shortlisted_jobs_list, handle)
    except Exception as e:
        print("EXCEPTION OCCURED!!## "+str(e))

# Loading shorted jobs from disk( pickle )
def loading_shortlisted_jobs():
    try:
        with open('shortlisted_jobs_disk.pickle', 'rb') as handle:
            shortlisted_jobs_list = pickle.load(handle)        
            print(str(len(shortlisted_jobs_list))+" shorted  jobs loaded!!!")
    except Exception as e:
        print("No shorted jobs exists on disk..."+str(e))
        shortlisted_jobs_list=[]
    return shortlisted_jobs_list


# saving shorted jobs on disk( pickle )
def saving_applied_jobs(applied_jobs_list):
    try:
        with open('applied_jobs_disk.pickle', 'wb') as handle:
            pickle.dump(applied_jobs_list, handle)
    except Exception as e:
        print("EXCEPTION OCCURED!!## "+str(e))

# Loading shorted jobs from disk( pickle )
def loading_applied_jobs():
    try:
        with open('applied_jobs_disk.pickle', 'rb') as handle:
            applied_jobs_list = pickle.load(handle)        
            #print(str(len(applied_jobs_list))+" applied  jobs loaded!!!")
    except Exception as e:
        print("No applied jobs exists on disk..."+str(e))
        applied_jobs_list=[]
    return applied_jobs_list

# saving shorted jobs on disk( pickle )
def saving_companies_status(company_status_list):
    try:
        with open('companies_status_disk.pickle', 'wb') as handle:
            pickle.dump(company_status_list, handle)
    except Exception as e:
        print("EXCEPTION OCCURED!!## "+str(e))

# Loading shorted jobs from disk( pickle )
def loading_companies_status():
    try:
        with open('companies_status_disk.pickle', 'rb') as handle:
            company_status_list = pickle.load(handle)        
            print(str(len(company_status_list))+" STATUS of companies loaded!!!")
    except Exception as e:
        print("No Company STATUS exists on disk..."+str(e))
        company_status_list=[]
    return company_status_list

# comment it runs everytime
#print("Starting Flask App")

#init flask app
app = Flask(__name__, static_folder="static")
bootstrap = Bootstrap(app)
app.secret_key = "siyajobfinder"



# To remove the data with improper keys
def all_keys_dict_only():
    saved_jobs_list = load_saved_jobs()

    keys_of_dict = [*saved_jobs_list[9889]]
    print(keys_of_dict)

    new_list_of_jobs_with_all_keys=[]

    
    jobs_list = saved_jobs_list[:]

    for job in jobs_list:
        all_keys = True

        # if("Company_name" not in job):
        #     print("NONAME")
        for k in keys_of_dict:
            if(k not in job):
                print("NONAME" + k)
                all_keys = False

                
        if(all_keys==True):
            new_list_of_jobs_with_all_keys.append(job)
            
    print(len(saved_jobs_list),"TOTAL")
    print(len(new_list_of_jobs_with_all_keys))

    with open('saved_jobs_disk.pickle', 'wb') as handle:
        pickle.dump(new_list_of_jobs_with_all_keys, handle)
        print("Successfully saved : "+str(len(new_list_of_jobs_with_all_keys))+ " jobs on disk!")

######################### Functions #######################
def get_company_filtered_list(company,job_list):
    # No argument is needed as it is the first filter, it won't be having any pre-filtered list
    # getting all companies name
        
    # getting the selected company names from argument
    selected_companies_list =[]
    print(company)
    job_list_filtered_step_1 =[]
    fliter1 = []
    selected_companies_list = list(company.split(","))
    print(selected_companies_list)            

    for c_name in selected_companies_list:            
        fliter1 = fliter1 + [job for job in job_list if job["Company_name"].lower() == c_name.lower()]
    
    job_list_filtered_step_1 = fliter1
    print("In FILTER 1 : by company")
    return job_list_filtered_step_1,selected_companies_list


def get_experience_filtered_list(experience,job_list_filtered_step_1):
    job_list_filtered_step_2 = []
    filter2 = []


    filter2 = [ job for job in job_list_filtered_step_1 if int(job["Experience"])<=int(experience)]

    # Applying both the filters
    filter2 = [value for value in filter2 if value in job_list_filtered_step_1]

    job_list_filtered_step_2 = filter2
    print("In FILTER 2 : by experience")
    return job_list_filtered_step_2
    

def get_locations_selected_companies(job_list_filtered_step_2):
    locations_list=[]
    location_set = set()
    for job in job_list_filtered_step_2:
        if("Job_location" in job):
            location_set.add(job["Job_location"])

    locations_list=sorted(location_set)

    return locations_list

def get_location_filtered_list(location,job_list_filtered_step_2):
    location = location
    selected_location_list = []
    job_list_filtered_step_3 = []
    filter3 = []


    selected_location_list = list(location.split("$,"))
    print(len(selected_location_list)," stripped part 1")
    print(selected_location_list)
    
    first_ele =  selected_location_list[0]
    selected_location_list[0] = first_ele.replace("$","")

    last_ele = selected_location_list[-1]
    selected_location_list[-1] = last_ele.replace("$","")
    print(len(selected_location_list)," stripped part 2")
    print(selected_location_list)

   #job_list_with_location_key = [job for job in job_list_filtered_step_2 if "Job_location" in job]
    for j_loc in selected_location_list:            
        filter3 = filter3 + [job for job in job_list_filtered_step_2 if job["Job_location"].lower() == j_loc.lower()]
    

    # Applying the ABOVE filters as well
    filter3 = [value for value in filter3 if value in job_list_filtered_step_2]

    job_list_filtered_step_3 = filter3
    print("In FILTER 3 : by location")

    return job_list_filtered_step_3,selected_location_list



######################### Routes ##########################

# to reinitialize filteres_list3 according to jobs, applied or shorted routes
route_tracker ="empty"

last_c_name = "company_default"
last_exp = "experience_default"
last_loc = "location_default$"
job_list_filtered_step_1 =[]
job_list_filtered_step_2 =[]
job_list_filtered_step_3 =load_saved_jobs()
locations_list =[]
selected_location_list = []
selected_companies_list = []


@app.route('/')
@app.route('/jobs', methods=['GET',"POST"])
@app.route('/jobs/<page_num>',methods=['GET',"POST"])
@app.route('/jobs/<page_num>/<company>', methods=['GET',"POST"])
@app.route('/jobs/<page_num>/<company>/<experience>', methods=['GET',"POST"])
@app.route('/jobs/<page_num>/<company>/<experience>/<location>', methods=['GET',"POST"])
def jobs(page_num=1,company="company_default",experience="experience_default",location="location_default$"):

    global last_c_name,last_exp,last_loc,job_list_filtered_step_1,job_list_filtered_step_2,job_list_filtered_step_3
    global locations_list,selected_location_list,selected_companies_list

    global route_tracker

    if(route_tracker!="jobs"):
        route_tracker="jobs"
        job_list_filtered_step_3 =load_saved_jobs()

    ## What is happening here boggles my mind. Both if and else part gets excetued when adding jobs in shorted list

    if request.method == "GET":

        
        max_jobs_in_page=25

        job_list = load_saved_jobs()
        shorted_lst=loading_shortlisted_jobs()

        max_jobs_in_page=int(max_jobs_in_page)
        page_num=int(page_num)

        all_companies_name=get_all_companies_name()        

        if(last_c_name!=company or last_exp!=experience or last_loc!=location):

            print("Changing",last_c_name!=company,last_c_name,company)
            print("Changing",last_exp!=experience,last_exp,experience)
            print("Changing",last_loc!=location,last_loc,location)

            # filtering by companies
            job_list_filtered_step_1 =job_list


            selected_companies_list=[]
            if(company!="company_default"):
                last_c_name = company
                job_list_filtered_step_1,selected_companies_list = get_company_filtered_list(company,job_list)      
            else:
                last_c_name="company_default"
            
            print(len(job_list_filtered_step_1))

            #filtering by experience, sent a sorted by experience dictionary
            job_list_filtered_step_2=job_list_filtered_step_1


            if(experience!="experience_default"):
                last_exp = experience
                job_list_filtered_step_2 = get_experience_filtered_list(experience,job_list_filtered_step_1)
            else:
                last_exp="experience_default"
            print(len(job_list_filtered_step_2))

            locations_list=get_locations_selected_companies(job_list_filtered_step_2)


            #filtering by location, 
            job_list_filtered_step_3=job_list_filtered_step_2

            selected_location_list =[]
            if(location!="location_default$"):
                last_loc = location
                job_list_filtered_step_3,selected_location_list= get_location_filtered_list(location,job_list_filtered_step_2)
            else:
                last_loc="location_default$"  

            print(len(job_list_filtered_step_3),"filter3 list length")
        else:
            print("\n!!No filter changed, just page filpped. So no need to calculate filter again! It saves time.")


        max_page_number = int(len(job_list_filtered_step_3)/int(max_jobs_in_page))+1 
        one_page_job_list=job_list_filtered_step_3[(page_num-1)*max_jobs_in_page:page_num*max_jobs_in_page]  
        

        lst=[]
        lst2=[]
        dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
        new_dict_keys = ("Job_id","Company_name","Job_position","Job_location","Time_posted","Experience")
        for job_dict in one_page_job_list:
            small_dict=dict_filter(job_dict, new_dict_keys)
            lst.append(small_dict)
        for short_dict in shorted_lst:
            small_dict=dict_filter(short_dict, new_dict_keys)
            lst2.append(small_dict)

        
        return render_template('jobs.html',lst=lst,lst2=lst2,start_page=page_num,max_page_number=max_page_number,
                company_list=all_companies_name,company_selected_arg = company,experience_arg = experience,
                location_arg = location,locations_list = locations_list,selected_location_list=selected_location_list,
                selected_companies_list=selected_companies_list)

        
    else:
        try:
            information = request.data
            data = json.loads(information)

            shorted_lst=loading_shortlisted_jobs()  
            for i in data:
                i = eval(i)
                shorted_lst.append(i)

            
            unique_shorted_jobs_list=[i for n, i in enumerate(shorted_lst) if i not in shorted_lst[n + 1:]] 
            #print(unique_shorted_jobs_list)
            saving_shortlisted_jobs(unique_shorted_jobs_list)
            print("ADDING JOBS")
            return jsonify({'message':'Added to short list'})
            
        except:
            return jsonify({'message':'Not able to add'})


last_c_name = "company_default"
last_exp = "experience_default"
last_loc = "location_default$"
job_list_filtered_step_1 =[]
job_list_filtered_step_2 =[]
job_list_filtered_step_3 =loading_shortlisted_jobs()
locations_list =[]
selected_location_list = []
selected_companies_list = []


#shorted
@app.route('/shorted', methods=['GET',"POST"])
@app.route('/shorted/<page_num>',methods=['GET',"POST"])
@app.route('/shorted/<page_num>/<company>', methods=['GET',"POST"])
@app.route('/shorted/<page_num>/<company>/<experience>', methods=['GET',"POST"])
@app.route('/shorted/<page_num>/<company>/<experience>/<location>', methods=['GET',"POST"])
def shorted(page_num=1,company="company_default",experience="experience_default",location="location_default$"):

    global last_c_name,last_exp,last_loc,job_list_filtered_step_1,job_list_filtered_step_2,job_list_filtered_step_3
    global locations_list,selected_location_list,selected_companies_list
    global route_tracker

    if(route_tracker!="shorted"):
        route_tracker="shorted"
        job_list_filtered_step_3 =loading_shortlisted_jobs()
    
    if request.method == "GET":
        shorted_lst = loading_shortlisted_jobs()
        applied_lst=loading_applied_jobs()

        max_jobs_in_page=25



        max_jobs_in_page=int(max_jobs_in_page)
        page_num=int(page_num)

        all_companies_name=get_all_companies_name()        

        if(last_c_name!=company or last_exp!=experience or last_loc!=location):

            print("Changing",last_c_name!=company,last_c_name,company)
            print("Changing",last_exp!=experience,last_exp,experience)
            print("Changing",last_loc!=location,last_loc,location)

            # filtering by companies
            job_list_filtered_step_1 =shorted_lst


            selected_companies_list=[]
            if(company!="company_default"):
                last_c_name = company
                job_list_filtered_step_1,selected_companies_list = get_company_filtered_list(company,shorted_lst)      
            else:
                last_c_name="company_default"
            
            print(len(job_list_filtered_step_1))

            #filtering by experience, sent a sorted by experience dictionary
            job_list_filtered_step_2=job_list_filtered_step_1


            if(experience!="experience_default"):
                last_exp = experience
                job_list_filtered_step_2 = get_experience_filtered_list(experience,job_list_filtered_step_1)
            else:
                last_exp="experience_default"
            print(len(job_list_filtered_step_2))

            locations_list=get_locations_selected_companies(job_list_filtered_step_2)


            #filtering by location, 
            job_list_filtered_step_3=job_list_filtered_step_2

            selected_location_list =[]
            if(location!="location_default$"):
                last_loc = location
                job_list_filtered_step_3,selected_location_list= get_location_filtered_list(location,job_list_filtered_step_2)
            else:
                last_loc="location_default$"  

            print(len(job_list_filtered_step_3),"filter3 list length")
        else:
            print("\n!!No filter changed, just page filpped. So no need to calculate filter again! It saves time.")


        max_page_number = int(len(job_list_filtered_step_3)/int(max_jobs_in_page))+1 
        one_page_job_list=job_list_filtered_step_3[(page_num-1)*max_jobs_in_page:page_num*max_jobs_in_page]  
        



        max_jobs_in_page=int(max_jobs_in_page)
        page_num=int(page_num)
        #shorted_lst=shorted_lst[(page_num-1)*max_jobs_in_page:page_num*max_jobs_in_page]

        lst=[]
        lst2=[]
        dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
        new_dict_keys = ("Job_id","Company_name","Job_position","Job_location","Time_posted","Experience")
        for job_dict in one_page_job_list:
            small_dict=dict_filter(job_dict, new_dict_keys)
            lst.append(small_dict)

        for short_dict in applied_lst:
            small_dict=dict_filter(short_dict, new_dict_keys)
            lst2.append(small_dict)

        print("SEE Shorted jobs ; GET method")
        return render_template('shorted.html',lst=lst,lst2=lst2,start_page=page_num,max_page_number=max_page_number,
                company_list=all_companies_name,company_selected_arg = company,experience_arg = experience,
                location_arg = location,locations_list = locations_list,selected_location_list=selected_location_list,
                selected_companies_list=selected_companies_list)
    else:
        try:
            information = request.data
            data = json.loads(information)

            applied_lst=loading_applied_jobs()
            for i in data:
                i = eval(i)
                applied_lst.append(i)

            unique_applied_jobs_list=[i for n, i in enumerate(applied_lst) if i not in applied_lst[n + 1:]]


            # checking fo updation in applied list here for status updation, doesn't not allow adding to applied list!!!
            # it says not able to add!!
            
            # old_applied_list = loading_applied_jobs()            
            # old_applied_list = [i for n, i in enumerate(old_applied_list) if i not in old_applied_list[n + 1:]]
            # #old_applied_list = sorted(old_applied_list, key=lambda k: k['Company_name']) 

            # #updated_applied_sorted_list = sorted(unique_applied_jobs_list, key=lambda k: k['Company_name'])
            

            # set_list1 = set(tuple(sorted(d.items())) for d in sorted(old_applied_list))
            # set_list2 = set(tuple(sorted(d.items())) for d in sorted(unique_applied_jobs_list))

            # set_difference = set_list1.symmetric_difference(set_list2)

            # print(set_difference)




            saving_applied_jobs(unique_applied_jobs_list)
            print("APPLYING !!")
            return jsonify({'message':'Added to Applied list'})
        except:
            return jsonify({'message':'Not able to add'})

def count_jobs_by_exp_2_year_and_1_year(c_name):
    jobs_list = load_saved_jobs()
    job_counter_2year = 0
    job_counter_0year = 0

    found_match = False


    for job in jobs_list:
        if(job["Company_name"]==c_name):
            if(int(job["Experience"])==2):
                job_counter_2year+=1
            elif(int(job["Experience"])==0):
                job_counter_0year+=1
            found_match = True

        elif( found_match == True and job["Company_name"]!=c_name):
            break;
        

    return job_counter_2year,job_counter_0year

def count_applied_jobs_by_exp_2_year_and_1_year(c_name):
    applied_jobs_list = loading_applied_jobs()
    job_counter_2year = 0
    job_counter_0year = 0
    found_match = False

    for job in applied_jobs_list:
        # print i, appplied_jobs_list[i]
        if(job["Company_name"]==c_name):
            if(int(job["Experience"])==2):
                job_counter_2year+=1
            elif(int(job["Experience"])==0):
                job_counter_0year+=1
            found_match = True

        elif( found_match == True and job["Company_name"]!=c_name):
            break;
            

    return job_counter_2year,job_counter_0year


def get_all_companies_name():
    job_list = load_saved_jobs()
    company_names_list = []

    company_name_set = set()
    for job in job_list:
        if("Company_name" in job):
            company_name_set.add(job["Company_name"])

    company_names_list=sorted(company_name_set)
    print("Company list length : ",len(company_names_list))

    return company_names_list


#mylist=[{"cname":....,"2yearexp":..., etc}]

# Take set difference to check for updation
# for the companies which had updation count in jobs in applied list : 
# for company in updated_companies_in_applied_list:
    # for i,comp_dict in enumerate(mylist):
    #     if(comp_dict["cname"]==company):
    #         mylist[i]=get_updated_company_status(cname)

def get_updated_company_status(company):

    company_status_dict ={}
    company_status_dict['Company_name'] = company;
    company_status_dict['Total_2year_exp_jobs'],company_status_dict['Total_0year_exp_jobs'] = count_jobs_by_exp_2_year_and_1_year(company)
    company_status_dict['Applied_2year_exp_jobs'],company_status_dict['Applied_0year_exp_jobs'] = count_applied_jobs_by_exp_2_year_and_1_year(company)   

    return company_status_dict

# run one time only, to save in pickle
# Run it at start to get updated about new scrapped jobs,
# for updation at new applied jobs, update only those companies which got newly added in applied list.
def get_companies_status_list(companies_list):
    all_companies_status_list=[] 

           

    for i,company in enumerate(companies_list):
        print(i," ",company)
        company_dict = get_updated_company_status(company)      
        all_companies_status_list.append(company_dict)


    # to save in pickle
    #saving_companies_status(all_companies_status_list);

    print(all_companies_status_list[:10])
    return all_companies_status_list


@app.route('/allstatus', methods=['GET', 'POST'])
def allstatus():


    t=time.time()
    status_list = loading_companies_status()

    print(time.time()-t)
    #return render_template("allstatus.html")
    return render_template("allstatus.html",lst=status_list)
    #return jsonify(status_list=status_list)

    
    # total_process =10

    # chunk_of_company_list_size=int(len(companies_list)/total_process)

    # arg_company_list=companies_list[:chunk_of_company_list_size]

    # for i in range(total_process):
    #     p = multiprocessing.Process(target=get_companies_status_list,args=(arg_company_list) )
    #     arg_company_list=companies_list[(i+1)*chunk_of_company_list_size:(i+2)*chunk_of_company_list_size]
    #     p.start()

    # p.join()

    # for i in range(total_process):
    #     arg_company_list=companies_list[(i+1)*chunk_of_company_list_size:(i+2)*chunk_of_company_list_size]
    #     print(i," ",len(arg_company_list))



    #tried compression

    # with lzma.open("lmza_test.xz", "wb") as handle:
    #     pickle.dump(temp, handle)
    # print("compressed")
    # with lzma.open("lmza_test.xz", "rb") as handle:
    #     my_loaded = pickle.load(handle)
    # print("loaded compressed")

    # print(len(my_loaded))


    #company_status_list = get_companies_status_list()
    #print(company_status_list[:3])


    return "hi"


@app.route('/removeshorted', methods=['GET', 'POST'])
def removeshorted():
    if request.method == "POST":
        try:
            global route_tracker

            if(route_tracker!="removed"):
                route_tracker="removed"

            information = request.data
            data = json.loads(information)

            remove_jobs_list=[]
            for i in data:
                i = eval(i)
                remove_jobs_list.append(i)

            shorted_jobs_list = loading_shortlisted_jobs()

            after_removing_jobs=[]

            after_removing_jobs = [job for job in shorted_jobs_list if job not in remove_jobs_list]

            print(after_removing_jobs)

            saving_shortlisted_jobs(after_removing_jobs)
            return jsonify({'message':'Removed from shortlist'})
        except Exception as e:
            return jsonify({'message':'Not able to remove'+str(e)})


# @app.route('/addtoapplied', methods=['GET', 'POST'])
# def addtoapplied():

last_c_name = "company_default"
last_exp = "experience_default"
last_loc = "location_default$"
job_list_filtered_step_1 =[]
job_list_filtered_step_2 =[]
job_list_filtered_step_3 =loading_applied_jobs()
locations_list =[]
selected_location_list = []
selected_companies_list = []


#applied
@app.route('/applied', methods=['GET',"POST"])
@app.route('/applied/<page_num>',methods=['GET',"POST"])
@app.route('/applied/<page_num>/<company>', methods=['GET',"POST"])
@app.route('/applied/<page_num>/<company>/<experience>', methods=['GET',"POST"])
@app.route('/applied/<page_num>/<company>/<experience>/<location>', methods=['GET',"POST"])
def applied(page_num=1,company="company_default",experience="experience_default",location="location_default$"):

    global last_c_name,last_exp,last_loc,job_list_filtered_step_1,job_list_filtered_step_2,job_list_filtered_step_3
    global locations_list,selected_location_list,selected_companies_list

    global route_tracker

    if(route_tracker!="applied"):
        route_tracker="applied"
        job_list_filtered_step_3 =loading_applied_jobs()
        

    applied_lst=loading_applied_jobs()
    print(len(applied_lst))

    max_jobs_in_page=25
    max_jobs_in_page=int(max_jobs_in_page)
    page_num=int(page_num)

    if request.method == "GET":
        



        all_companies_name=get_all_companies_name()        

        if(last_c_name!=company or last_exp!=experience or last_loc!=location):

            print("Changing",last_c_name!=company,last_c_name,company)
            print("Changing",last_exp!=experience,last_exp,experience)
            print("Changing",last_loc!=location,last_loc,location)

            # filtering by companies
            job_list_filtered_step_1 =applied_lst


            selected_companies_list=[]
            if(company!="company_default"):
                last_c_name = company
                job_list_filtered_step_1,selected_companies_list = get_company_filtered_list(company,applied_lst)      
            else:
                last_c_name="company_default"
            
            print(len(job_list_filtered_step_1))

            #filtering by experience, sent a sorted by experience dictionary
            job_list_filtered_step_2=job_list_filtered_step_1


            if(experience!="experience_default"):
                last_exp = experience
                job_list_filtered_step_2 = get_experience_filtered_list(experience,job_list_filtered_step_1)
            else:
                last_exp="experience_default"
            print(len(job_list_filtered_step_2))

            locations_list=get_locations_selected_companies(job_list_filtered_step_2)


            #filtering by location, 
            job_list_filtered_step_3=job_list_filtered_step_2

            selected_location_list =[]
            if(location!="location_default$"):
                last_loc = location
                job_list_filtered_step_3,selected_location_list= get_location_filtered_list(location,job_list_filtered_step_2)
            else:
                last_loc="location_default$"  

            print(len(job_list_filtered_step_3),"filter3 list length")
    else:
        print("\n!!No filter changed, just page filpped. So no need to calculate filter again! It saves time.")


    max_page_number = int(len(job_list_filtered_step_3)/int(max_jobs_in_page))+1 
    one_page_job_list=job_list_filtered_step_3[(page_num-1)*max_jobs_in_page:page_num*max_jobs_in_page]  
    

    max_jobs_in_page=int(max_jobs_in_page)
    page_num=int(page_num)


    lst=[]
    dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    new_dict_keys = ("Job_id","Company_name","Job_position","Job_location","Time_posted","Experience")
    for job_dict in one_page_job_list:
        small_dict=dict_filter(job_dict, new_dict_keys)
        lst.append(small_dict)

    max_jobs_in_page=int(max_jobs_in_page)
    page_num=int(page_num)


    return render_template('applied.html',lst=lst,start_page=page_num,max_page_number=max_page_number,
                company_list=all_companies_name,company_selected_arg = company,experience_arg = experience,
                location_arg = location,locations_list = locations_list,selected_location_list=selected_location_list,
                selected_companies_list=selected_companies_list)


#####END#####