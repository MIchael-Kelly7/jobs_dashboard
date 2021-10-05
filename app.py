import pandas as pd
import dash
import flask
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table
import dash_daq as daq
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
#from dash_bootstrap_templates import load_table_template
from gather_data import *
from datetime import datetime

#from flask_apscheduler import APScheduler
#import pytz

#Use this to launch the app if it's made in a virtual enviroment.
## venv/bin/gunicorn app:server -2 localhost:8050

#class config:
#    SCHEDULER_API_ENABLED = True
#    timezone = ''


import plotly.express as px
from create_db import create_connection, check_average
from urllib.request import urlopen
import json
response = urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json')
counties = json.load(response)
#counties["features"][0]
load_figure_template("cyborg")

CYBORG = {
    "external_stylesheets": [dbc.themes.CYBORG],
    "primary": "#2a9fd6",
    "secondary": "#555",
    "selected": "rgba(255, 255, 255, 0.075)",
    "font_color": "white",
    "font": "Roboto",
}

THEME = CYBORG


styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=THEME["external_stylesheets"])
server = app.server
#app = dash.Dash(__name__, external_stylesheets=THEME["external_stylesheets"])
#app.config.from_object(Config())

## The AP scheduler function was originally intended to refresh the data in the chart every day, however I decided it was cleaner to simply close and restart the app to do this.
#scheduler = APScheduler()
#scheduler.init_app(app)
#scheduler.start()

#scheduler function left for reference
#@scheduler.task('cron', id='do_update_data', hour=5)
#def update_data():
    #tz_central = pytz.timezone('America/Chicago') 
    #datetime_central = datetime.now(tz_central)
    #print("Central time:", datetime_central.strftime("%H:%M:%S"))

# The code below would have been part of the scheduled function, instead I moved it out of the indent and commented out the return and the line after that picks up these variables.
#gather_data()
print('running update data')
with create_connection() as conn:
    dfsql = pd.read_sql('select fips_code, location, case when job_count = 0 THEN NULL else job_count end as job_count from count_by_co_vw', conn)
    df_job_list = pd.read_sql('select * from job_list_vw', conn)
    df_days_posted = pd.read_sql('select distinct max(current_date-post_date) from jobs where active = true order by 1 desc', conn)
    print('done with db')
    conn.close()
longest_posted = df_days_posted.iloc[0,0]
df_active = df_job_list[df_job_list['active'] == True]
job_count = df_active['job_id'].count()
print('final job count:',job_count)
county_count = df_active['location'].nunique()
print('final county count:', county_count)
df_inactive = df_job_list[df_job_list['active'] == False].sort_values('inactive', ascending=False)
#return dfsql,longest_posted, df_active, job_count, county_count, df_inactive


#dfsql,longest_posted, df_active, job_count, county_count, df_inactive = update_data()

#This generates the map.
fig = px.choropleth(dfsql, geojson=counties, locations='fips_code',  color=('job_count'),
                           #color_continuous_scale="Viridis",
                           #color_continuous_scale="jet",
                           range_color=(0, 50),
                           scope="usa",
                           labels={'fips_code':'Fip Code', 'job_count':'Active Job Postings'},
                           hover_name='location',
                           #template='plotly_dark',
                           title='State of TN Jobs'
                          )

#This zooms to the state of TN.
fig.update_geos(fitbounds="locations")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout(clickmode='event+select')







#Page size for data tables
page_size = 10

#Data table of active jobs
data_table = dash_table.DataTable(
    id='jobs_table',
    columns=[{"name": 'Job ID', "id": 'job_id'},
    {"name": 'Job Title', "id": 'job_title'},
    {"name": 'County', "id": 'location'},
    {"name": 'Business Unit', "id": 'business_unit'},
    {"name": 'Department', "id": 'dept'},
    {"name": 'Days Posted', "id": 'days_posted'},
    {"name": 'Probation period', "id": 'probation'}],
    data=df_active.to_dict('records'),
    page_size=page_size,
    filter_action='native',
    sort_action='native',
    style_cell={"backgroundColor": "transparent", "fontFamily": THEME["font"]},
    css=[
        {"selector": "input", "rule": f"color:{THEME['font_color']}"},
        {"selector": "tr:hover", "rule": "background-color:transparent"},
        {"selector": ".dash-table-tooltip", "rule": "color:black"},
    ],
    style_data_conditional=[
        {
            "if": {"state": "active"},
            "backgroundColor": THEME["selected"],
            "border": "1px solid " + THEME["primary"],
            "color": THEME["primary"],
        },
        {
            "if": {"state": "selected"},
            "backgroundColor": THEME["primary"],
            "border": "1px solid" + THEME["secondary"],
            "color": THEME["font_color"],
        },
    ],
)

#Data Table of inactive jobs
inactive_jobs = dash_table.DataTable(
    id='inactive_jobs_table',
    columns=[{"name": 'Job ID', "id": 'job_id'},
    {"name": 'Job Title', "id": 'job_title'},
    {"name": 'County', "id": 'location'},
    {"name": 'Business Unit', "id": 'business_unit'},
    {"name": 'Department', "id": 'dept'},
    {"name": 'Inactive Date', "id": 'inactive'},
    {"name": 'Date Originally Posted', "id": 'post_date'}],
    data=df_inactive[:200].to_dict('records'),
    page_size=page_size,
    filter_action='native',
    sort_action='native',
    style_cell={"backgroundColor": "transparent", "fontFamily": THEME["font"]},
    css=[
        {"selector": "input", "rule": f"color:{THEME['font_color']}"},
        {"selector": "tr:hover", "rule": "background-color:transparent"},
        {"selector": ".dash-table-tooltip", "rule": "color:black"},
    ],
    style_data_conditional=[
        {
            "if": {"state": "active"},
            "backgroundColor": THEME["selected"],
            "border": "1px solid " + THEME["primary"],
            "color": THEME["primary"],
        },
        {
            "if": {"state": "selected"},
            "backgroundColor": THEME["primary"],
            "border": "1px solid" + THEME["secondary"],
            "color": THEME["font_color"],
        },
    ],
)

#Setting up the cards across the top
cards = [
    dbc.Card(
        [
            html.H2(f"{job_count}", className="card-title"),
            html.P("Currently Active Job Postings", className="card-text", style ={'fontSize': '1.5em'}),
        ],
        body=True,
        color="light",
    ),
    dbc.Card(
        [
            html.H2(f"{county_count}", className="card-title"),
            html.P("Counties with Job Openings", className="card-text", style ={'fontSize': '1.5em'}),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(f"{longest_posted}", className="card-title"),
            html.P("Longest Active Job Opening (Days)", className="card-text", style ={'fontSize': '1.5em'}),
        ],
        body=True,
        color="primary",
        inverse=True,
    ),
]

#setting up the graph HTML.
graphs = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig), lg=10),
            ],
            className="mt-4",
        )
    ]
)
#Heading
heading = html.H1("State of Tennessee Job Postings", className="bg-primary text-white p-2", style={"textAlign": 'center'})
hr = html.Hr(style={'color': 'white'})
#Creating a link to the job page
link = html.A('https://www.tn.gov/careers.html',href='https://www.tn.gov/careers.html', title='State of TN Careers Site', target='new-window')
#link_click = html.A(link, n_clicks)
#Creating the paragraph to display the info
paragraph = html.P([f'This page is not affiliated with the State of Tennessee, it is a representation of the jobs scraped from the publicly facing careers page for the State of Tennessee. Please navigate to ', link,' to see current listings and apply. While I strive to keep this information up-to-date, there is no guarantee that it is as this information is not updated real time.'])
active_jobs_descr = html.P('Below is a list of currently active job openings. This list should match the map above. To filter by county, type the county name in the location field, for example "Davidson" or "Shelby". There are also some Statewide or multiple location openings included. To search for a specific title, search in all caps or turn off case sensitivity.')

app.layout = html.Div([
    heading,
    hr,
    dbc.Container(
    [
        #Header("Dash Heart Disease Prediction with AIX360", app),
        html.Hr(),
        dbc.Row([dbc.Col(card) for card in cards]),
        html.Br(),
    ],
    fluid=True,),
    #html.Div(html.P('This is a representation of the jobs scraped from the publicly facing careers page for the State of Tennessee. Please navigate to', html.A( href='https://www.tn.gov/careers.html'),' to see current listings and apply. While I strive to keep this information up-to-date, there is no guarantee that it is as this information is not updated real time.', style={'fontSize': 18})),
    html.Div(paragraph, style={'fontSize': '1.5em', 'fontWeight': 'bold'}),
    dcc.Graph(
        id='active-job-postings',
        figure=fig
    ),
    hr,
    html.Div(active_jobs_descr, style={'fontSize': '1.5em', 'fontWeight': 'bold'}),
    html.Div(data_table,),
    html.Div(html.P('Below are a list of previously posted but jobs. Max = 200'), style={'fontSize': '1.5em', 'fontWeight': 'bold'}),
    html.Div(inactive_jobs,),
    
])






#App callback function. At some point I may update to let users click counties on the map to update the filters on the tables
#@app.callback(
#    Output('click-data', 'children'),
#    Input('basic-interactions', 'clickData'))
#def display_click_data(clickData):
#    info2 = json.dumps(clickData, indent=2)
#    print(clickData.location)
#    return info2

if __name__ == '__main__':
    #from waitress import serve
    #serve(app.server,host='127.0.0.1', port=8050)
    #app.server.run(debug=False)
    app.run(debug=False, reload=True)
    print('through')
    #gunicorn app:app.server
    #app.run()
