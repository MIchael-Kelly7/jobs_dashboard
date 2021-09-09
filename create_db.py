import sqlite3
from sqlite3 import Error


##Currently this is written to use SQLite, I am going to re-write using postgras so I am holding off commenting this file for now.

def create_db(db_file):
    """Create database connection to SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_connection(db_file):
    """Create database connection to SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    """ create table from create_table_sql
    :param conn: connection object
    :param create_table_sql: a create table statement
    :return:
    
    """
    create_table_sql = """ CREATE TABLE IF NOT EXISTS postings(
                            job_id integer PRIMARY KEY,
                            job_title text NOT NULL,
                            location text NOT NULL,
                            dept text NOT NULL,
                            probation text,
                            business_unit text,
                            post_date date,
                            active integer,
                            inactive date);
                            """

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_jobs(conn, jobs):

    sql  = """INSERT OR IGNORE INTO postings(job_id, job_title, location, dept, probation, business_unit, post_date, active)
    VALUES(?,?,?,?,?,?, date('now'),?)"""
    cur = conn.cursor()
    cur.execute(sql, jobs)
    conn.commit()
    return cur.lastrowid

def check_jobs (conn):
    sql = """SELECT job_id from postings where active = 1"""
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    cur.execute(sql)
    output = cur.fetchall()
    return output


def update_jobs (conn, missing_id):
  
    #conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    cur.execute("UPDATE postings SET active = 0, inactive = date('now') WHERE job_id IN (%s)" %','.join('?'*len(missing_id)), missing_id)
    conn.commit()
    return cur.lastrowid



def update_job_count (conn, count):
    pass