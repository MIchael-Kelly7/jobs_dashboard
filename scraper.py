import requests
import re
from bs4 import BeautifulSoup
#page = requests.get('https://careers.edison.tn.gov/psc/hrprdrs/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U')
page = open('Careers.html')

html = BeautifulSoup(page, 'html5lib')
#print(html)
selection = html.find_all('li', id=re.compile("HRS_AGNT_RSLT_I\$.*"))
#selection = html.findAll('li', id=lambda L: L and L.startswith('HRS_AGNT_RSLT_I\$'))
#selection = html.find_all("li", id=re.compile("#HRS_AGNT_RSLT_I\$0_row_\d+"))

#selection = html.select('#HRS_AGNT_RSLT_I\$0_row_0')
#selection = selection.select('div', selection)
#selection = html.select('div', {'id:' 'HRS_AGNT_RSLT_I\$0_row_0'})
#selection = html.select('div', {'id:' 'HRS_AGNT_RSLT_I\$0_row_0'})
#str(selection)
#print(selection.getText())

print(len(selection))
for selections in selection:
    print(selections.getText())

##win0divLOCATION\$0
#win0divHRS_APP_JBSCH_I_HRS_DEPT_DESCR\$0
#win0divJOB_FAMILY_LABEL\$0
#win0divJOB_FUNCTION\$0
#win0divHRS_BU_DESCR\$0
#win0divSCH_OPENED\$0
#HRS_AGNT_RSLT_I\$0_row_1
#SCH_JOB_TITLE\$0
#HRS_AGNT_RSLT_I\$0_row_0