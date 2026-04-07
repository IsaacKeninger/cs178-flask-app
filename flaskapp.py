# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT
""" 
uses flask: done
rds correctly used: done
dyamodb:wip
crud: wip
sql join: Done
rds in vpc: Done
creds not stored in repo: done
readme: wip
"""

from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import datetime
from datetime import timezone
import boto3 # for dynamodb
from dbCode import *

# CLAUDE for initializing dynamo db and event table
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
event_table = dynamodb.Table('event_log')

#function for logging to the dynamodb table
def log_event(app_id, event, old_val=None, new_val=None):
    event_table.put_item(Item={
        'app_id': str(app_id),
        'timestamp': datetime.datetime.now(timezone.utc).isoformat(),
        'event': event,
        'old_val': old_val or '',
        'new_val': new_val or ''
    })

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone

@app.route('/')
def home():
    return render_template('home.html')

# @app.route('/display_companies')
# def display_companies():
#     rows = execute_query("""SELECT * FROM companies;""")
#     return render_template('display_companies.html', companies=rows)
    
@app.route('/add-application', methods=['GET', 'POST'])
def add_application():
    if request.method == 'POST':
        # Extract form data
        company_name = request.form['company_name']
        job_title = request.form['job_title']
        job_url = request.form['job_url']
        applied_date = request.form['applied_date']
        source = request.form['source']
        notes = request.form['notes']
        
        # Process the data (e.g., add it to a database)
        # THIS DATABASE LOGIC ADDITION WAS PARTIALLY GENERATED WITH THE HELP OF CLAUDE AI
        res = execute_query(
            "SELECT company_id FROM companies WHERE name = %s",
            (company_name,)
        )
        if len(res) == 0: # If the result of the query is nothing, company isnt present
            # add comapny to companies table
            execute_write(
                "INSERT INTO companies (name) VALUES (%s)",
                (company_name,)
            )
            # get id of company in table of name im looking for
            res = execute_query(
                "SELECT company_id FROM companies WHERE name = %s",
                (company_name,)
            )
        # company_id key
        company_id = res[0]['company_id']

        execute_write(
            "INSERT INTO applications (user_id, company_id, job_title, job_url, applied_date, source, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (1, company_id, job_title, job_url, applied_date, source, notes)
        )

        new_application = execute_query(
            "SELECT application_id FROM applications WHERE company_id = %s AND job_title = %s",
            (company_id, job_title)
        )
        new_id = new_application[0]['application_id']
        log_event(new_id, 'INSERT')


        flash('Application added successfully!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('add_application.html')

@app.route('/delete-application',methods=['GET', 'POST'])
def delete_application():
    if request.method == 'POST':
        # Extract form data
        company_name = request.form['company_name']
        job_title = request.form['job_title']
        
        res = execute_query(
            "SELECT company_id FROM companies WHERE name = %s",
            (company_name,)
        )
        if res:
            company_id = res[0]['company_id']
            execute_write(
                "DELETE FROM applications WHERE company_id = %s AND job_title = %s",
                (company_id, job_title)
            )

        # add to dynamo db
        result = execute_query(
            "SELECT application_id FROM applications WHERE company_id = %s AND job_title = %s",
            (company_id, job_title)
        )
        if result:
            app_id = result[0]['application_id']
            log_event(app_id, 'DELETE')


        flash('Application deleted successfully!', 'warning') 
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('delete_application.html')

@app.route("/update-application",methods=['GET', 'POST'])
def update_application():
    if request.method == 'POST':
        # extract form data
        company_name = request.form['company_name']
        job_title = request.form['job_title']
        job_url = request.form['job_url']
        applied_date = request.form['applied_date']
        source = request.form['source']
        notes = request.form['notes']

        # Look up company_id from company name
        res = execute_query(
            "SELECT company_id FROM companies WHERE name = %s",
            (company_name,)
        )
        if res:
            company_id = res[0]['company_id']
            execute_write(
                """UPDATE applications
                   SET job_url = %s, applied_date = %s, source = %s, notes = %s
                   WHERE company_id = %s AND job_title = %s""",
                (job_url, applied_date, source, notes, company_id, job_title)
            )
        
        result = execute_query(
            "SELECT application_id FROM applications WHERE company_id = %s AND job_title = %s",
            (company_id, job_title)
        )
        if result == True:
            app_id = result[0]['application_id']
            log_event(app_id, 'UPDATE', old_val=job_title, new_val=f"{job_url}, {source}, {notes}")


        flash('Application updated successfully!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('update_application.html')

@app.route('/display-applications')
def display_users():
    # hard code a value to the users_list;
    # note that this could have been a result from an SQL query :) 
    applications_list = execute_query("""SELECT applications.*, companies.name AS company_name FROM applications JOIN companies WHERE applications.company_id = companies.company_id;""")#     
    return render_template('display_applications.html', applications=applications_list)

@app.route('/display-event-log')
def display_event_log():
    # dispalys the dynamo db table
    response = event_table.scan()
    events = response['Items']
    events.sort(key=lambda x: x['timestamp'], reverse=True) # this was made by claude, was tricky to find way to sort them by time
    return render_template('event_log.html', events=events)

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
