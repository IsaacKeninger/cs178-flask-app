# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT
""" 
uses flask: done
rds correctly used: done
dyamodb:done
crud: done
sql join: Done
rds in vpc: Done
creds not stored in repo: done
readme: wip
"""

from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
from datetime import timezone
import boto3 # for dynamodb
from dbCode import *
from flask import session

# CLAUDE AI for initializing dynamo db with event log function.
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
event_table = dynamodb.Table('event_log')

# function for logging to the dynamodb table
def log_event(app_id, event, company, old_val=None, new_val=None):
    event_table.put_item(Item={
        'app_id': str(app_id),
        'company': company,
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
    """
    Endpoint for rendering the home page of the tracker.
    """
    return render_template('home.html')

@app.route('/add-application', methods=['GET', 'POST'])
def add_application():
    """
    End Point for /add-application. 
    1. Accepts data from html forms, executes a query to database to get database name. 
    2. If the company is already in companies table, else if the company is not already in comnpanies then add it 
    3. Find the ID of the company im finding, then insert into applications information of the application
    4. The event is then logged onto dynamo db event log
    """

    if request.method == 'POST':
        # Extract form data
        company_name = request.form['company_name']
        job_title = request.form['job_title']
        job_url = request.form['job_url']
        applied_date = request.form['applied_date']
        source = request.form['source']
        notes = request.form['notes']

        # THIS DATABASE LOGIC ADDITION WAS PARTIALLY GENERATED WITH THE HELP OF CLAUDE AI, NON DYNAMO DB IMPLEMENTATION PART
        try:
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
            log_event(new_id, 'INSERT', company_name)

            flash('Application added successfully!', 'success')  # 'success' is a category; makes a green banner at the top
            # Redirect to home page or another page upon successful submission
            return redirect(url_for('home'))
        
        except Exception as exception:
            flash('Application addition failed...', 'danger')
            return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('add_application.html')

@app.route('/delete-application',methods=['GET', 'POST'])
def delete_application():
    """
    1. recieves the company name and job title from user
    2. extracts query to match company_id to jobtitle and removes company from applications. 
    3. event is then logged.
    """
    if request.method == 'POST':
        # Extract form data
        company_name = request.form['company_name']
        job_title = request.form['job_title']
        try:
            res = execute_query(
                "SELECT company_id FROM companies WHERE name = %s",
                (company_name,)
                )
            if res:
                company_id = res[0]['company_id']
                # get apps id prior deletion
            result = execute_query(
                "SELECT application_id FROM applications WHERE company_id = %s AND job_title = %s",
                (company_id, job_title)
            )

            execute_write(
                "DELETE FROM applications WHERE company_id = %s AND job_title = %s",
                (company_id, job_title)
            )

            if result:
                app_id = result[0]['application_id']
                log_event(app_id, 'DELETE', company_name)

        except Exception as exception:
            flash('Application Deletion failed...', 'danger')
            return redirect(url_for('home'))

        flash('Application deleted successfully!', 'warning') 
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('delete_application.html')

@app.route("/update-application",methods=['GET', 'POST'])
def update_application():
    """
    1. select application to change
    2. match company id to job title
    3. update application in applications table
    4. log event
    """
    if request.method == 'POST':
        # extract form data
        company_name = request.form['company_name']
        job_title = request.form['job_title']
        job_url = request.form.get('job_url','')
        applied_date = request.form.get('applied_date', '')
        source = request.form.get('source', '')
        notes = request.form.get('notes', '')

        try:
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
            if result:
                app_id = result[0]['application_id']
                log_event(app_id, 'UPDATE', company_name, old_val=job_title, new_val=f"{job_url}, {source}, {notes}")


            flash('Application updated successfully!', 'success')  # 'success' is a category; makes a green banner at the top
            # Redirect to home page or another page upon successful submission
            return redirect(url_for('home'))
        except Exception as exception:
            flash('Application updating failed...', 'danger')
            return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('update_application.html')

@app.route('/display-applications')
def display_applications():
    """
    1. Display applications in lsit format
    """

    # MY COMPLEX SQL QUERY. IT selects all the items from applications, joins the companies with applications to find which applications relate to which company
    try:
        applications_list = execute_query("""SELECT applications.*, companies.name AS company_name FROM applications JOIN companies WHERE applications.company_id = companies.company_id;""")
        if applications_list: # meaning there is a result
            return render_template('display_applications.html', applications=applications_list)
        else: # meaning there is nothing in list
            return redirect(url_for('home'))
    except Exception as exception:
        flash('Failed to Display Applications: ', 'danger')
        return redirect(url_for('home'))

# DYNAMO DB IMPLEMENTATION
@app.route('/display-event-log')
def display_event_log():
    """
    display event log from dynamo db
    """
    try:
        # dispalys the dynamo db table
        response = event_table.scan()
        events = response['Items']
        events.sort(key=lambda x: x['timestamp'], reverse=True) # this was made by claude, was tricky to find way to sort them by time
        return render_template('event_log.html', events=events)
    except Exception as exception:
        flash('Failed to load event_log...')
        return redirect(url_for('home'))

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
