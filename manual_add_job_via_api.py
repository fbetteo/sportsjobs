
## MANUALLY POST JOB VIA API


from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime, timezone
import json

# EDIT HTML IN INSPECT AND PASTE HERE
html_content = """<div class="desc">
    			<article>
    	        	<p><strong>Department:</strong> Football Division – Men’s First Team Scouting Team</p> <p><strong>Hours of Work:</strong> Full Time (with flexibility to work during evenings and weekends, including matchdays)</p> <p><strong>Contract Type:</strong> Permanent</p> <p><strong>Salary:</strong> Attractive Remuneration Package depending on experience</p> <p><strong>Location:</strong> Bodymoor Heath Training Ground, Home-Based and travel to matches (where required)</p> <p><strong>Closing Date:</strong> Sunday 9 February 2025</p> <p><strong>Interview Date:</strong> Week Commencing Monday 17 February 2025 and Monday 24 February 2025</p> <p><strong>1.</strong> <strong>The Department</strong></p> <p>The First Team Scouting Department provide detailed information, analysis, and recommendations to key stakeholders regarding the recruitment of prospective Men’s First Team players. Our ultimate goal is to contribute to the continued success and growth of the Men’s First Team performance whilst supporting emerging talent operations to maintain a longer-term approach to squad building and succession planning.</p> <p><strong>2.</strong> <strong>The Role</strong></p> <p>Working predominantly at Bodymoor Heath Training Ground, you will hold responsibility for the identification of elite statistical performers for both the Aston Villa First Team and Emerging Talent Departments.</p> <p>You will be responsible for implementing and executing a strategy to utilise data and driving forward the integration of data conclusively as a vital part of the scouting process to sustain a process-led and evidence-based scouting department.</p> <p>Working closely with the Football Research Department, you will assist in the profiling of specific transfer targets and continue to develop the current player performance metrics and bespoke position specific KPIs across the Club.</p> <p>Bringing the use of data to the forefront of the scouting process, you will create automated tools and reports for the scouting department in a creative and visualised manner to ensure it is consumed by stakeholders at all levels.</p> <p>For further information about the Role, please see the <strong><a href="https://api.my.corehr.com/ws/avfcp/corehr/recruitment/vacancy/jobdescription/document?key1=01B369814E0AFC84CC05D8404B750ADB9E16987E019EE16007886D5939D2396211A58C7229DD525291DCD4E3F28A39C57AA49D1ED2628ED285DA67FF30DD4CAC1C933DD1E52D5704CA158DA3350117B7F7C7F4B81ECDB42755E5B8B6AA8A2669C14C0923A59E4594E67D3A2AD892AB516D56C833D0061CF97D85DAB291C846B3BA4C13655C2AC9520A1BC0290E38DF940C8F4427234FBAD6F4CDF161B5B402A47CD33FF4920C34E118AAD60CD9E42752228C70B9AD274643EEC4814057D9639F&amp;key2=9FCAB958656AAED4C4E41C939760E5364EC837E3D3A0E91D9FEDC60061E7D829D152DF4E62D4971B92EF85480A4F56A7E4113CAA06C1F4DE17E8E071FD2D3B04E04165474E60389A8D41A24CFDB5036A2CFD9B8BB87836678708A8BAC29A6226270DC54D37FE84ECF2232A486FA5DD7FC24E9E75CD86364C179040EB68762782B9D79B3C61272C90012C275D67E84BAF3C79A29EBD285BA92C5F0F66E7F2F477DF0BEFC64CE398F45ABB8D4C9853F937449F2DF310114D31364455A5702EB52F" data-uw-rm-brl="PR" data-uw-original-href="https://api.my.corehr.com/ws/avfcp/corehr/recruitment/vacancy/jobdescription/document?key1=01B369814E0AFC84CC05D8404B750ADB9E16987E019EE16007886D5939D2396211A58C7229DD525291DCD4E3F28A39C57AA49D1ED2628ED285DA67FF30DD4CAC1C933DD1E52D5704CA158DA3350117B7F7C7F4B81ECDB42755E5B8B6AA8A2669C14C0923A59E4594E67D3A2AD892AB516D56C833D0061CF97D85DAB291C846B3BA4C13655C2AC9520A1BC0290E38DF940C8F4427234FBAD6F4CDF161B5B402A47CD33FF4920C34E118AAD60CD9E42752228C70B9AD274643EEC4814057D9639F&amp;key2=9FCAB958656AAED4C4E41C939760E5364EC837E3D3A0E91D9FEDC60061E7D829D152DF4E62D4971B92EF85480A4F56A7E4113CAA06C1F4DE17E8E071FD2D3B04E04165474E60389A8D41A24CFDB5036A2CFD9B8BB87836678708A8BAC29A6226270DC54D37FE84ECF2232A486FA5DD7FC24E9E75CD86364C179040EB68762782B9D79B3C61272C90012C275D67E84BAF3C79A29EBD285BA92C5F0F66E7F2F477DF0BEFC64CE398F45ABB8D4C9853F937449F2DF310114D31364455A5702EB52F">Role Profile</a></strong>.</p> <p><strong>3.</strong> <strong>The Person</strong></p> <p>We are seeking a pro-active, driven and experienced individual to play a crucial role in Aston Villa Football Club’s Scouting process.</p> <p>You must hold a BSc (Hons) in Computer Science, Statistics, Economics, Mathematics or an equivalent subject area (minimum 2:1) and/or have demonstrable experience of bringing data into a football club’s scouting process. Previous experience of working within a professional football club as well as proven experience of using different programming languages to interrogate data (eg. R, Python) as well as visualisation tools. (e.g Tableau) is essential.</p> <p>You will need to have clear and accurate verbal and written communication skills and be able to thrive under pressure in a fast-paced environment. You will have the ability to interpret data quickly and efficiently and to deliver findings in a concise and presentable manner to stakeholders at various levels.</p> <p>You will need a full UK Driving Licence with access to your own vehicle as the role will require you to travel (potentially internationally) as and when required. This role will require working flexibly including evenings, weekends and matchdays.</p> <p><strong>4.</strong> <strong>Why join us?</strong></p> <p>There has never been a better time to join us,&nbsp;we are celebrating our 150th anniversary, showcasing Aston Villa Football Club in all its glory to a global audience, and are determined to continue our growing success, both on and off the pitch. We currently offer a range of fantastic benefits* including:&nbsp;</p> <ul> <li>Offers on tickets for Men and Women’s matches (subject to match and ticketing arrangements) &nbsp;</li> <li>Pension scheme&nbsp;&nbsp;</li> <li>Employee Assistance Programme&nbsp;&nbsp;</li> <li>Free car parking&nbsp;</li> <li>Free staff breakfast and lunches&nbsp;</li> <li>Club Shop discount&nbsp;</li> <li>adidas discount&nbsp;</li> <li>Travel discount&nbsp;</li> <li>Death in service benefit &nbsp;</li> <li>Free Will writing&nbsp;</li> <li>Free mortgage and insurance broker consultations &nbsp;</li> <li>Free eye tests&nbsp;</li> <li>Mobile network discounts&nbsp;</li> <li>Gym discount</li> </ul> <p>*Please note these are subject to change at any time&nbsp;</p> <p><strong>As part of your application, please ensure you upload your CV.</strong></p> <p>&nbsp;</p> <p><strong>Right to Close Vacancy Posting Early</strong></p> <p><em>The Club reserves the right to close any advertised vacancies earlier than the advertised closing date if sufficient applications have been received.</em>&nbsp;</p> <p><strong>Equality Statement</strong></p> <p><em>Aston Villa Football Club celebrates the diversity of its Club and embrace equal opportunities for all.</em></p> <p><em>We welcome applications from all candidates regardless of age, race, disability, gender reassignment, pregnancy and maternity, sexual orientation, marriage and civil partnership, sex and religion or belief.</em></p> <p><strong><em>Safeguarding Statement&nbsp;</em></strong></p> <p><em>Aston Villa Football Club is fully committed to safeguarding children and adults at risk across our Club. As such, we adhere to Safer Recruitment processes and for some roles a satisfactory enhanced disclosure via the Disclosure &amp; Barring Service may be required prior to starting in a role at the Club. For more information, please see</em> Aston Villa Football Club | The official club website | AVFC - Safeguarding</p> 
    	        </article>
    		</div>"""

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
# Extract the content inside the div IF NECESSARY
# description_div = soup.find('div', {'data-automation-id': 'jobPostingDescription'})

# Convert HTML to Markdown
if soup:
    markdown_description = md(str(soup))
    print(markdown_description)
else:
    print("Description not found.")

post_body = {
    "name": "Lead Data Analyst",  # Job title or post name
    "url": "https://careers.avfc.co.uk/job/lead-data-analyst?source=linkedin.com",  # Link to the job or post
    "location": "Birmingham",  # City or region
    "country": "united kingdom",  # Country
    "seniority": "With Experience",  # Level (e.g., Junior, Mid, Senior)
    "description": markdown_description,  # Detailed description of the job or post
    "sport_list": 'Football - Soccer',  # Relevant sports categories, if any
    "skills": None,  # List of required skills (e.g., ["Python", "Data Analysis"])
    "remote_office": "Office",  # Whether it's remote, office, or hybrid
    "salary": "-",  # Salary information (e.g., "50k-70k USD per year")
    "language": ["English"],  # List of required languages (e.g., ["English", "Spanish"])
    "company": "Aston Villa FC",  # Company name
    "industry": "Sports",  # Industry type (e.g., "Sports Analytics")
    "hours": "Fulltime",  # Working hours (e.g., "Full-time", "Part-time")
    "featured": "1 - regular",  # Regular by default
    "logo_permanent_url": "https://careers.avfc.co.uk/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNkdXV3c9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--003a578b882bd1e291f4c51dbc939dad8c48503d/Aston%20Villa_1874_Crest_RGB.svg",  # Default logo
    "creation_date": str(datetime.now(timezone.utc)),  # Automatically set creation date
}



aa = json.dumps(post_body, ensure_ascii=False)

print(aa)


# PASTE THE PRINT IN https://jsonlint.com/ AND COPY THE RESULT BELOW#

# GO TO REQBIN AND POST THE JSON TO THE API