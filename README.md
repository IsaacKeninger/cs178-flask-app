# Job Application Tracker

**CS178: Cloud and Database Systems — Project #1**
**Author:** Isaac Keninger
**GitHub:** IsaacKeninger

---

## Overview

This project is a crud project for tracking job applications. Allowing for the recording of applications and full crud compatability, users can keep track of and compile their job applications into one website. 

---

## Technologies Used

- **Flask** — Python web framework
- **AWS EC2** — hosts the running Flask application
- **AWS RDS (MySQL)** — relational database for Application and company data realationships
- **AWS DynamoDB** — non-relational database for event logging of crud operations
- **GitHub Actions** — auto-deploys code from GitHub to EC2 on push

---

## Project Structure

```
CS178-FLASK-APP/
├── .github
   ├── deploy.yml
├── templates
   ├── add_application.html
   ├── delete_applications.html
   ├── display_applications.html
   ├── display_users.html
   ├── event_log.html
   ├── home.html
   ├── update_application.html
├── .gitignore
├── dbCode.py            # Database helper functions (MySQL connection + queries)
├── flaskapp.py          # Main Flask application — routes and app logic
├── creds_sample.py      # Sample credentials file (see Credential Setup below)
├── flaskapp.py          # Main Flask application — routes and app logic
├── job_tracker_schema.sql # Job Application Tracker DB schema
└── README.md
```

---

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install dependencies:

   ```bash
   pip3 install flask pymysql boto3
   ```

3. Set up your credentials (see Credential Setup below)

4. Run the app:

   ```bash
   python3 flaskapp.py
   ```

5. Open your browser and go to `http://127.0.0.1:8080`

---

## How to Access in the Cloud

The app is deployed on an AWS EC2 instance. To view the live version:

```
http://98.88.23.115:8080
```

_(Note: the EC2 instance may not be running after project submission.)_

---

## Credential Setup

This project requires a `creds.py` file that is **not included in this repository** for security reasons.

Create a file called `creds.py` in the project root with the following format (see `creds_sample.py` for reference):

```python
# creds.py — do not commit this file
host = "your-rds-endpoint"
user = "admin"
password = "your-password"
db = "your-database-name"
```

---

## Database Design

### SQL (MySQL on RDS)

This database schema for the job_tracker schema tracks data from user applications and companies. The primary realationship is between application and companies, where the companies applied to are related to each other directly. Otherwise, the database stores information about the applications themselves.

**Example:**

- `applications` — stores user applications; primary key is `applications_id`
- `companies` — stores company information; foreign key links to `applications table`

The JOIN query used in this project: 
SELECT applications.*, companies.name AS company_name FROM applications JOIN companies WHERE applications.company_id = companies.company_id;

This Query selects all items from applications,and the company names from the companies table then joins applications and companies matching where the applicatino rows company_id is equal to the companies_id. This matches applications with companies in the db. 

### DynamoDB

This dynamo db table keeps track of crud operations that occur in the project. These attributes include ones such as which application was changed, the time it was, and the operations that occured. This connects as a way to quickly reference events that happen with the use of a nosql db. The partition key is app_id. 

- **Table name:** `event_log`
- **Partition key:** `app_id`
- **Used for:** Tracking when crud operations occur with time dates and other information. 

---

## CRUD Operations

| Operation | Route      | Description    |
| --------- | ---------- | -------------- |
| Create    | `/add-application` | Adds a job application to the tracker |
| Read      | `/delete-application` | Deletes a job application from the tracker |
| Update    | `/update-application` | Updates fields of an application |
| Delete    | `/display-applications` | Displays all applications |

---

## Challenges and Insights

The hardest part of creating this application was implementing the logic for each of the crud operations. This includes making the queries as well as storing and validing the output of those queries. I learned a lot about making the queries themselves and how to handle the data after recording the output. 

---

## AI Assistance

Claude AI was used for code generation of parts of the project. In particular, Claude AI was used for support in creating and initializing the dynamo db table as an event table, the database logic for the add_application endpoint, and for the events.sort() on line 233 to help me sort event logger events by timestamp. By so using claude for these sections, I was able to learn how to sort events with lambda functions, understand and conceputalize the logic for the backend endpoints, and streamline initalizing the boilerplate dynamo db code. Claude generated the sql schema as well.
