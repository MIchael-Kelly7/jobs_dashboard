# State of TN Jobs Dashboard
Looking at publicly avaliable data for Jobs posted by the State of TN

## Current capability
Currently this python script will check if a postgresql db has been created and if it has populate with the appropriate tables. It then scrapes public State of TN job postings and displays them in a Dash app dashboard complete with choropleth map.

## TODOs:
- Update script to use Postgras  DONE
- Create new tables to handle number of job posts per day DONE
- Include requirements.txt DONE
- Update script with other possible data points we can gather from this potentially limited data set. somewhat done
- Start creating dashboard items or report items DONE
- Examine possibility to adding a map giving some kind of informaton on which county the job posting are in or a way to see what the current job postings are by county. DONE
