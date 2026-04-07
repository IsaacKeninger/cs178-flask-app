-- ============================================================
--  Job Application Tracker — SQL Schema
--  Tables: users, companies, applications, contacts,
--          interview_rounds, compensation, deadlines
-- ============================================================

-- THIS SCHEMA WAS GENERATED WITH THE HELP OF CLAUDE AI
CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

-- ------------------------------------------------------------
-- 1. USERS
--    One user owns all their applications / data.
--    Extend this if you add auth (e.g. hashed_password).
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id     INT           PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100)  NOT NULL,
    email       VARCHAR(150)  NOT NULL UNIQUE,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 2. COMPANIES
--    Reusable across applications (apply to Google twice?
--    only one "Google" row).
-- ------------------------------------------------------------
CREATE TABLE companies (
    company_id  INT           PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(150)  NOT NULL,
    industry    VARCHAR(100),
    website     VARCHAR(255),
    hq_location VARCHAR(150),
    notes       TEXT
);

-- ------------------------------------------------------------
-- 3. APPLICATIONS  (core table)
--    One row per job you applied (or plan to apply) to.
-- ------------------------------------------------------------
CREATE TABLE applications (
    application_id   INT           PRIMARY KEY AUTO_INCREMENT,
    user_id          INT           NOT NULL,
    company_id       INT           NOT NULL,
    job_title        VARCHAR(150)  NOT NULL,
    job_url          VARCHAR(255),
    -- Lifecycle status
    status           ENUM(
                       'Saved',
                       'Applied',
                       'Phone Screen',
                       'Technical Interview',
                       'Onsite',
                       'Offer',
                       'Rejected',
                       'Withdrawn'
                     ) NOT NULL DEFAULT 'Saved',
    applied_date     DATE,
    source           VARCHAR(100),   -- e.g. LinkedIn, Referral, Company Site
    notes            TEXT,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                             ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)    REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 4. CONTACTS  (recruiters, hiring managers, referrals)
--    Many contacts can be linked to many applications.
-- ------------------------------------------------------------
CREATE TABLE contacts (
    contact_id   INT           PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,                          -- optional — contact may span roles
    first_name   VARCHAR(75)   NOT NULL,
    last_name    VARCHAR(75),
    role         VARCHAR(100),                 -- e.g. "Recruiter", "Hiring Manager"
    email        VARCHAR(150),
    linkedin_url VARCHAR(255),
    phone        VARCHAR(30),
    notes        TEXT,

    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

-- Join table: which contacts are tied to which applications
CREATE TABLE application_contacts (
    application_id  INT  NOT NULL,
    contact_id      INT  NOT NULL,
    relationship    VARCHAR(100),   -- e.g. "Recruiter", "Referral", "Interviewer"
    PRIMARY KEY (application_id, contact_id),

    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id)     REFERENCES contacts(contact_id)         ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 5. INTERVIEW ROUNDS
--    Track every interview stage + feedback.
-- ------------------------------------------------------------
CREATE TABLE interview_rounds (
    round_id         INT           PRIMARY KEY AUTO_INCREMENT,
    application_id   INT           NOT NULL,
    round_number     INT           NOT NULL DEFAULT 1,   -- 1, 2, 3…
    round_type       ENUM(
                       'Phone Screen',
                       'Technical',
                       'System Design',
                       'Behavioral',
                       'Take-Home',
                       'Onsite',
                       'Final'
                     ) NOT NULL,
    scheduled_at     DATETIME,
    duration_minutes INT,
    interviewer_name VARCHAR(150),
    format           VARCHAR(100),    -- e.g. "Zoom", "HackerRank", "In-person"
    topics_covered   TEXT,
    self_rating      TINYINT CHECK (self_rating BETWEEN 1 AND 5),
    feedback         TEXT,            -- recruiter feedback or your own notes
    outcome          ENUM('Pending', 'Passed', 'Failed', 'No Decision') DEFAULT 'Pending',
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 6. COMPENSATION
--    Store the full offer/expected package per application.
-- ------------------------------------------------------------
CREATE TABLE compensation (
    comp_id          INT           PRIMARY KEY AUTO_INCREMENT,
    application_id   INT           NOT NULL UNIQUE,   -- one comp row per application
    base_salary      DECIMAL(12,2),
    signing_bonus    DECIMAL(12,2),
    annual_bonus_pct DECIMAL(5,2),                    -- e.g. 10.00 = 10%
    equity_total     DECIMAL(12,2),                   -- total grant value
    equity_vest_yrs  TINYINT,                         -- vesting period in years
    currency         CHAR(3)       NOT NULL DEFAULT 'USD',
    pay_period       ENUM('Annual','Monthly','Hourly') NOT NULL DEFAULT 'Annual',
    is_offer         BOOLEAN       NOT NULL DEFAULT FALSE,   -- TRUE once offer received
    offer_deadline   DATE,
    notes            TEXT,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 7. DEADLINES
--    Any date-based reminder tied to an application.
-- ------------------------------------------------------------
CREATE TABLE deadlines (
    deadline_id      INT           PRIMARY KEY AUTO_INCREMENT,
    application_id   INT           NOT NULL,
    label            VARCHAR(150)  NOT NULL,    -- e.g. "Submit coding assessment"
    due_date         DATE          NOT NULL,
    due_time         TIME,                       -- optional specific time
    completed        BOOLEAN       NOT NULL DEFAULT FALSE,
    reminder_sent    BOOLEAN       NOT NULL DEFAULT FALSE,
    notes            TEXT,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

-- ============================================================
--  INDEXES  — speed up the most common lookups
-- ============================================================
CREATE INDEX idx_applications_user    ON applications(user_id);
CREATE INDEX idx_applications_status  ON applications(status);
CREATE INDEX idx_applications_company ON applications(company_id);
CREATE INDEX idx_interviews_app       ON interview_rounds(application_id);
CREATE INDEX idx_deadlines_due        ON deadlines(due_date);
CREATE INDEX idx_deadlines_app        ON deadlines(application_id);

-- ============================================================
--  SAMPLE DATA
-- ============================================================

INSERT INTO users (name, email)
VALUES ('Jane Dev', 'jane@example.com');

INSERT INTO companies (name, industry, website, hq_location)
VALUES
  ('Google',    'Technology',      'https://careers.google.com',  'Mountain View, CA'),
  ('Stripe',    'Fintech',         'https://stripe.com/jobs',     'San Francisco, CA'),
  ('Airbnb',    'Travel/Tech',     'https://careers.airbnb.com',  'San Francisco, CA');

INSERT INTO applications (user_id, company_id, job_title, status, applied_date, source)
VALUES
  (1, 1, 'Software Engineering Intern', 'Technical Interview', '2026-02-10', 'LinkedIn'),
  (1, 2, 'Backend Engineer Intern',     'Applied',             '2026-03-01', 'Referral'),
  (1, 3, 'Full Stack Intern',           'Saved',                NULL,        'Company Site');

INSERT INTO contacts (company_id, first_name, last_name, role, email)
VALUES
  (1, 'Alex',  'Smith',  'Recruiter',       'asmith@google.com'),
  (2, 'Maria', 'Lopez',  'Hiring Manager',  'mlopez@stripe.com');

INSERT INTO application_contacts (application_id, contact_id, relationship)
VALUES
  (1, 1, 'Recruiter'),
  (2, 2, 'Hiring Manager');

INSERT INTO interview_rounds
  (application_id, round_number, round_type, scheduled_at, duration_minutes,
   format, topics_covered, self_rating, outcome)
VALUES
  (1, 1, 'Phone Screen', '2026-02-20 10:00:00', 30,  'Zoom',       'Behavioral, background',   4, 'Passed'),
  (1, 2, 'Technical',    '2026-03-05 14:00:00', 60,  'HackerRank', 'Arrays, dynamic programming', 3, 'Pending');

INSERT INTO compensation
  (application_id, base_salary, signing_bonus, equity_total, currency, pay_period, is_offer)
VALUES
  (1, 55000.00, 5000.00, NULL, 'USD', 'Annual', FALSE);

INSERT INTO deadlines (application_id, label, due_date)
VALUES
  (1, 'Complete take-home assessment', '2026-03-15'),
  (2, 'Follow up with recruiter',      '2026-03-20');

-- ============================================================
--  USEFUL STARTER QUERIES
-- ============================================================

-- 1. Dashboard: all applications with company name + status
SELECT
    a.application_id,
    c.name            AS company,
    a.job_title,
    a.status,
    a.applied_date,
    a.source
FROM applications a
JOIN companies c ON a.company_id = c.company_id
WHERE a.user_id = 1
ORDER BY a.applied_date DESC;

-- 2. Upcoming deadlines (next 14 days)
SELECT
    c.name        AS company,
    a.job_title,
    d.label,
    d.due_date
FROM deadlines d
JOIN applications a ON d.application_id = a.application_id
JOIN companies c    ON a.company_id = c.company_id
WHERE d.completed = FALSE
  AND d.due_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 14 DAY
ORDER BY d.due_date;

-- 3. All interview rounds for an application
SELECT
    ir.round_number,
    ir.round_type,
    ir.scheduled_at,
    ir.format,
    ir.topics_covered,
    ir.self_rating,
    ir.outcome,
    ir.feedback
FROM interview_rounds ir
WHERE ir.application_id = 1
ORDER BY ir.round_number;

-- 4. Compensation comparison across offers
SELECT
    c.name        AS company,
    a.job_title,
    co.base_salary,
    co.signing_bonus,
    co.annual_bonus_pct,
    co.equity_total,
    co.offer_deadline
FROM compensation co
JOIN applications a ON co.application_id = a.application_id
JOIN companies c    ON a.company_id = c.company_id
WHERE a.user_id = 1
ORDER BY co.base_salary DESC;

-- 5. Applications by status summary
SELECT
    status,
    COUNT(*) AS total
FROM applications
WHERE user_id = 1
GROUP BY status
ORDER BY FIELD(status,
    'Saved','Applied','Phone Screen',
    'Technical Interview','Onsite','Offer','Rejected','Withdrawn');
