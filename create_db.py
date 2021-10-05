from sqlalchemy import create_engine
from sqlalchemy import insert, update, table, text
import subprocess
import configparser
from pathlib import Path
#import pgpasslib
import os
import pandas as pd



def readConfig(cfg):
    localpath = Path(Path.home()/'Code/config')
    config = ('postgres_config.ini')
    configp = configparser.ConfigParser()
    configp.read(localpath/ config)

    if cfg == 'jobs':
        c = configp['jobs']
        #host = c.get('server')
        db = c.get('dbname')
        #username = c.get('username')
        #password = c.get('password')
        return db
        #return host,db,username,password;



def create_connection():
    """Create database connection to to postgres"""
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "postgresql"])
    db_name = readConfig('jobs')

    #checking to see if postgres is actually running
    if stat == 0:
        engine = create_engine(f'postgresql+psycopg2://{os.getlogin()}@localhost/{db_name}') 

        conn = engine.connect()
        #rs = conn.execute("SELECT * FROM pg_catalog.pg_database WHERE datname = 'posted_jobs'")
        return conn
    else: 
        print('Cannot Connect to DB')


def create_table(conn):
    """ create table from create_table_sql
    :param conn: connection object
    :param create_table_sql: a create table statement
    :return:
    
    """
    create_table_sql = """ CREATE TABLE IF NOT EXISTS jobs(
                            job_id integer PRIMARY KEY,
                            job_title varchar(100) NOT NULL,
                            location varchar(60) NOT NULL,
                            dept varchar(60) NOT NULL,
                            probation varchar(60),
                            business_unit varchar(60),
                            post_date date,
                            active bool,
                            inactive date);
                            """

    create_table_sql2 = """ CREATE TABLE IF NOT EXISTS jobs_count(
                            count integer PRIMARY KEY,
                            date_counted date,
                            PRIMARY KEY(date_counted));
                            """

    create_table_sql3 = """ CREATE TABLE IF NOT EXISTS dates_posted(
                            job_id integer,
                            date_checked date,
                            PRIMARY KEY(job_id, date_checked),
                            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
                            );
                            """


    conn.execute(create_table_sql)
    #conn.execute(create_table_sql2)
    #conn.execute(create_table_sql3)

def insert_jobs(conn, a, b, c, d, e, f, g):
    insert_stmt = text("INSERT INTO jobs (job_id, job_title, location, dept, probation, business_unit, post_date, active) \
        VAlUES (:a, :b, :c, :d, :e, :f, :g, TRUE) ON CONFLICT (job_id) DO NOTHING RETURNING job_id")
        #VAlUES (:a, :b, :c, '{d}', '{e}', '{f}', '{g}', TRUE) ON CONFLICT (job_id) DO NOTHING RETURNING job_id")
    #do_nothing = insert_stmt.on_conflict_do_nothing(index_elements=['job_id'])
    #print(do_nothing)
    results = conn.execute(insert_stmt, {'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f, 'g': g})
    #conn.commit()
    #cur = conn.cursor()
    #conn.execute(sql, jobs)
    #conn.commit()
    #return cur.lastrowid

def check_jobs (conn):
    sql = """SELECT job_id from jobs where active = TRUE"""
    conn.row_factory = lambda cursor, row: row[0]
    results = conn.execute(sql)
    results = [r for r, in results]
    return results

def check_inactive_jobs (conn):
    sql = """SELECT job_id from jobs where active = FALSE"""
    conn.row_factory = lambda cursor, row: row[0]
    results = conn.execute(sql)
    results = [r for r, in results]
    return results

def check_average(conn):
    sql = 'select AVG(distinct count) from jobs_count;'
    conn.row_factory = lambda cursor, row: row[0]
    results = conn.execute(sql)
    results = [r for r, in results]
    return results



def update_jobs (conn, missing):
    #conn.row_factory = lambda cursor, row: row[0]
    #cur = conn.cursor()
    update_stmt = text('UPDATE jobs set active= FALSE, inactive=CURRENT_DATE WHERE job_id = :missing')
    conn.execute(update_stmt, {'missing': missing})
    #return cur.lastrowid



def update_job_count (conn, num):

    stmt = text(f'INSERT INTO jobs_count VALUES({num}, current_date) ON CONFLICT (date_counted) DO NOTHING RETURNING date_counted')
    
    #insert_stmt = insert('jobs_count').values(count=num, date_counted=current_date)
    #print(insert_stmt)
    #do_nothing = insert_stmt.on_conflict_do_nothing(index_elements=['date_counted'])
    result = conn.execute(stmt)


def update_dates_posted (conn, job_id):

    stmt = text(f'INSERT INTO dates_posted VALUES({job_id}, current_date) ON CONFLICT (job_id, date_checked) DO NOTHING RETURNING CURRENT_DATE')
    
    #insert_stmt = insert('jobs_count').values(count=num, date_counted=current_date)
    #print(insert_stmt)
    #do_nothing = insert_stmt.on_conflict_do_nothing(index_elements=['date_counted'])
    result = conn.execute(stmt)


def create_fips(conn):
    df = pd.read_csv('TN_FIPS.csv')
    df.head()

    try:
        df.to_sql('tn_fips', conn, index=False)
        print('table created')
        key_stmt = 'ALTER TABLE tn_fips ADD PRIMARY KEY(fips_code)'
        conn.execute(key_stmt)
        print('key added')
    except ValueError:
        print('table already created')


def create_views(conn):
    create_job_fips_vw = """ create or replace view job_fips_vw AS(select tf.fips_code, j.job_id, j.active
                            from jobs j, tn_fips tf
                            where lower(tf.location) = lower(j.location))
                            """

    create_days_posted_vw = """create or replace view days_posted_vw as (
                            select j.job_id, j.job_title, (j.Inactive-j.post_date) as days_posted
                            from jobs j where j.ACTIVE = false);"""

    create_count_by_co_vw = """create  or replace view  count_by_co_vw as (select tf.fips_code, tf.location, 
							coalesce (count(job_id), 0) as job_count
                            from  tn_fips tf left join jobs j on lower(tf.location) = lower(j.location)
                            group by tf.fips_code, tf.location);"""

    create_count_by_bu_vw = """create or replace view count_by_bu_vw as (select
                            business_unit, count(job_id) 
                            from jobs j 
                            group by j.business_unit);"""

    create_no_county_job_vw ="""create or replace view no_county_job_vw as (select j.job_id, j.location  from jobs j
                            except
                            select j.job_id, j.location --, tf.fips_code, tf.location 
                            from jobs j, tn_fips tf
                            where lower(tf.location) = lower(j.location));"""

    create_no_county_counts = """create or replace view no_county_counts_vw as (select count(distinct z.job_id), z.location from 
                            (select j.job_id, j.location  from jobs j
                            except
                            select j.job_id, j.location --, tf.fips_code, tf.location 
                            from jobs j, tn_fips tf
                            where lower(tf.location) = lower(j.location)) z
                            group by z.location);"""

    create_job_list_vw = """create or replace view job_list_vw as (select j.*, (coalesce(inactive,current_date)-post_date) as days_posted, tf.fips_code 
                            from jobs j 
                            left join tn_fips tf on lower(tf.location) = lower(j.location)
                            group by j.job_id, tf.fips_code);"""

    create_active_job_list_vw = """create or replace view active_job_list_vw as (select j.*, (current_date-post_date) as days_posted, tf.fips_code 
                            from jobs j 
                            left join tn_fips tf on lower(tf.location) = lower(j.location)
                            where active = true
                            group by j.job_id, tf.fips_code);"""

    create_inactive_job_list_vw = """create or replace view active_job_list_vw as (select j.*, (inactive-post_date) as days_posted, tf.fips_code 
                                from jobs j 
                                left join tn_fips tf on lower(tf.location) = lower(j.location)
                                where active = true
                                group by j.job_id, tf.fips_code);"""
    

    sqls = (create_job_fips_vw, create_days_posted_vw, create_count_by_co_vw, create_count_by_bu_vw, create_no_county_job_vw, create_no_county_counts )
    for sql in sqls:
        conn.execute(sql)
    
    print('Views created')

    #create_fips_table = """ CREATE TABLE IF NOT EXISTS jobs(
    #                        job_id integer PRIMARY KEY,
    #                        job_title varchar(100) NOT NULL,
    #                        location varchar(60) NOT NULL,
    #                        dept varchar(60) NOT NULL,
    #                        probation varchar(60),
    #                        business_unit varchar(60),
    #                        post_date date,
    #                        active bool,
    #                        inactive date);
    #                        """
    #conn.execute(create_fips_table)

if __name__ == '__main__':
    create_connection()
