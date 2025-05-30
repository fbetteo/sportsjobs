
<insert_step>
conn = start_postgres_connection()
    with conn as conn:
        record = {
            "name": job_data.get("Name"),
            "status": "Open",
            "start_date": self.current_time,
            "url": job_data.get("url"),
            "location": job_data.get("location"),
            "country": job_data.get("country"),
            "country_code": job_data.get("country_code"),
            "seniority": job_data.get("seniority"),
            "description": job_data.get("desciption"),
            "sport_list": (
                job_data.get("sport_list")[0]
                if job_data.get("sport_list")
                else None
            ),
            "skills": job_data.get("skills"),
            "job_area": job_data.get("job_area"),
            "remote": job_data.get("remote"),
            "remote_office": job_data.get("remote_office"),
            "salary": str(job_data.get("salary")),
            "language": job_data.get("language", ["English"]),
            "company": job_data.get("company", self.company),
            "industry": (
                job_data.get("industry")[0]
                if job_data.get("industry")
                else None
            ),
            "job_type": "Permanent",
            "hours": job_data.get("hours"),
            "logo_permanent_url": self.logo[0].get("url"),
            "post_duration": 30,
            "post_tier": "Free",
            "featured": "1 - regular",
            "creation_date": self.now,
        }
</insert_step>

<template>
{
"jobs": [
	{
		"job_id" : 8019,
		"name" : "Lead Software Engineer",
		"status" : "Open",
		"start_date" : "2025-05-14",
		"url" : "https:\/\/www.teamworkonline.com\/baseball-jobs\/miamibaseball\/miami-marlins\/lead-software-engineer-2118155",
		"location" : "Miami · FL",
		"country" : "united states",
		"country_code" : "US",
		"seniority" : "With Experience",
		"description" : "**Company Overview**At the Miami Marlins, we make waves — on *and* off the field.  We’re built for sustainable success thanks to our commitment to be great teammates, bold innovators, and thinking long\\-term. These three pillars guide us in championing a winning culture across the organization. The work we do doesn’t just impact our team — it reaches fans and communities across South Florida. **Position Summary** As a Lead Software Engineer, you will play a pivotal role in designing, developing, and optimizing software applications that support the entire Baseball Operations department. This role requires technical expertise in software development, architecture, and cloud\\-based infrastructure, as well as leadership capabilities to mentor and guide other engineers. You will collaborate closely with analysts, scouts, coaches, and other baseball personnel to create innovative solutions that enhance decision\\-making and operational efficiency.**Essential Functions*** Lead the development and maintenance of web\\-based and mobile applications that support baseball operations, scouting, player development, and analytics.\n* Architect scalable, high\\-performance software solutions, ensuring reliability and security.\n* Implement best practices for software engineering, including version control, testing, and deployment pipelines.\n* Collaborate with cross\\-functional teams to gather requirements and translate baseball operations needs into technical solutions.\n* Mentor and provide technical leadership to junior software engineers.\n* Develop and optimize APIs and database integrations to facilitate seamless data access and analysis.\n* Ensure the performance, scalability, and maintainability of software applications.\n* Stay informed about emerging technologies and trends in software development and baseball technology.\n* Work closely with the Director of Baseball Applications to align software development efforts with organizational goals.\n\n **Our Values****We Are Great Teammates*** Supports and encourages colleagues.\n* Provides and receives feedback without judgement or ego.\n* Holds one another to a high standard.\n* Provides help and encouragement proactively.\n* Assumes positive intentions from others.\n* Looks for ways to help make their teammates better.\n\n**We Are Innovators*** Embraces a growth mindset.\n* Challenges conventional wisdom.\n* Unafraid to fail.\n* Pushes boundaries and doesn't accept impossible.\n* Asks why and asks why not.\n\n**We Think Long\\-Term*** Asks: what can I do today that will pay off a year from now.\n* Eschews instant gratification for bigger benefits in the future.\n* Always trying to think three steps ahead.\n\n **Skill Requirements** * Proficiency in modern programming languages such as Python, JavaScript, TypeScript, or Java.\n* Experience with front\\-end frameworks (React, Angular, or Vue) and back\\-end frameworks (Node.js, Django, or Flask).\n* Strong knowledge of cloud platforms (AWS, Google Cloud, Azure) and DevOps best practices.\n* Experience developing and integrating APIs and working with relational and NoSQL databases.\n* Familiarity with CI\/CD pipelines, automated testing, and containerization (Docker, Kubernetes).\n* Strong problem\\-solving skills and ability to troubleshoot complex technical challenges.\n* Ability to work independently and collaboratively in a fast\\-paced environment with high demand stakeholders and fixed deadlines.\n* Excellent communication and leadership skills.\n* Passion for baseball and familiarity with advanced baseball analytics is a plus.\n\n **Education \\& Experience Guidelines** * Bachelor’s degree in Computer Science, Software Engineering, or a related field required; Master’s degree preferred.\n* Minimum of 10\\+ years of experience in software engineering, application development, or related fields.\n* Experience leading software development teams or technical projects.\n* Proven track record of building and maintaining large\\-scale high\\-availability applications in a professional environment.\n\n **Work Environment*** Ability to work evenings, weekends, and holidays as needed.\n* Availability to travel occasionally for industry conferences or organizational needs.\n* Ability to sit\/stand for extended periods and work in an office environment.\n\n We are an equal opportunity employer, and all qualified applicants will receive consideration for employment without regard to race, color, religion, national origin, sex, sexual orientation, age, disability, gender identity, marital, or veteran status, or any other protected status.   \n  \n",
		"sport_list" : "Baseball",
		"skills" : "{\"Software Engineering\",\"Software Engineering\",\"Software Engineer\",\"Software Engineer\",Javascript,TypeScript,Kubernetes,Analytics,Analytics,baseball,Angular,Python,Devops,Docker,Devops,React,Azure,NoSQL,Java,Data,AWS,Vue,IT}",
		"remote" : false,
		"remote_office" : "Office",
		"salary" : "",
		"language" : "{English}",
		"tags" : null,
		"company" : "Miami Marlins",
		"industry" : "Sports",
		"job_type" : "Permanent",
		"hours" : "{Fulltime}",
		"logo_permanent_url" : "https:\/\/cf-production.teamworkonline.com\/uploads\/public\/thumb_f9f5f76f-202f-4294-9b3c-f879aecafa3c.png",
		"job_area" : "Analytics",
		"post_duration" : 30,
		"creation_date" : "2025-05-14T13:21:50.285Z",
		"post_tier" : "Free",
		"featured" : "1 - regular",
		"airtable_id" : null,
		"slug" : "8019-lead-software-engineer"
	}
]}
</template>

<instructions>
<insert_step> is the current way I'm inserting records in my database when I scrape them.
job_data is all the data I scrape from the job listing page.
The fields in the <template> that are not in the insert step are being automatically created.

The description should be in markdown. Currently before inserting I'm doing this.
full_description = markdownify.markdownify(
                description_raw, heading_style="ATX"
            )


country must be in lower case.

skills can only be from this list:
[Tableau
ETL
Networks
NodeJS
Powerpoint
React
Email Marketing
Kafka
Engineer
Javascript
Julia
TypeScript
ELT
MLOps
Power BI
IOS
Machine Learning
Airflow
Sports Analytics
Sports Science
Angular
Excel
Statistics
CSS
NoSQL
Analytics
Software Engineering
Postgres
Sports
Manager
A/B testing
powerbi
Azure
R
Kotlin
Data Analytics
Docker
AWS
Data Engineer
Data Scientist
AI
GCP
Devops
SQL
Business Intelligence
Gaming
Spark
Data Engineering
Databricks
Rust
Google Analytics
GraphQL
Data Visualization
DBT
LLM
BigQuery
Data
Vue
Data Science
Bayesian
Salesforce
IT
Media
Software Engineer
Git
baseball
Redis
kpi
HTML
Intern
UI/UX
Python
Redshift
Linux
Kubernetes
Java
Social Media
Snowflake]

Sports can only be from this list:
[Football - Soccer
Football - NFL
NULL
Formula 1
Baseball
Tennis
Hockey
Basketball
Null
]

Senioity can only be from this list:
[With Experience
Internship
Junior]

remote_office can only be from this list:
[On-site
Global Remote
Remote
Office]

industry can only be from this list:
[Esports
Betting
Sports]

job_type can only be from this list:
[Temporary
Permanent]

hours can only be from this list:
[Part time
Fulltime]

job_area can only be from this list:
[Data Engineer
DS/ML/AI
Analytics]

My goal is to be able to insert data from other resources I come across, like a linkedin post or a pdf and quickly insert them into the database.
I think I need you to pull the info and create the record in the same way as the insert step.
And tell me then how to insert it into the database with minimal effort. It will probably be a script to connect to the db and insert. I also need the description which should be mardown formatted in json format.

Ask me to send the job description or new job info.
</instructions>

