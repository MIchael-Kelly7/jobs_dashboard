from create_db import create_db, insert_jobs, create_connection, create_table, check_jobs, update_jobs, update_job_count
from pathlib import Path
from tn_jobs import scrape_jobs, scroll_page
import re
import numpy as np


def main():
    #setting name of the file we will be opening or creating if not created.
    db_name = Path('postings.db')

    #checking to see if DB exists, if not create it.
    if db_name.is_file():
        print('Database found, name:', db_name)
    else:
        print('Database not found. Creating...')
        create_db(db_name)
        print('Database Created, ', db_name)

    #connecting to db then creating a cursor
    conn = create_connection(db_name)
    cur = conn.cursor()

    #if we can connect to the database then create our tables using a CREATE TABLE IF NOT EXISTS sql. If the tables exist no action will be taken.
    if conn is not None:
        create_table(conn)
        print('Table created or exists')
    else:
        print('Cannot create table')

    #getting the data from our selenium session into a variable to feed into 
    #page = scroll_page()

    #I believe this should work but will need to wait for a data change in the source to confirm this.
    html = scrape_jobs(scroll_page())


    #Using the info from the html variable to create the data, keep in mind, here they are simply the HTML values. 
    job_title = html.find_all('span', id=re.compile("SCH_JOB_TITLE\$.*"))
    job_id = html.find_all('span', id=re.compile("HRS_APP_JBSCH_I_HRS_JOB_OPENING_ID\$.*"))
    location = html.find_all('span', id=re.compile("LOCATION\$.*"))
    dept = html.find_all('span', id=re.compile("HRS_APP_JBSCH_I_HRS_DEPT_DESCR\$.*"))
    pp = html.find_all('span', id=re.compile("JOB_FUNCTION\$.*"))
    bu = html.find_all('span', id=re.compile("HRS_BU_DESCR\$.*"))
    post_date = html.find_all('span', id=re.compile("SCH_OPENED\$.*"))
    jobs_found = html.find('div', class_='ps-htmlarea')

    #update_job_count(conn, jobs_found)    --Not ready to add yet. Going to switch to postgras SQL first to better handle dates. Will record the number of jobs posted on the date scraping is done.


    #I do not believe this assignment is needed due to a structure change, keeping just in case I'm wrong here.
    #cur = conn.cursor()
    #pulling list of job ids that are currently showing active in the databse
    id_list = check_jobs(conn)
    ## Note, it's likely you can do missing = np.setdiff1d(id_list, job_id) however, this could be a bit more difficult to debug so went this route.
    active_postings = ([x.get_text() for x in job_id])

    #finds out which job ids are not in the current scraping of the page then uses the missing list to set those job ids inactive as of today's date.
    missing = np.setdiff1d(id_list, active_postings)
    missing_list = missing.tolist()
    print(missing_list)
    #compares the missing job ids to all active job ids.
    update_jobs(conn, missing_list)


    #This loop is what actually adds the new entires into the database. I am sure there is a quicker way to do this. I am holding off making any changes here until I update to use postgras.
    for (a,b,c,d,e,f, g) in zip(job_id, job_title, location, dept, pp, bu, post_date):
        
        jobs = (a.get_text(),b.get_text(),c.get_text(),d.get_text(),e.get_text(),f.get_text(), 1)
        insert_jobs(conn, jobs)

    #closing connection
    conn.close()


if __name__ == '__main__':
    main()