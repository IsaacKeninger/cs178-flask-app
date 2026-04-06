# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT
""" 
uses flask: done
rds correctly used: done
dyamodb:wip
crud: wip
sql join: wip
rds in vpc: wip
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

# CLAUDE
# for dynamodb log
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# event_table = dynamodb.Table('event_log')

# #function for logging to the dynamodb table
# def log_event(app_id, event, old_val=None, new_val=None):
#     event_table.put_item(Item={
#         'application_id': str(app_id),
#         'timestamp': datetime.now(timezone.utc).isoformat(),
#         'event': event,
#         'old_val': old_val or '',
#         'new_val': new_val or ''
#     })

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
        
        execute_write( 
            "INSERT IGNORE INTO companies (name) VALUES (%s)", # ignore skips insert if duplicate exists
            (company_name,)
        )

        res = execute_query(
            "SELECT company_id FROM companies WHERE name = %s",
            (company_name,)
        )

        company_id = res[0]['company_id']

        execute_write(
            "INSERT INTO applications (company_id, job_title, job_url, applied_date, source, notes) VALUES (%s, %s, %s, %s, %s, %s)",
            (company_name, job_title, job_url, applied_date, source, notes)
        )

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
        
        # Process the data (e.g., add it to a database)
        
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
    applications_list = execute_query("""SELECT * FROM applications;""")#     
    return render_template('display_applications.html', applications=applications_list)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
