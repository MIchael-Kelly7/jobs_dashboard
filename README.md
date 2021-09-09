# State of TN Jobs Dashboard
Looking at publicly avaliable data for Jobs posted by the State of TN

## Current capability
Currently this python script will check if a sqlite db has been created, create the file if not then scrape the State of TN public job posting website and push that information to said sqlite file.

## TODOs:
- Update script to use Postgras
- Create new tables to handle number of job posts per day
- Determine method to post report or deploy dashboard. Current considerations include Pelican, Streamlit and a few others.
- Include requirements.txt
- Update script with other possible data points we can gather from this potentially limited data set
- Start creating dashboard items or report items
- Examine possibility to adding a map giving some kind of informaton on which county the job posting are in or a way to see what the current job postings are by county.

### Reason for changing to postgras
SQLite has some limitations, for example, it does not have a bool data type. Dates are not stored as dates so currently the code will use the run date as the posting date. Once this is using postgras, the code will be updated to use the posting date included on the site.
