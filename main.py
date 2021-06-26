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
import traceback


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

# SAVING jobs from disk( pickle )
def saving_base_jobs(jobs_list):
    try:    
        with open('saved_jobs_disk.pickle', 'wb') as handle:
            pickle.dump(jobs_list, handle)
    except Exception as e:
        print("EXCEPTION OCCURED!!## "+str(e))

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






######################### Routes ##########################

# to reinitialize filteres_list3 according to jobs, applied or shorted routes

class stateTracker:    
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

    # call it at start, whenever changing routes, with disk_jobs or shortlisted_jobs accordingly
    def load_filter1_list_default(self,loaded_jobs):
        self.job_list_filtered_step_1 = loaded_jobs

    def filter_company(self,company,job_list):

        
        self.selected_companies_list =[]
        self.job_list_filtered_step_1 =[]        
        self.selected_companies_list = list(company.split(","))
          
        fliter1=[]
        for c_name in self.selected_companies_list:            
            fliter1 = fliter1 + [job for job in job_list if job["Company_name"].lower() == c_name.lower()]
        
        self.job_list_filtered_step_1 = fliter1
        print("In FILTER 1 : by company")

    def filter_experience(self,experience):
        self.job_list_filtered_step_2 = []
        filter2 = []

        if(int(experience)>=0):
            filter2 = [ job for job in self.job_list_filtered_step_1 if int(job["Experience"])<=int(experience)]
        else:
            filter2 = [ job for job in self.job_list_filtered_step_1 if int(job["Experience"])>=-1*int(experience)]

        # Applying both the filters
        filter2 = [value for value in filter2 if value in self.job_list_filtered_step_1]

        self.job_list_filtered_step_2 = filter2
        print("In FILTER 2 : by experience")


    def filter_location(self,location):
        location = location
        self.selected_location_list = []
        self.job_list_filtered_step_3 = []
        filter3 = []


        self.selected_location_list = list(location.split("$,"))
        
        first_ele =  self.selected_location_list[0]
        self.selected_location_list[0] = first_ele.replace("$","")

        last_ele = self.selected_location_list[-1]
        self.selected_location_list[-1] = last_ele.replace("$","")


        for j_loc in self.selected_location_list:            
            filter3 = filter3 + [job for job in self.job_list_filtered_step_2 if job["Job_location"].lower() == j_loc.lower()]
        

        # Applying the ABOVE filters as well
        filter3 = [value for value in filter3 if value in self.job_list_filtered_step_2]

        self.job_list_filtered_step_3 = filter3
        print("In FILTER 3 : by location")

    def get_locations_selected_companies(self,job_list):
        self.locations_list=[]
        location_set = set()
        for job in self.job_list_filtered_step_2:
            if("Job_location" in job):
                location_set.add(job["Job_location"])

        self.locations_list=sorted(location_set)

        if(len(self.locations_list)==0):
            self.locations_list=[]
            location_set = set()
            for job in job_list:
                if("Job_location" in job):
                    location_set.add(job["Job_location"])

            self.locations_list=sorted(location_set)


    def calculate_filters(self,company,experience,location,job_list):
        if(self.last_c_name!=company or self.last_exp!=experience or self.last_loc!=location):

            print("Changing",self.last_c_name!=company,self.last_c_name,company)
            print("Changing",self.last_exp!=experience,self.last_exp,experience)
            print("Changing",self.last_loc!=location,self.last_loc,location)

            # filtering by companies
            self.job_list_filtered_step_1=job_list

            self.selected_companies_list=[]
            if(company!="company_default"):
                self.last_c_name = company
                self.filter_company(company,job_list)      
            else:
                self.last_c_name="company_default"
            
            #filtering by experience, sent a sorted by experience dictionary
            self.job_list_filtered_step_2=self.job_list_filtered_step_1


            if(experience!="experience_default"):
                self.last_exp = experience
                self.filter_experience(experience)
            else:
                self.last_exp="experience_default"

            self.get_locations_selected_companies(job_list)
            self.job_list_filtered_step_3=self.job_list_filtered_step_2

            self.selected_location_list =[]
            if(location!="location_default$"):
                self.last_loc = location
                self.filter_location(location)
            else:
                self.last_loc="location_default$"  
        else:
            print("\n!!No filter changed, just page filpped. So no need to calculate filter again! It saves time.")



state = stateTracker()


@app.route('/')
@app.route('/jobs', methods=['GET',"POST"])
@app.route('/jobs/<page_num>',methods=['GET',"POST"])
@app.route('/jobs/<page_num>/<company>', methods=['GET',"POST"])
@app.route('/jobs/<page_num>/<company>/<experience>', methods=['GET',"POST"])
@app.route('/jobs/<page_num>/<company>/<experience>/<location>', methods=['GET',"POST"])
def jobs(page_num=1,company="company_default",experience="experience_default",location="location_default$"):


    if(state.route_tracker!="jobs"):
        state.route_tracker="jobs"
        temp =load_saved_jobs()
        state.job_list_filtered_step_1=temp;
        state.job_list_filtered_step_3 = load_saved_jobs()
        state.get_locations_selected_companies(temp)

    ## What is happening here boggles my mind. Both if and else part gets excetued when adding jobs in shorted list

    if request.method == "GET":

        
        max_jobs_in_page=25


        shorted_lst=loading_shortlisted_jobs()

        page_num=int(page_num)

        all_companies_name=get_all_companies_name()        

        job_list = load_saved_jobs()
        state.calculate_filters(company,experience,location,job_list)

        max_page_number = int(len(state.job_list_filtered_step_3)/int(max_jobs_in_page))+1 
        one_page_job_list=state.job_list_filtered_step_3[(page_num-1)*max_jobs_in_page:page_num*max_jobs_in_page]  
        

        lst=[]
        lst2=[]
        dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
        new_dict_keys = ("Job_id","Company_name","Job_position","Job_location","Time_posted","Experience","Job_apply_link")
        for job_dict in one_page_job_list:
            small_dict=dict_filter(job_dict, new_dict_keys)
            lst.append(small_dict)
        for short_dict in shorted_lst:
            small_dict=dict_filter(short_dict, new_dict_keys)
            lst2.append(small_dict)

        print("IN JOBS length of filtered list 3",len(state.job_list_filtered_step_3))
        
        
        return render_template('jobs.html',lst=lst,lst2=lst2,start_page=page_num,max_page_number=max_page_number,
                company_list=all_companies_name,company_selected_arg = company,experience_arg = experience,
                location_arg = location,locations_list = state.locations_list,selected_location_list=state.selected_location_list,
                selected_companies_list=state.selected_companies_list,remove_jobs_by_filter=state.job_list_filtered_step_3)

        
    else:
        try:
            information = request.data
            data = json.loads(information)
            print("Yo yo added in shortlist")
            print(data[0])
            shorted_lst=loading_shortlisted_jobs()  
            for i in data:
                i = eval(i)
                shorted_lst.append(i)

            unique_shorted_jobs_list=[i for n, i in enumerate(shorted_lst) if i not in shorted_lst[n + 1:]] 
            saving_shortlisted_jobs(unique_shorted_jobs_list)
            print("ADDING JOBS")
            return jsonify({'message':'Added to short list'})            
        except Exception as e:
            return jsonify({'message':'Not able to add'+str(e)})


#shorted
@app.route('/shorted', methods=['GET',"POST"])
@app.route('/shorted/<page_num>',methods=['GET',"POST"])
@app.route('/shorted/<page_num>/<company>', methods=['GET',"POST"])
@app.route('/shorted/<page_num>/<company>/<experience>', methods=['GET',"POST"])
@app.route('/shorted/<page_num>/<company>/<experience>/<location>', methods=['GET',"POST"])
def shorted(page_num=1,company="company_default",experience="experience_default",location="location_default$"):
    if(state.route_tracker!="shorted"):
        state.route_tracker="shorted"
        
        job_list = loading_applied_jobs()
        state.job_list_filtered_step_3 = job_list
        state.get_locations_selected_companies(job_list)
    
    if request.method == "GET":

        applied_lst=loading_applied_jobs()

        max_jobs_in_page=25
        page_num=int(page_num)

        all_companies_name=get_applied_companies_name()

        job_list = loading_applied_jobs()
        state.calculate_filters(company,experience,location,job_list)


        max_page_number = int(len(state.job_list_filtered_step_3)/int(max_jobs_in_page))+1 
        one_page_job_list=state.job_list_filtered_step_3[(page_num-1)*max_jobs_in_page:page_num*max_jobs_in_page]  
        
        lst=[]
        lst2=[]
        dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
        new_dict_keys = ("Job_id","Company_name","Job_position","Job_location","Time_posted","Experience","Job_apply_link")
        for job_dict in one_page_job_list:
            small_dict=dict_filter(job_dict, new_dict_keys)
            lst.append(small_dict)

        for short_dict in applied_lst:
            small_dict=dict_filter(short_dict, new_dict_keys)
            lst2.append(small_dict)



        print("SEE Shorted jobs ; GET method")
        return render_template('shorted.html',lst=lst,lst2=lst2,start_page=page_num,max_page_number=max_page_number,
                company_list=all_companies_name,company_selected_arg = company,experience_arg = experience,
                location_arg = location,locations_list = state.locations_list,selected_location_list=state.selected_location_list,
                selected_companies_list=state.selected_companies_list)
    else:
        try:
            information = request.data
            data = json.loads(information)

            applied_lst=loading_applied_jobs()
            for i in data:
                i = eval(i)
                applied_lst.append(i)

            unique_applied_jobs_list=[i for n, i in enumerate(applied_lst) if i not in applied_lst[n + 1:]]
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

def get_applied_companies_name():
    job_list = loading_applied_jobs()
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

@app.route('/nalinkfix', methods=['GET', 'POST'])
def nalinkfix():

    temp = load_saved_jobs();

    lst=[]
    for i,job in enumerate(temp):
        if(job["Job_apply_link"]=="NA"):
            job["Job_apply_link"]="https://www.linkedin.com/jobs/view/"+job['Job_id']
            print("hi")
            t=i

        lst.append(job)

    print(lst[t]["Job_apply_link"])

    saving_base_jobs(lst);
    status_list=["Ha!"]
    #return render_template("allstatus.html")
    return render_template("allstatus.html",lst=status_list)

# saving the jobs with defaulta time which dont have time
@app.route('/fixtime', methods=['GET', 'POST'])
def fixtime():
    temp = load_saved_jobs();

    lst=[]
    for i,job in enumerate(temp):
        if(job["Time_posted"]=="NA" or 'ago' in job["Time_posted"]):
            job["Time_posted"]='2021-05-05'
            t=i

        lst.append(job)

    print(lst[t]["Time_posted"])

    saving_base_jobs(lst);
    return "HI time fixed"


@app.route('/removejobs', methods=['GET', 'POST'])
def removejobs():
    if request.method == "POST":
        try:

            # because it stays in jobs route only, to not to reomve the applied filters on jobs
            if(state.route_tracker!="jobs"):
                state.route_tracker="jobs"

            information = request.data
            data = json.loads(information)

            print(type(data))
            print(type(data[0]))
            print(data[0]);
            remove_jobs_list=[]
            for i in data:

                # this is done when data[0] is a string
                if(type(i) is str):
                    i = eval(i)
                remove_jobs_list.append(i)

            saved_jobs_list = load_saved_jobs()

            lst=[]
            dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
            new_dict_keys = ("Job_id","Company_name","Job_position","Job_location","Time_posted","Experience","Job_apply_link")
            for job_dict in saved_jobs_list:
                small_dict=dict_filter(job_dict, new_dict_keys)
                lst.append(small_dict)

            saved_jobs_list=lst


            print(len(saved_jobs_list))

            
            # to remove for filtered list 
            state.job_list_filtered_step_3 = [job for job in state.job_list_filtered_step_3 if job not in remove_jobs_list]

            # to remove and save into disk
            after_removing_jobs=[]
            after_removing_jobs = [job for job in saved_jobs_list if job not in remove_jobs_list]

            saving_base_jobs(after_removing_jobs)
            print("length of filtered list 3",len(state.job_list_filtered_step_3))
            print(len(after_removing_jobs))
            return jsonify({'message':'Removed from disk!!'})
        except Exception as e:
            print(traceback.format_exc())
            return jsonify({'message':'Not able to remove'+str(e)})


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
