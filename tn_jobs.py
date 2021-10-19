
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os

def error_exit():
    pass

def scroll_page():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")

    with webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options) as driver:
        driver.get('https://careers.edison.tn.gov/psc/hrprdrs/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U')

        time.sleep(2)
        #defining current_height and new_height variables to use in while loop.
        current_height = 0
        new_height = 1

        #This will compare current_height to new_height until they equal each other. Values are based on the scroll height of the element. 
        #Each scroll should reload the page, so the element has to be re-established within the loop, otherwise the element will be stale.
        while current_height != new_height:
            #set current_height = scrollheight
            current_height = driver.execute_script("return document.getElementById('win0divHRS_AGNT_RSLT_I\$grid\$0').scrollHeight")
            element = driver.find_element_by_id(r"win0divHRS_AGNT_RSLT_I\$grid\$0")
            driver.execute_script("document.getElementById('win0divHRS_AGNT_RSLT_I\$grid\$0').scrollBy(0,12000)")
            #Initially tried to use a wait to wait for the element to be stale, but there wasn't really a great option here.
            #I also couldn't use something like is_visible as the element would end up being stale after the page reload. Therefore a simple wait worked.
            time.sleep(1)
            driver.execute_script("document.getElementById('win0divHRS_AGNT_RSLT_I\$grid\$0').scrollBy(0,12000)")
            #time.sleep(2)
            #get the new scroll height
            new_height = driver.execute_script("return document.getElementById('win0divHRS_AGNT_RSLT_I\$grid\$0').scrollHeight")
            #printing out the current and new height to help see how they change.
            print(current_height, new_height)


        #assign driver object's page source to the page variable to start scraping. This will be the fully expanded 
        page = driver.page_source
        return page


def scrape_jobs(page):

    html = BeautifulSoup(page, 'html5lib')

    selection = html.find_all('li', id=re.compile("HRS_AGNT_RSLT_I\$.*"))
    selection2 = html.find('div', class_='ps-htmlarea')


    print(len(selection))
    #print (selection[].get_text())
    ##for x in selection:
    #    print(x.get_text())
    #post_date = html.find_all('span', id=re.compile("SCH_OPENED\$.*"))
    #print(post_date)
    return html



if __name__ == '__main__':
    print('running again')
    scrape_jobs()
#     job_title = html.find_all('span', id=re.compile("SCH_JOB_TITLE\$.*"))
#     job_id = html.find_all('span', id=re.compile("HRS_APP_JBSCH_I_HRS_JOB_OPENING_ID\$.*"))
#     location = html.find_all('span', id=re.compile("LOCATION\$.*"))
#     dept = html.find_all('span', id=re.compile("HRS_APP_JBSCH_I_HRS_DEPT_DESCR\$.*"))
#     pp = html.find_all('span', id=re.compile("JOB_FUNCTION\$.*"))
#     bu = html.find_all('span', id=re.compile("HRS_BU_DESCR\$.*"))
#     post_date = html.find_all('span', id=re.compile("SCH_OPENED\$.*"))
#     ##items = [job_title, job_id, location, dept, pp, bu, post_date]
#     ##i = 0


# for (a,b,c,d,e,f, g) in zip(job_id, job_title, location, dept, pp, bu, post_date):
#     sql [] = '''INSERT INTO postings(job_id, job_title, location, dept, probation, business_unit, post_date)
# VALUES({a},{b},{c},{d},{e},{f},{g})'''
#     return sql []
# #    print(a.get_text(),b.get_text(),c.get_text(),d.get_text(),e.get_text(),f.get_text(), g.get_text())
