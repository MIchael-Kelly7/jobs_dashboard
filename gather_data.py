from create_db import *
from pathlib import Path
import tn_jobs
import re
import numpy as np
#import smtplib, ssl
import sys

def find_intersects(lst1, lst2):
    return set(lst1).intersection(lst2)

def gather_data():
    #setting name of the file we will be opening or creating if not created.
    ##db_name = Path('postings.db')

    #checking to see if DB exists, if not create it.
    #if db_name.is_file():
    #    print('Database found, name:', db_name)
    #else:
    #    print('Database not found. Creating...')
    #    create_db(db_name)
    #    print('Database Created, ', db_name)

    #connecting to db then creating a cursor
    with create_connection() as conn:

        #if we can connect to the database then create our tables using a CREATE TABLE IF NOT EXISTS sql. If the tables exist no action will be taken.
        if conn is not None:
            create_table(conn)
            print('Table created or exists')
            create_views(conn)
            print('views created')
        else:
            print('Cannot create table')
            sys.exit()

        #getting the data from our selenium session into a variable to feed into 
        #page = scroll_page()

        #I believe this should work but will need to wait for a data change in the source to confirm this.
        html = tn_jobs.scrape_jobs(tn_jobs.scroll_page())


        #Using the info from the html variable to create the data, keep in mind, here they are simply the HTML values. 
        job_title = html.find_all('span', id=re.compile("SCH_JOB_TITLE\$.*"))
        job_id = html.find_all('span', id=re.compile("HRS_APP_JBSCH_I_HRS_JOB_OPENING_ID\$.*"))
        location = html.find_all('span', id=re.compile("LOCATION\$.*"))
        dept = html.find_all('span', id=re.compile("HRS_APP_JBSCH_I_HRS_DEPT_DESCR\$.*"))
        pp = html.find_all('span', id=re.compile("JOB_FUNCTION\$.*"))
        bu = html.find_all('span', id=re.compile("HRS_BU_DESCR\$.*"))
        post_date = html.find_all('span', id=re.compile("SCH_OPENED\$.*"))
        jobs_found = html.find('div', class_='ps-htmlarea')
        job_count = jobs_found.get_text().split(' ')[0]
        if int(job_count) == int(len(job_id)):
            print('Job count:', int(job_count))
        else: 
            print('job_id count:',len(job_id))
            print('Job count:', int(job_count))
            print('qutting')
            sys.exit('Job id count does not match active jobs count.')
        #To keep rows in the db low, this was removed
        #update_job_count(conn, job_count)
        #To keep rows in the db low, this was removed
        #update_job_count(conn, jobs_found)    --Not ready to add yet. Going to switch to postgras SQL first to better handle dates. Will record the number of jobs posted on the date scraping is done.



        #pulling list of job ids that are currently showing active in the database
        id_list = check_jobs(conn)
        ## Note, it's likely you can do missing = np.setdiff1d(id_list, job_id) however, this could be a bit more difficult to debug so wanted to get just the job_ids in a list this route.
        active_postings = ([x.get_text() for x in job_id])
        inactive_list = check_inactive_jobs(conn)
        #ikactive_inactive = active_postings, inactive_list)
        #print('active_inactive:',len(active_inactive))

#The below was added to potentially send an email. If the numbers start to be inconsistent then I'll work on adding this.
        #if 1 == False:
        #    port = 1025
        #    smpt_server = 'localhost'
        #    #password = input('Type password and press enter')
        #    sender_email = "my@gmail.com"  # Enter your address
        #    receiver_email = "your@gmail.com"  # Enter receiver address
        #    context = ssl.create_default_context()
        #    message = """\
        #        Subject: Hi there
        #        
        #        This message is sent from Python."""
        #    #with smtplib.SMTP_SSL(smpt_server, port, context=context) as server:
        #    with smtplib.SMTP(smpt_server, port) as server:
        #        #server.login(sender_email, password)
        #        server.sendmail(sender_email, receiver_email, message)



        #finds out which job ids are not in the current scraping of the page then uses the missing list to set those job ids inactive as of today's date.
        missing = np.setdiff1d(id_list, active_postings)
        missing_list = missing.tolist()
        print(missing_list)
        #compares the missing job ids to all active job ids.
        #update_jobs(conn, missing_list)
        for miss in missing_list:
            update_jobs(conn, miss)
            
        #This loop is what actually adds the new entires into the database. I suspect there's a quicker way to do this
        #Potentially get the list of active job postings in the db and add to dataframe then create a new dataframe with the remaining job ids, will save time/writes
        for (a,b,c,d,e,f, g) in zip(job_id, job_title, location, dept, pp, bu, post_date):
            
            #jobs = (a.get_text(),b.get_text(),c.get_text(),d.get_text(),e.get_text(),f.get_text(), 1)
            #I may eventually change this to put all the info into a dataframe then push using to_sql, but I would have to see if this would allow me toe insert or ignore.
            insert_jobs(conn, a.get_text(),b.get_text(),c.get_text(),d.get_text(),e.get_text(),f.get_text(), g.get_text())
            #update_dates_posted(conn, a.get_text())

        create_fips(conn)
        #create_views(conn)

        #closing connection


if __name__ == '__main__':
    gather_data()